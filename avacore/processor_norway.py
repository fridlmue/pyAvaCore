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

from avacore.avabulletin import (
    AvaBulletin,
    DangerRating,
    AvalancheProblem,
    Elevation,
    Region,
    Texts,
)
from avacore.avabulletins import Bulletins


def process_reports_no(region_id) -> Bulletins:
    """
    Downloads and returns requested Avalanche Bulletins
    """

    langkey = "2"  # Needs to be set by language 1 -> Norwegian, 2 -> Englisch (parts of report)

    url = (
        "https://api01.nve.no/hydrology/forecast/avalanche/v6.0.0/api/AvalancheWarningByRegion/Detail/"
        + region_id[3:]
        + "/"
        + langkey
        + "/"
    )

    headers = {"Content-Type": "application/json; charset=utf-8"}

    req = urllib.request.Request(url, headers=headers)

    logging.info("Fetching %s", req.full_url)
    with urllib.request.urlopen(req) as response:
        content = response.read()

    varsom_report = json.loads(content)

    reports = parse_json_no(region_id, varsom_report)
    reports.append_raw_data("json", content)
    return reports


def process_all_reports_no() -> Bulletins:
    """
    Downloads and returns all norwegian avalanche reports
    """
    all_reports = Bulletins()
    for region in no_regions:
        try:
            m_reports = process_reports_no(region)
        except Exception as e:  # pylint: disable=broad-except
            logging.error("Failed to download %s", region, exc_info=e)

        for report in m_reports.bulletins:
            all_reports.append(report)

    return all_reports


def parse_json_no(
    region_id, varsom_report, fetch_time_dependant=True
) -> Bulletins:
    """
    Builds the CAAML JSONs form the norwegian JSON formats.
    """
    # pylint: disable=too-many-locals
    # pylint: disable=too-many-branches
    # pylint: disable=too-many-statements

    reports = Bulletins()
    report = AvaBulletin()

    current = 0
    now = datetime.now(pytz.timezone("Europe/Oslo"))
    if fetch_time_dependant and now.time() > time(17, 0, 0):
        current = 1

    report.regions.append(Region(region_id))
    report.publicationTime = dateutil.parser.parse(
        varsom_report[current]["PublishTime"].split(".")[0]
    )
    report.bulletinID = region_id + "_" + str(report.publicationTime)

    report.validTime.startTime = dateutil.parser.parse(
        varsom_report[current]["ValidFrom"]
    )
    report.validTime.endTime = dateutil.parser.parse(varsom_report[current]["ValidTo"])

    danger_rating = DangerRating()
    danger_rating.set_mainValue_int(int(varsom_report[current]["DangerLevel"]))

    report.dangerRatings.append(danger_rating)

    for problem in varsom_report[current]["AvalancheProblems"]:
        problem_type = ""
        if problem["AvalancheProblemTypeId"] == 7:
            problem_type = "new_snow"
        elif problem["AvalancheProblemTypeId"] == 10:
            problem_type = "wind_drifted_snow"
        elif problem["AvalancheProblemTypeId"] == 30:
            problem_type = "persistent_weak_layers"
        elif problem["AvalancheProblemTypeId"] == 45:
            problem_type = "wet_snow"
        elif problem["AvalancheProblemTypeId"] == 0:  # ???
            problem_type = "gliding_snow"
        elif problem["AvalancheProblemTypeId"] == 0:  # ???
            problem_type = "favourable_situation"

        aspects = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
        aspect_list = []

        for i, c in enumerate(problem["ValidExpositions"]):
            if c == "1":
                aspect_list.append(aspects[i])

        elev_prefix = ""
        if problem["ExposedHeightFill"] == 1:
            elev_prefix = ">"
        elif problem["ExposedHeightFill"] == 2:
            elev_prefix = "<"

        if not problem_type == "":
            elevation = Elevation()
            elevation.auto_select(elev_prefix + str(problem["ExposedHeight1"]))
            problem = AvalancheProblem()
            problem.aspects = aspect_list
            problem.elevation = elevation
            problem.problemType = problem_type
            report.avalancheProblems.append(problem)

    wxSynopsis = Texts()
    avalancheActivity = Texts()
    snowpackStructure = Texts()

    avalancheActivity.highlights = varsom_report[current]["MainText"]
    avalancheActivity.comment = varsom_report[current]["AvalancheDanger"]
    waek_layers = ""
    if varsom_report[0]["CurrentWeaklayers"] is not None:
        waek_layers = "\n" + varsom_report[0]["CurrentWeaklayers"]
    snowpackStructure.comment = varsom_report[current]["SnowSurface"] + waek_layers
    report.tendency.tendencyComment = varsom_report[current + 1]["MainText"]

    report.wxSynopsis = wxSynopsis
    report.avalancheActivity = avalancheActivity
    report.snowpackStructure = snowpackStructure

    reports.append(report)

    return reports


no_regions = [
    "NO-3003",
    "NO-3006",
    "NO-3007",
    "NO-3009",
    "NO-3010",
    "NO-3011",
    "NO-3012",
    "NO-3013",
    "NO-3014",
    "NO-3015",
    "NO-3016",
    "NO-3017",
    "NO-3018",
    "NO-3022",
    "NO-3023",
    "NO-3024",
    "NO-3027",
    "NO-3028",
    "NO-3029",
    "NO-3031",
    "NO-3032",
    "NO-3034",
    "NO-3035",
    "NO-3037",
]
