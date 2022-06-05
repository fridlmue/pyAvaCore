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
import json
import urllib.request
from datetime import datetime
from datetime import time
import logging

import pytz
import dateutil.parser

from .avajson import JSONEncoder

from avacore.avabulletin import (
    AvaBulletin,
    DangerRating,
    AvalancheProblem,
    Elevation,
    Region,
    Texts,
)


def process_reports_se(region_id, local="sv"):
    """
    Downloads and returns requested Avalanche Bulletins
    """

    langkey = "sv" # Should also work with en and smi (Samiska)

    url = (
        "http://nvgis.naturvardsverket.se/geoserver/lavinprognoser/"
        + "ows?service=WFS&version=1.0.0&request=GetFeature"
        + "&typeName=lavinprognoser:published_forecasts&outputformat=application/json"
        + f"&viewparams=lang:{langkey};location:{region_id[3:]};"
    )

    url = url + "valid_date:2021-03-01" #ToDo remove line - only debug

    headers = {"Content-Type": "application/json; charset=utf-8"}

    req = urllib.request.Request(url, headers=headers)

    logging.info("Fetching %s", req.full_url)
    with urllib.request.urlopen(req) as response:
        content = response.read()

    properties = json.loads(content)

    reports = get_reports_fromjson(region_id, properties)

    return reports


def process_all_reports_se():
    """
    Downloads and returns all norwegian avalanche reports
    """
    all_reports = []
    for region in no_regions:
        try:
            m_reports = process_reports_se(region)
        except Exception as e:  # pylint: disable=broad-except
            logging.error("Failed to download %s", region, exc_info=e)

        for report in m_reports:
            all_reports.append(report)

    return all_reports


def get_reports_fromjson(region_id, se_report, fetch_time_dependant=True):
    """
    Builds the CAAML JSONs form the norwegian JSON formats.
    """
    # pylint: disable=too-many-locals
    # pylint: disable=too-many-branches
    # pylint: disable=too-many-statements

    reports = []
    report = AvaBulletin()

    properties = se_report['features'][0]['properties']

    now = datetime.now(pytz.timezone("Europe/Stockholm"))

    report.regions.append(Region(region_id))
    report.publicationTime = dateutil.parser.parse(
        properties["published_date"]
    )
    report.bulletinID = region_id + "_" + str(report.publicationTime)

    report.validTime.startTime = dateutil.parser.parse(
        properties["valid_from"]
    )
    report.validTime.endTime = dateutil.parser.parse(properties["valid_to"])

    danger_rating = DangerRating()
    danger_rating.set_mainValue_int(int(properties["risk"]))

    report.dangerRatings.append(danger_rating)

    # up to now unly usage of 3 values found ({6: 'Wind slabs', 3: 'Persistent slabs', 11: 'Wet avalanches', 7: 'Cornices'})

    if not properties["problems"] is None:
        problems = json.loads(properties["problems"])
        print(json.dumps(problems, indent=2))
        for problem in problems:
            problem_type = problem_ids[problem["problem_type_id"]]

            aspects = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
            aspect_list = []

            for i, c in enumerate(aspects):
                if problem[aspect_keys[c]]:
                    aspect_list.append(aspects[i])

            elev = ""
            if problem["altitude_meter_above_treeline"] == True:
                elev = ">treeline"
            if problem["altitude_meter_below_treeline"] == True:
                if elev != ">treeline":
                    elev = "<treeline"
                else:
                    elev = ""

            if not problem_type == "":
                elevation = Elevation()
                elevation.auto_select(elev)
                av_problem = AvalancheProblem()
                av_problem.aspects = aspect_list
                av_problem.elevation = elevation
                av_problem.problemType = problem_type
                av_problem.terrainFeature = problem["content"]
                report.avalancheProblems.append(av_problem)

    wxSynopsis = Texts()
    avalancheActivity = Texts()
    snowpackStructure = Texts()
    travelAdvisory = Texts()

    avalancheActivity.highlights = properties["assessment_title"]
    avalancheActivity.comment = properties["assessment_content"]
    snowpackStructure.comment = properties["size_and_spread"]
    report.tendency.tendencyComment = properties["trend_label"]
    travelAdvisory.comment = properties["recommendation"]

    report.wxSynopsis = wxSynopsis
    report.avalancheActivity = avalancheActivity
    report.snowpackStructure = snowpackStructure
    report.travelAdvisory = travelAdvisory

    print(json.dumps(report, cls=JSONEncoder, indent=2))

    reports.append(report)

    return reports


no_regions = [
    "SE-01",
    "SE-02",
    "SE-03",
    "SE-04",
    "SE-05",
    "SE-06",
    "SE-07",
    "SE-08",
    "SE-09",
]

problem_ids = {
    6: 'wind_drifted_snow',
    3: 'persistent_weak_layers',
    11: 'wet_snow',
    7: 'cornice_failure'
}

aspect_keys = {
    'E': 'direction_meter_east',
    'N': 'direction_meter_north',
    'NE': 'direction_meter_north_east',
    'NW': 'direction_meter_north_west',
    'S': 'direction_meter_south',
    'SE': 'direction_meter_south_east',
    'SW': 'direction_meter_south_west',
    'W': 'direction_meter_west',
    }
