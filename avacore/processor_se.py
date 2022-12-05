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
from datetime import datetime
from .avabulletin import (
    AvaBulletin,
    DangerRating,
    AvalancheProblem,
    Elevation,
    Region,
    Texts,
)
from .avabulletins import Bulletins
from .processor import JsonProcessor


class Processor(JsonProcessor):
    def process_bulletin(self, region_id) -> Bulletins:
        langkey = "sv"  # Should also work with en and smi (Samiska)
        url = (
            "https://nvgis.naturvardsverket.se/geoserver/lavinprognoser/"
            + "ows?service=WFS&version=1.0.0&request=GetFeature"
            + "&typeName=lavinprognoser:published_forecasts&outputformat=application/json"
            + f"&viewparams=lang:{langkey};"
        )
        if region_id != "SE":
            url += f"location:{region_id[3:]};"
        headers = {"Content-Type": "application/json; charset=utf-8"}
        response_json = self._fetch_json(url, headers)
        bulletins = self.parse_json(region_id, response_json)
        return bulletins

    def parse_json(self, region_id, data) -> Bulletins:
        # pylint: disable=too-many-locals
        # pylint: disable=too-many-branches
        # pylint: disable=too-many-statements

        bulletins = Bulletins()

        for feature in data["features"]:
            properties = feature["properties"]
            report = AvaBulletin()
            report.regions.append(Region(region_id))
            report.publicationTime = datetime.fromisoformat(
                properties["published_date"]
            )
            report.bulletinID = region_id + "_" + str(report.publicationTime)

            report.validTime.startTime = datetime.fromisoformat(
                properties["valid_from"]
            )
            report.validTime.endTime = datetime.fromisoformat(properties["valid_to"])

            danger_rating = DangerRating()
            danger_rating.set_mainValue_int(int(properties["risk"]))

            report.dangerRatings.append(danger_rating)

            if properties["problems"]:
                problems = json.loads(properties["problems"])
                for problem in problems:
                    problem_type = problem_ids[problem["problem_type_id"]]

                    aspects = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
                    aspect_list = []

                    for i, c in enumerate(aspects):
                        if problem[aspect_keys[c]]:
                            aspect_list.append(aspects[i])

                    elev = ""
                    if problem["altitude_meter_above_treeline"]:
                        elev = ">treeline"
                    if problem["altitude_meter_below_treeline"]:
                        if elev != ">treeline":
                            elev = "<treeline"
                        else:
                            elev = ""

                    if problem_type:
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

            bulletins.append(report)

        return bulletins


regions = [
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
    6: "wind_slab",
    3: "persistent_weak_layers",
    11: "wet_snow",
    7: "cornice_failure",
    4: "new_snow",
}

aspect_keys = {
    "E": "direction_meter_east",
    "N": "direction_meter_north",
    "NE": "direction_meter_north_east",
    "NW": "direction_meter_north_west",
    "S": "direction_meter_south",
    "SE": "direction_meter_south_east",
    "SW": "direction_meter_south_west",
    "W": "direction_meter_west",
}
