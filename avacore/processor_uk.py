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
import re

from avacore.avabulletin import (
    AvaBulletin,
    DangerRating,
    AvalancheProblem,
    Region,
    Texts,
)
from avacore.avabulletins import Bulletins
from avacore.processor import JsonProcessor


class Processor(JsonProcessor):
    def parse_json(self, region_id, data) -> Bulletins:
        """
        Builds the CAAML JSONs form the original JSON formats.
        """

        reports = Bulletins()

        for sais_report in data:
            report = AvaBulletin()
            report.regions.append(Region("GB-SCT-" + sais_report["Region"]))
            report.bulletinID = "GB-SCT-" + sais_report["ID"]

            report.publicationTime = datetime.fromisoformat(
                sais_report["DatePublished"]
            )
            report.validTime.startTime = report.publicationTime.replace(hour=18)
            report.validTime.endTime = report.validTime.startTime + timedelta(days=1)

            avalancheActivity = Texts()
            snowpackStructure = Texts()
            avalancheActivity.highlights = sais_report["Summary"]
            avalancheActivity.comment = (
                "Forecast Snow Stability: " + sais_report["SnowStability"]
            )
            snowpackStructure.comment = (
                "Forecast Weather Influences: "
                + sais_report["WeatherInfluences"]
                + "\n"
                + "Observed Weather Influences: "
                + sais_report["ObservedWeatherInfluences"]
                + "\n"
                + "ObservedSnowStability: "
                + sais_report["ObservedSnowStability"]
            )

            report.avalancheActivity = avalancheActivity
            report.snowpackStructure = snowpackStructure

            problems = int(sais_report["KeyIcons"])

            problem = AvalancheProblem()

            if problems & (1 << 1):
                problem = AvalancheProblem()
                problem.problemType = "wind_slab"
                report.avalancheProblems.append(problem)
            if problems & (1 << 2):
                problem = AvalancheProblem()
                problem.problemType = "persistent_weak_layers"
                report.avalancheProblems.append(problem)
            if problems & (1 << 3):
                problem = AvalancheProblem()
                problem.problemType = "new_snow"
                report.avalancheProblems.append(problem)
            if problems & (1 << 4):
                problem = AvalancheProblem()
                problem.problemType = "wet_snow"
                report.avalancheProblems.append(problem)
            if problems & (1 << 5):
                problem = AvalancheProblem()
                problem.problemType = "cornice_failure"
                report.avalancheProblems.append(problem)
            if problems & (1 << 6):
                problem = AvalancheProblem()
                problem.problemType = "gliding_snow"
                report.avalancheProblems.append(problem)

            danger_ratings_raw = sais_report["CompassRose"][4:36]

            boundary_group = re.search(
                r"(?<=txtm\=)(.)*?(?=\&txte)", sais_report["CompassRose"]
            )
            boundary = boundary_group.group(
                0
            )  # No content if no different ratings for elevations

            filter_lw = [True, False, False, False] * 8
            filter_hi = [False, True, False, False] * 8

            danger_ratings_hi = list(
                d for d, s in zip(danger_ratings_raw, filter_hi) if s
            )
            danger_ratings_lw = list(
                d for d, s in zip(danger_ratings_raw, filter_lw) if s
            )

            aspects = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]

            if (
                max(danger_ratings_hi) == min(danger_ratings_hi)
                and max(danger_ratings_lw) == min(danger_ratings_lw)
                and max(danger_ratings_hi) == max(danger_ratings_lw)
            ):
                danger_rating = DangerRating()
                danger_rating.set_mainValue_int(int(max(danger_ratings_lw)))
                report.dangerRatings.append(danger_rating)
            else:
                for rating in sorted(set(danger_ratings_hi)):
                    aspect_list = []
                    for idx, aspect in enumerate(aspects):
                        if danger_ratings_hi[idx] == rating:
                            aspect_list.append(aspect)

                    danger_rating = DangerRating()
                    danger_rating.set_mainValue_int(int(rating))
                    danger_rating.elevation.lowerBound = boundary
                    danger_rating.customData = {"SAIS": {"aspects": aspect_list}}
                    # danger_rating.aspect = aspect_list
                    report.dangerRatings.append(danger_rating)

                for rating in sorted(set(danger_ratings_lw)):
                    aspect_list = []
                    for idx, aspect in enumerate(aspects):
                        if danger_ratings_lw[idx] == rating:
                            aspect_list.append(aspect)

                    danger_rating = DangerRating()
                    danger_rating.set_mainValue_int(int(rating))
                    danger_rating.elevation.upperBound = boundary
                    danger_rating.customData = {"SAIS": {"aspects": aspect_list}}
                    # danger_rating.aspect = aspect_list
                    report.dangerRatings.append(danger_rating)

            reports.append(report)

        return reports

    def process_bulletin(self, region_id) -> Bulletins:
        """
        Downloads and returns requested Avalanche Bulletins
        """

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/50.0.2661.102 Safari/537.36"
        }
        sais_reports = self._fetch_json(self.url, headers)

        return self.parse_json(region_id, sais_reports)
