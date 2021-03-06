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
import re
import xml.etree.ElementTree as ET
from urllib.request import urlopen, Request

import dateutil.parser
import pytz

from avacore.avabulletin import (
    AvaBulletin,
    DangerRating,
    AvalancheProblem,
    Region,
    Texts,
    Elevation,
)


def download_report_is(lang):
    """
    Download reports
    """
    req = Request(
        "https://xmlweather.vedur.is/avalanche?op=xml&type=status&lang=" + lang
    )  # lang can only be `is` or `en`
    logging.info("Fetching %s", req.full_url)

    with urlopen(req) as response_content:
        try:
            root = ET.fromstring(response_content.read().decode("utf-8"))
        except Exception as r_e:  # pylint: disable=broad-except
            print("error parsing ElementTree: " + str(r_e))
    return root


def process_reports_is(path="", cached=False, lang="en"):
    # pylint: disable=too-many-locals
    """
    Processes downloaded report
    """
    if not cached:
        root = download_report_is(lang)
    else:
        root = ET.parse(path)

    common_report = AvaBulletin()

    conditions = root.find("conditions")
    common_report.travelAdvisory = Texts(
        highlights=conditions.find("short_description").text,
        comment=re.sub(r"(\<.*?\>)", "", conditions.find("full_description").text),
    )
    common_report.publicationTime = pytz.timezone("Iceland").localize(
        dateutil.parser.parse(conditions.find("update_time").text)
    )

    weather_forecast = root.find("weather_forecast")
    common_report.wxSynopsis = Texts(comment=weather_forecast.find("forecast").text)

    reports = []

    area_forecasts = root.find("area_forecasts")
    for area_forcast in area_forecasts.iter(tag="area_forecast"):
        wxSynopsis = Texts()
        avalancheActivity = Texts()
        snowpackStructure = Texts()
        report = copy.deepcopy(common_report)
        report.publicationTime = pytz.timezone("Iceland").localize(
            dateutil.parser.parse(area_forcast.find("updated").text)
        )
        report.validTime.startTime = pytz.timezone("Iceland").localize(
            dateutil.parser.parse(area_forcast.find("valid_from").text)
        )
        report.validTime.endTime = pytz.timezone("Iceland").localize(
            dateutil.parser.parse(area_forcast.find("valid_until").text)
        )
        report.regions.append(
            Region("IS-" + area_forcast.find("region_code").text.upper())
        )

        report.bulletinID = (
            report.regions[0].regionId + "-" + report.publicationTime.isoformat()
        )

        avalancheActivity.highlights = area_forcast.find("forecast").text
        avalancheActivity.comment = area_forcast.find("recent_avalances").text
        snowpackStructure.highlights = area_forcast.find("snow_condition").text
        wxSynopsis.highlights = area_forcast.find("weather").text

        danger_rating = DangerRating()
        danger_rating.set_mainValue_int(
            int(area_forcast.find("danger_level_day1_code").text)
        )
        report.dangerRatings.append(danger_rating)

        report.wxSynopsis = wxSynopsis
        report.avalancheActivity = avalancheActivity
        report.snowpackStructure = snowpackStructure

        for snow_problem in area_forcast.iter(tag="snow_problem"):
            # problem_danger_rating = DangerRating()

            aspects_list = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"] * 2
            index_from = "0"
            index_to = "0"
            index_from = aspects_list.index(snow_problem.find("aspect_from").text)
            index_to = aspects_list.index(
                snow_problem.find("aspect_to").text, index_from
            )
            # problem_danger_rating.aspect = aspects_list[index_from:index_to+1]
            elevation = Elevation()

            if snow_problem.find("height").text != "0":
                up_down = ">"
                if "Above" in snow_problem.find("height").text:
                    up_down = "<"
                elevation.auto_select(up_down + snow_problem.find("height").text)

            problem = AvalancheProblem()
            problem.add_problemType(snow_problem.find("type").text.lower())
            problem.aspects = aspects_list[index_from : index_to + 1]
            problem.elevation = elevation
            # problem.dangerRating = problem_danger_rating
            report.avalancheProblems.append(problem)

        reports.append(report)

    return reports
