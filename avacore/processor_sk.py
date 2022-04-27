"""
    Copyright (C) 2022 Friedrich Mütschele and other contributors
    This file is part of pyAvaCore.
    pyAvaCore is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    pyAvaCore is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with pyAvaCore. If not, see <http://www.gnu.org/licenses/>.
"""
import logging
import copy
import json
from urllib.request import urlopen, Request

from avacore.avabulletin import (
    AvaBulletin,
    DangerRating,
    Region,
    Provider,
    Source,
    Tendency,
    Texts,
    ValidTime,
)


def process_reports_sk():
    """
    Download reports
    """
    req = Request("https://caaml.hzs.sk/")
    with urlopen(req) as response_content:
        response = response_content.read().decode("utf-8").split("</textarea>")[1]
        response_json = json.loads(response)

    return get_reports_fromjson(response_json[0])


def get_reports_fromjson(sk_report):
    # pylint: disable=too-many-locals
    """
    Processes downloaded report
    """

    common_bulletin = AvaBulletin()

    common_bulletin.source = Source(
        provider=Provider(name=sk_report["author"], website=str("https://www.hzs.sk"),)
    )
    common_bulletin.validTime = ValidTime(
        startTime=sk_report["validFrom"], endTime=sk_report["validTill"]
    )
    common_bulletin.publicationTime = sk_report["published"]

    common_bulletin.bulletinID = "SK" + sk_report["published"]

    avalancheActivity = Texts()
    snowpackStructure = Texts()

    avalancheActivity.highlights = sk_report["headline"]

    for description in sk_report["descriptions"]:
        if "Lavínová situácia" in description["heading"]:
            avalancheActivity.comment = description["text"]
        elif "Snehová pokrývka" in description["heading"]:
            snowpackStructure.comment = description["text"]
        elif "Krátkodobý vývoj" in description["heading"]:
            common_bulletin.tendency = Tendency(tendencyComment=description["text"])

    common_bulletin.avalancheActivity = avalancheActivity
    common_bulletin.snowpackStructure = snowpackStructure

    bulletins = []

    for region_id, region in sk_report["regions"].items():
        bulletin = AvaBulletin()
        bulletin = copy.deepcopy(common_bulletin)
        bulletin.regions.append(Region(region_id.replace("SK0R", "SK-0")))

        keys = ["am"]
        if "pm" in region:
            keys.append("pm")
        valid_time = {"am": "earlier", "pm": "later"}

        for key in keys:
            elevations = ["lower"]
            if len(region[key][f"{elevations[0]}Text"]) > 4:
                elevations.append("upper")
            for elevation in elevations:
                danger_rating = DangerRating()
                main_val = (
                    int(region[key][f"{elevation}Level"])
                    if region[key][f"{elevation}Level"].isdigit()
                    else 0
                )
                danger_rating.set_mainValue_int(main_val)
                if len(elevations) > 1:
                    height = region[key][f"{elevation}Text"]
                    height = height.replace("nad ", ">")
                    height = height.replace("pod ", "<")
                    danger_rating.elevation.auto_select(height)
                if len(keys) > 1:
                    danger_rating.validTimePeriod = valid_time[key]
                else:
                    danger_rating.validTimePeriod = "all_day"
                bulletin.dangerRatings.append(danger_rating)

        bulletins.append(bulletin)

    return bulletins
