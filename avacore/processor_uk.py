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
    Elevation,
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

            problems = sais_report["avalancheProblems"]
            for problem in problems:
                prob = AvalancheProblem()
                prob.problemType = problem["problemType"]
                prob.elevation = Elevation(
                    lowerBound=problem["elevation"],
                    upperBound=None,
                )
                prob.aspects = problem["aspects"]
                report.avalancheProblems.append(prob)

            # danger rating values for enum
            drVal = [
                "n/a",
                "low",
                "moderate",
                "considerable",
                "high",
                "very_high",
                "no_snow",
                "no_rating",
            ]
            # get data for all values on compass rose
            cpData = sais_report["CompassRose"][4:36]

            # get lower bounds and upper bounds
            cpBoundsRE = re.search(
                r"txts=(?P<txts>[0-9]*)&txtm=(?P<txtm>[0-9]*)&txte=(?P<txte>[0-9]*)",
                sais_report["CompassRose"],
            )
            cpBounds = []

            if not cpBoundsRE.group("txtm"):
                # if there is no medium text value then there is only one bound and we will only look at outer layer data
                cpBounds.append(
                    {  # just Outer layer
                        "lowerBound": round(int(cpBoundsRE.group("txts")), ndigits=-2),
                        "upperBound": round(int(cpBoundsRE.group("txte")), ndigits=-2),
                    }
                )
            else:
                # two bounds exist outer layer and inner layer
                cpBounds.append(
                    {  # Outer layer
                        "lowerBound": round(int(cpBoundsRE.group("txts")), ndigits=-2),
                        "upperBound": round(int(cpBoundsRE.group("txtm")), ndigits=-2),
                    }
                )
                cpBounds.append(
                    {  # Inner layer
                        "lowerBound": round(int(cpBoundsRE.group("txtm")), ndigits=-2),
                        "upperBound": round(int(cpBoundsRE.group("txte")), ndigits=-2),
                    }
                )

            # Outer layer data
            groupDanger = {
                "low": [],
                "moderate": [],
                "considerable": [],
                "high": [],
                "very_high": [],
            }
            if (v := int(cpData[0])) != 0:  # North Outer layer
                groupDanger[drVal[v]].append("N")
            if (v := int(cpData[4])) != 0:  # North East Outer layer
                groupDanger[drVal[v]].append("NE")
            if (v := int(cpData[8])) != 0:  # East Outer layer
                groupDanger[drVal[v]].append("E")
            if (v := int(cpData[12])) != 0:  # South East Outer layer
                groupDanger[drVal[v]].append("SE")
            if (v := int(cpData[16])) != 0:  # South Outer layer
                groupDanger[drVal[v]].append("S")
            if (v := int(cpData[20])) != 0:  # South West Outer layer
                groupDanger[drVal[v]].append("SW")
            if (v := int(cpData[24])) != 0:  # West Outer layer
                groupDanger[drVal[v]].append("W")
            if (v := int(cpData[28])) != 0:  # North West Outer layer
                groupDanger[drVal[v]].append("NW")

            for group, aspects in groupDanger.items():
                if aspects:
                    # there are identified dangers so create the dangerRating
                    drMain = DangerRating()
                    drMain.validTimePeriod = "all_day"
                    drMain.mainValue = group
                    drMain.elevation = Elevation.from_dict(cpBounds[0])
                    drMain.aspects = aspects
                    report.dangerRatings.append(drMain)

            if len(cpBounds) > 1:
                # add inner layer in case there are more bounds
                # Inner layer data
                groupDanger = {
                    "low": [],
                    "moderate": [],
                    "considerable": [],
                    "high": [],
                    "very_high": [],
                }
                if (v := int(cpData[1])) != 0:  # North Inner layer
                    groupDanger[drVal[v]].append("N")
                if (v := int(cpData[5])) != 0:  # North East Inner layer
                    groupDanger[drVal[v]].append("NE")
                if (v := int(cpData[9])) != 0:  # East Inner layer
                    groupDanger[drVal[v]].append("E")
                if (v := int(cpData[13])) != 0:  # South East Inner layer
                    groupDanger[drVal[v]].append("SE")
                if (v := int(cpData[17])) != 0:  # South Inner layer
                    groupDanger[drVal[v]].append("S")
                if (v := int(cpData[21])) != 0:  # South West Inner layer
                    groupDanger[drVal[v]].append("SW")
                if (v := int(cpData[25])) != 0:  # West Inner layer
                    groupDanger[drVal[v]].append("W")
                if (v := int(cpData[29])) != 0:  # North West Inner layer
                    groupDanger[drVal[v]].append("NW")

                for group, aspects in groupDanger.items():
                    if aspects:
                        # there are identified dangers so create the dangerRating
                        drMain = DangerRating()
                        drMain.validTimePeriod = "all_day"
                        drMain.mainValue = group
                        drMain.elevation = Elevation.from_dict(cpBounds[1])
                        drMain.aspects = aspects
                        report.dangerRatings.append(drMain)

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
