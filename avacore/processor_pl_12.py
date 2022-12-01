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
import re
import json


from avacore.avabulletin import (
    AvaBulletin,
    ValidTime,
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

        url = f"https://lawiny.topr.pl/"
        response: str = self._fetch_url(url, {})

        raw = re.compile(r"const oLawReport = (?P<raw_json>[^*]+?);\n").search(response).group(1)

        pl_12_report = json.loads(raw)

        self.raw_data = raw
        self.raw_data_format = "JSON"

        return self.parse_json(region_id, pl_12_report)

    def parse_json(self, region_id, data) -> Bulletins:

        bulletins = Bulletins()
        bulletin = AvaBulletin()

        # ZoneInfo("Europe/Warsaw")

        bulletin.regions = [Region(regionID=region_id)]
        bulletin.validTime  = ValidTime(
            data["iat"],
            data["exp"]
            )

        bulletin.publicationTime = bulletin.validTime.startTime

        bulletin.bulletinID = f"{region_id}_{data['exp']}"

        avalancheActivity = Texts()
        avalancheActivity.comment = data["comment"]

        bulletin.avalancheActivity = avalancheActivity

        snowpackStructure = Texts()
        snowpackStructure.comment = data['mst']['desc1']

        bulletin.snowpackStructure = snowpackStructure

        travelAdvisory = Texts()
        travelAdvisory.comment = data['mst']['desc2']

        bulletin.travelAdvisory = travelAdvisory

        ratings = {
            "am": "earlier", 
            "pm": "later"
            }

        aspects = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]

        for rating in ratings:
            elevs = ["upper"]
            if data[rating]["mode"] == 2:
                elevs.append("lower")
            for elev in elevs:
                danger_rating = DangerRating(
                    validTimePeriod=ratings[rating]
                )
                danger_rating.set_mainValue_int(int(data[rating][elev]["lev"]))
                if len(elev) > 1:
                    elevation = Elevation()
                    if elev == "upper":
                        elevation.lowerBound = str(data[rating]["height"])
                    else:
                        elevation.upperBound = str(data[rating]["height"])
                    danger_rating.elevation = elevation

                aspect_list = []

                for i, c in enumerate(data[rating][elev]["exp"]):
                    if c == "1":
                        aspect_list.append(aspects[i])

                problem_type = ""
                if data[rating][elev]["prb"] == 'prwd':
                    problem_type = "wind_slab"
                if data[rating][elev]["prb"] == 'prws':
                    problem_type = "wet_snow"
                if data[rating][elev]["prb"] == 'brak':
                    problem_type = ""
                '''
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
                '''

                bulletin.dangerRatings.append(danger_rating)

                if not problem_type == "":
                    problem = AvalancheProblem()
                    problem.aspects = aspect_list
                    if len(elev) > 1:
                        problem.elevation = elevation
                    problem.problemType = problem_type
                    bulletin.avalancheProblems.append(problem)

        bulletins.append(bulletin)

        return bulletins