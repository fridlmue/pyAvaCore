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
        response: str = self._fetch_url(self.url, {})

        raw = (
            re.compile(r"const oLawReport = (?P<raw_json>[^*]+?);\n")
            .search(response)
            .group(1)
        )

        pl_12_report = json.loads(raw)

        self.raw_data = raw
        self.raw_data_format = "JSON"

        return self.parse_json(region_id, pl_12_report)

    def parse_json(self, region_id, data) -> Bulletins:
        bulletins = Bulletins()
        bulletin = AvaBulletin()

        # ZoneInfo("Europe/Warsaw")

        bulletin.regions = [Region(regionID=region_id)]
        bulletin.validTime = ValidTime(data["iat"], data["exp"])

        bulletin.publicationTime = bulletin.validTime.startTime

        bulletin.bulletinID = f"{region_id}_{data['exp']}"

        avalancheActivity = Texts()
        avalancheActivity.comment = data["comment"]

        bulletin.avalancheActivity = avalancheActivity

        snowpackStructure = Texts()
        snowpackStructure.comment = data["mst"]["desc1"]

        bulletin.snowpackStructure = snowpackStructure

        travelAdvisory = Texts()
        travelAdvisory.comment = data["mst"]["desc2"]

        bulletin.travelAdvisory = travelAdvisory

        ratings = {"am": "earlier", "pm": "later"}
        for rating in ratings:
            del data[rating]["img"]
        if data["am"] == data["pm"]:
            ratings = {"am": "all_day"}

        aspects = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]

        for rating, rating_ident in ratings.items():
            elevs = ["upper"]
            if data[rating]["mode"] == 2:
                elevs.append("lower")
            for elev in elevs:
                danger_rating = DangerRating(validTimePeriod=rating_ident)
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

                bulletin.dangerRatings.append(danger_rating)

                if data[rating][elev]["prb"]:
                    problem = AvalancheProblem()
                    problem.aspects = aspect_list
                    if len(elev) > 1:
                        problem.elevation = elevation
                    if data[rating][elev]["prb"] == "prgs":
                        problem.problemType = "gliding_snow"
                    if data[rating][elev]["prb"] == "prnn":
                        problem.problemType = "no_distinct_avalanche_problem"
                    if data[rating][elev]["prb"] == "prns":
                        problem.problemType = "new_snow"
                    if data[rating][elev]["prb"] == "prwd":
                        problem.problemType = "wind_slab"
                    if data[rating][elev]["prb"] == "prwl":
                        problem.problemType = "persistent_weak_layers"
                    if data[rating][elev]["prb"] == "prws":
                        problem.problemType = "wet_snow"
                    if problem.problemType:
                        bulletin.avalancheProblems.append(problem)

        bulletins.append(bulletin)

        return bulletins
