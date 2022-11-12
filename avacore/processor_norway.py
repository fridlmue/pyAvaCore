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
from datetime import datetime
from datetime import time
import logging
from zoneinfo import ZoneInfo


from avacore.avabulletin import (
    AvaBulletin,
    DangerRating,
    AvalancheProblem,
    Elevation,
    Region,
    Texts,
)
from avacore.avabulletins import Bulletins
from avacore.processor import JsonProcessor


class Processor(JsonProcessor):

    fetch_time_dependant = True

    def process_bulletin(self, region_id) -> Bulletins:
        if region_id == "NO":
            return self.process_all_reports_no()

        langkey = "2"  # Needs to be set by language 1 -> Norwegian, 2 -> Englisch (parts of report)
        url = (
            "https://api01.nve.no/hydrology/forecast/avalanche/v6.0.0/api/AvalancheWarningByRegion/Detail/"
            + region_id[3:]
            + "/"
            + langkey
            + "/"
        )
        headers = {"Content-Type": "application/json; charset=utf-8"}
        varsom_report = self._fetch_json(url, headers=headers)
        return self.parse_json(region_id, varsom_report)

    def process_all_reports_no(self) -> Bulletins:
        """
        Downloads and returns all norwegian avalanche reports
        """
        all_reports = Bulletins()
        for region in no_regions:
            try:
                m_reports = self.process_bulletin(region)
            except Exception as e:  # pylint: disable=broad-except
                logging.error("Failed to download %s", region, exc_info=e)

            for report in m_reports.bulletins:
                all_reports.append(report)

        return all_reports

    def parse_json(self, region_id, data) -> Bulletins:
        """
        Builds the CAAML JSONs form the norwegian JSON formats.
        """
        # pylint: disable=too-many-locals
        # pylint: disable=too-many-branches
        # pylint: disable=too-many-statements

        reports = Bulletins()
        report = AvaBulletin()

        current = 0
        now = datetime.now(ZoneInfo("Europe/Oslo"))
        if self.fetch_time_dependant and now.time() > time(17, 0, 0):
            current = 1

        report.regions.append(Region(region_id))
        report.publicationTime = datetime.fromisoformat(
            data[current]["PublishTime"].split(".")[0]
        )
        report.bulletinID = region_id + "_" + str(report.publicationTime)

        report.validTime.startTime = datetime.fromisoformat(data[current]["ValidFrom"])
        report.validTime.endTime = datetime.fromisoformat(data[current]["ValidTo"])

        danger_rating = DangerRating()
        danger_rating.set_mainValue_int(int(data[current]["DangerLevel"]))

        report.dangerRatings.append(danger_rating)

        if data[current]["AvalancheProblems"] is not None:
            for problem in data[current]["AvalancheProblems"]:
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

        avalancheActivity.highlights = data[current]["MainText"]
        avalancheActivity.comment = data[current]["AvalancheDanger"]
        waek_layers = ""
        if data[0]["CurrentWeaklayers"] is not None:
            waek_layers = "\n" + data[0]["CurrentWeaklayers"]
        if data[current]["SnowSurface"] is not None:
            snowpackStructure.comment = data[current]["SnowSurface"] + waek_layers
        report.tendency.tendencyComment = data[current + 1]["MainText"]

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
