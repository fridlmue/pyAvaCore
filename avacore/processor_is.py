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
import copy
import re
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo

from avacore.avabulletin import (
    AvaBulletin,
    DangerRating,
    AvalancheProblem,
    Region,
    Texts,
    Elevation,
)
from avacore.avabulletins import Bulletins
from avacore.processor import XmlProcessor


class Processor(XmlProcessor):
    def parse_xml(self, region_id, root: ET.ElementTree) -> Bulletins:

        # pylint: disable=too-many-locals
        """
        Processes downloaded report
        """
        common_report = AvaBulletin()
        tzinfo = ZoneInfo("Iceland")

        conditions = root.find("conditions")
        common_report.travelAdvisory = Texts(
            highlights=conditions.find("short_description").text,
            comment=re.sub(r"(\<.*?\>)", "", conditions.find("full_description").text),
        )
        common_report.publicationTime = datetime.fromisoformat(
            conditions.find("update_time").text
        ).replace(tzinfo=tzinfo)

        weather_forecast = root.find("weather_forecast")
        common_report.wxSynopsis = Texts(comment=weather_forecast.find("forecast").text)

        reports = Bulletins()

        area_forecasts = root.find("area_forecasts")
        for area_forcast in area_forecasts.iter(tag="area_forecast"):
            wxSynopsis = Texts()
            avalancheActivity = Texts()
            snowpackStructure = Texts()
            report = copy.deepcopy(common_report)
            report.publicationTime = datetime.fromisoformat(
                area_forcast.find("updated").text
            ).replace(tzinfo=tzinfo)
            report.validTime.startTime = datetime.fromisoformat(
                area_forcast.find("valid_from").text
            ).replace(tzinfo=tzinfo)
            report.validTime.endTime = datetime.fromisoformat(
                area_forcast.find("valid_until").text
            ).replace(tzinfo=tzinfo)
            report.regions.append(
                Region("IS-" + area_forcast.find("region_code").text.upper())
            )

            report.bulletinID = (
                report.regions[0].regionID + "-" + report.publicationTime.isoformat()
            )

            avalancheActivity.highlights = area_forcast.find("forecast").text
            avalancheActivity.comment = area_forcast.find("recent_avalances").text
            snowpackStructure.highlights = area_forcast.find("snow_condition").text
            wxSynopsis.highlights = area_forcast.find("weather").text

            danger_rating = DangerRating()
            danger_rating.set_mainValue_int(
                int(area_forcast.find("danger_level_day1_code").text)
            )
            report.dangerRatings.append(danger_rating)

            report.wxSynopsis = wxSynopsis
            report.avalancheActivity = avalancheActivity
            report.snowpackStructure = snowpackStructure

            for snow_problem in area_forcast.iter(tag="snow_problem"):
                # problem_danger_rating = DangerRating()

                aspects_list = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"] * 2
                index_from = "0"
                index_to = "0"
                index_from = aspects_list.index(snow_problem.find("aspect_from").text)
                index_to = aspects_list.index(
                    snow_problem.find("aspect_to").text, index_from
                )
                # problem_danger_rating.aspect = aspects_list[index_from:index_to+1]
                elevation = Elevation()

                if snow_problem.find("height").text != "0":
                    up_down = ">"
                    if "Above" in snow_problem.find("height").text:
                        up_down = "<"
                    elevation.auto_select(up_down + snow_problem.find("height").text)

                problem = AvalancheProblem()
                problem.add_problemType(snow_problem.find("type").text.lower())
                problem.aspects = aspects_list[index_from : index_to + 1]
                problem.elevation = elevation
                # problem.dangerRating = problem_danger_rating
                report.avalancheProblems.append(problem)

            reports.append(report)

        return reports
