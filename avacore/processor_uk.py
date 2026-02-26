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

            """ 
                build danger ratings

                "dangerRatings":[
                    "dangerRating" : {
                        "validTimePeriod": "all_day",
                        "mainValue": [ "low", "moderate", "considerable", "high", "very_high", "no_snow", "no_rating" ],
                        "elevation": {
                            "lowerBound": "integer in meters",
                            "upperBound": "integer in meters"
                        },
                        "aspects": array : [ "N", "NE", "E", "SE", "S", "SW", "W", "NW", "n/a" ],
                    }
                ]
            """

            # danger rating values for enum
            drVal = ["n/a", "low", "moderate", "considerable", "high", "very_high", "no_snow", "no_rating"]
            # get data for all values on compass rose
            cpData = sais_report["CompassRose"][4:36]

            # get lower bounds and upper bounds
            cpBoundsRE = re.search("txts\\=([0-9]*)&txtm\\=([0-9]*)&txte\\=([0-9]*)", sais_report["CompassRose"])
            cpBounds = []

            if cpBoundsRE.groups()[1] == "":
                # if there is no medium text value then there is only one bound and we will only look at outer layer data
                cpBounds.append({       # just Outer layer
                    "lowerBound": str(cpBoundsRE.groups()[0]),
                    "upperBound": str(cpBoundsRE.groups()[2])
                })
            else:
                # two bounds exist outer layer and inner layer
                cpBounds.append({       # Outer layer
                    "lowerBound": str(cpBoundsRE.groups()[0]),
                    "upperBound": str(cpBoundsRE.groups()[1])
                })
                cpBounds.append({       # Inner layer
                    "lowerBound": str(cpBoundsRE.groups()[1]),
                    "upperBound": str(cpBoundsRE.groups()[2])
                })

            #Outer layer data
            groupDanger = {"low" : [], "moderate": [], "considerable": [], "high": [], "very_high": []}
            if cpData[0]!=0:        # North Outer layer
                groupDanger[drVal[int(cpData[0])]].append("N")
            if cpData[4]!=0:        # North East Outer layer
                groupDanger[drVal[int(cpData[4])]].append("NE")
            if cpData[8]!=0:        # East Outer layer
                groupDanger[drVal[int(cpData[8])]].append("E")
            if cpData[12]!=0:        # South East Outer layer
                groupDanger[drVal[int(cpData[12])]].append("SE")
            if cpData[16]!=0:        # South Outer layer
                groupDanger[drVal[int(cpData[16])]].append("S")
            if cpData[20]!=0:        # South West Outer layer
                groupDanger[drVal[int(cpData[20])]].append("SW")
            if cpData[24]!=0:        # West Outer layer
                groupDanger[drVal[int(cpData[24])]].append("W")
            if cpData[28]!=0:        # North West Outer layer
                groupDanger[drVal[int(cpData[28])]].append("NW")

            for group in groupDanger:
                if len(groupDanger[group])>0:
                    # there are identified dangers so create the dangerRating
                    drMain = DangerRating()
                    drMain.validTimePeriod = "all_day"
                    drMain.mainValue = group
                    drMain.elevation = Elevation(
                        lowerBound = cpBounds[0]["lowerBound"],
                        upperBound = cpBounds[0]["upperBound"],
                    )
                    drMain.aspects = groupDanger[group]
                    report.dangerRatings.append(drMain)
            
            if len(cpBounds)>1:
                # add inner layer in case there are more bounds
                # Inner layer data
                groupDanger = {"low" : [], "moderate": [], "considerable": [], "high": [], "very_high": []}
                if cpData[1]!=0:        # North Inner layer
                    groupDanger[drVal[int(cpData[1])]].append("N")
                if cpData[5]!=0:        # North East Inner layer
                    groupDanger[drVal[int(cpData[5])]].append("NE")
                if cpData[9]!=0:        # East Inner layer
                    groupDanger[drVal[int(cpData[9])]].append("E")
                if cpData[13]!=0:        # South East Inner layer
                    groupDanger[drVal[int(cpData[13])]].append("SE")
                if cpData[17]!=0:        # South Inner layer
                    groupDanger[drVal[int(cpData[17])]].append("S")
                if cpData[21]!=0:        # South West Inner layer
                    groupDanger[drVal[int(cpData[21])]].append("SW")
                if cpData[25]!=0:        # West Inner layer
                    groupDanger[drVal[int(cpData[25])]].append("W")
                if cpData[29]!=0:        # North West Inner layer
                    groupDanger[drVal[int(cpData[29])]].append("NW")

                for group in groupDanger:
                    if len(groupDanger[group])>0:
                        # there are identified dangers so create the dangerRating
                        drMain = DangerRating()
                        drMain.validTimePeriod = "all_day"
                        drMain.mainValue = group
                        drMain.elevation = Elevation(
                            lowerBound = cpBounds[1]["lowerBound"],
                            upperBound = cpBounds[1]["upperBound"],
                        )
                        drMain.aspects = groupDanger[group]
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
