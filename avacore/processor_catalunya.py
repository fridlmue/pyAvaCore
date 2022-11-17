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
from zoneinfo import ZoneInfo

from avacore.avabulletin import (
    AvaBulletin,
    DangerRating,
    AvalancheProblem,
    Region,
    Texts,
)
from avacore.avabulletins import Bulletins
from avacore.processor import JsonProcessor


code_dir = {
    "1": "ES-CT-L-04",
    "2": "ES-CT-RF",
    "3": "ES-CT-PA",
    "4": "ES-CT-PP",
    "5": "ES-CT-VN",
    "6": "ES-CT-PR",
    "7": "ES-CT-TF",
}


class Processor(JsonProcessor):
    today = datetime.today().date()

    def process_bulletin(self, region_id) -> Bulletins:
        lang_dir = {"en": 3, "ca": 1, "es": 2}
        lang = lang_dir.get(self.local, 2)
        url = (
            "https://bpa.icgc.cat/api/apiext/butlletiglobal?values="
            + str(self.today)
            + ";"
            + str(lang_dir[lang])
        )
        headers = {"Content-Type": "application/json; charset=utf-8"}
        icgc_reports = self._fetch_json(url, headers)
        reports = self.parse_json(region_id, icgc_reports)
        return reports

    def parse_json(self, region_id, data) -> Bulletins:
        """
        Builds the CAAML JSONs form the ICGC JSON formats.
        """
        reports = Bulletins()
        report = AvaBulletin()

        for icgc_report in data:
            region_id = code_dir[icgc_report["id_zona"]]

            report = AvaBulletin()
            tzinfo = ZoneInfo("Europe/Madrid")

            report.publicationTime = datetime.fromisoformat(
                icgc_report["databutlleti"]
            ).replace(tzinfo=tzinfo)
            report.bulletinID = region_id + "_" + str(report.publicationTime)
            report.regions.append(Region(region_id))
            report.validTime.startTime = datetime.fromisoformat(
                icgc_report["datavalidesabutlleti"] + "T00:00"
            ).replace(tzinfo=tzinfo)
            report.validTime.endTime = datetime.fromisoformat(
                icgc_report["datavalidesabutlleti"] + "T23:59"
            ).replace(tzinfo=tzinfo)

            report.avalancheActivity = Texts(
                highlights=icgc_report["perill_text"],
                comment=icgc_report["text_estat_mantell"],
            )
            report.snowpackStructure = Texts(comment=icgc_report["text_distribucio"])
            report.tendency.tendencyComment = icgc_report["text_tendencia"]

            danger_rating = DangerRating()
            danger_rating.set_mainValue_int(int(icgc_report["grau_perill_primari"]))
            report.dangerRatings.append(danger_rating)
            if not icgc_report["grau_perill_secundari"] is None:
                danger_rating_2 = DangerRating()
                danger_rating_2.set_mainValue_int(
                    int(icgc_report["grau_perill_secundari"])
                )
                report.dangerRatings.append(danger_rating_2)

            for problem in icgc_report["problems"]:
                problem_type = ""
                if problem["id_tipus_situacio"] == "1":
                    problem_type = "new snow"
                elif problem["id_tipus_situacio"] == "2":
                    problem_type = "drifting snow"
                elif problem["id_tipus_situacio"] == "3":
                    problem_type = "old snow"
                elif problem["id_tipus_situacio"] == "4":
                    problem_type = "wet snow"
                elif problem["id_tipus_situacio"] == "5":
                    problem_type = "gliding snow"
                elif problem["id_tipus_situacio"] == "6":
                    problem_type = "favourable situation"

                problem = AvalancheProblem()
                problem.add_problemType(problem_type)
                report.avalancheProblems.append(problem)

            reports.append(report)

        return reports
