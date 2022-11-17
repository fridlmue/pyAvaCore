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
from datetime import datetime, timedelta
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
    def process_bulletin(self, region_id) -> Bulletins:
        url = "https://www.horskasluzba.cz/cz/avalanche-json"
        headers = {"Content-Type": "application/json; charset=utf-8"}
        horskasluzba_report = self._fetch_json(url, headers)
        reports = self.parse_json(region_id, horskasluzba_report)
        return reports

    def parse_json(self, region_id, data) -> Bulletins:
        reports = Bulletins()

        for bulletin in data:
            report = AvaBulletin()
            report.regions.append(Region("CZ-" + bulletin["region_id"]))
            report.publicationTime = datetime.fromisoformat(
                bulletin["date_time"]
            ).replace(tzinfo=ZoneInfo("Europe/Prague"))
            report.bulletinID = bulletin["id"]

            report.validTime.startTime = report.publicationTime
            report.validTime.endTime = report.publicationTime + timedelta(hours=24)

            danger_rating = DangerRating()
            danger_rating.set_mainValue_int(int(bulletin["warning_level"]))

            report.dangerRatings.append(danger_rating)

            for warning in bulletin["warnings"]:
                aspect_list = []
                if warning["exposition"] != "NONE":
                    for exposition in warning["exposition"].replace(" ", "").split(","):
                        aspect_list.append(exposition)

                problem = AvalancheProblem()
                if "ALL" not in aspect_list:
                    problem.aspects = aspect_list
                problem.elevation = Elevation(
                    lowerBound=warning["altitude_from"] or None,
                    upperBound=warning["altitude_to"] or None,
                )
                problem.add_problemType(warning["type"])
                report.avalancheProblems.append(problem)

            report.avalancheActivity = Texts(comment=bulletin["description"])

            reports.append(report)

        return reports
