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
from typing import List, TypedDict
from avacore.avabulletin import (
    AvaBulletin,
    DangerRating,
    AvalancheProblem,
    Region,
    ValidTime,
)
from avacore.avabulletins import Bulletins
from avacore.processor import JsonProcessor


ATTNS_REGIONS = {
    1: "Western and central parts of Zakarpattia oblast",
    2: "Eastern part of Zakarpattia oblast",
    3: "Ivano-Frankivsk oblast",
    4: "Lviv oblast",
    5: "Chernivtsi oblast",
}
ATTNS_TYPES = {
    1: "Stable",  # new_snow https://www.meteo.gov.ua/_/img/5001.png
    2: "Snowstorm",  # wind_slab https://www.meteo.gov.ua/_/img/5001.png
    3: "Sleet, thaw",  # wet_snow https://www.meteo.gov.ua/_/img/5003.png
    4: "Old, settled",  # persistent_weak_layers https://www.meteo.gov.ua/_/img/5004.png
    5: "Ice-like snow",  # gliding_snow https://www.meteo.gov.ua/_/img/5005.png
}
avalancheProblemTypes = {
    1: "new_snow",
    2: "wind_slab",
    3: "wet_snow",
    4: "persistent_weak_layers",
    5: "gliding_snow",
}
ATTNS_CATS = [
    "Low danger",
    "Moderate danger",
    "Considerable danger",
    "High danger",
    "Very high danger",
]


class A(TypedDict):
    C: int  # ATTNS_CATS
    T: int  # ATTNS_TYPES
    P: str  # "17.01 09:34 &mdash; 23:59"
    D: None


class Obj(TypedDict):
    O: str  # noqa: E741
    U: str
    R: int  # ATTNS_REGIONS
    L: str
    A: List[A]


class Root(TypedDict):
    MAP: str
    UPD: str
    OBJ: List[List[Obj]]


class Processor(JsonProcessor):
    def parse_json(self, region_id, root: Root) -> Bulletins:
        """
        Builds the CAAML JSONs form the original JSON formats.
        """

        tzinfo = ZoneInfo("Europe/Kiev")
        bulletins = Bulletins()
        for obj in (j for i in root["OBJ"] for j in i):
            publicationTime = datetime.strptime(root["UPD"], "%d.%m.%Y, %H:%M")
            publicationTime = publicationTime.replace(tzinfo=tzinfo)
            for a in obj["A"]:
                [start, end] = a["P"].split(" &mdash; ")
                fmt = "%d.%m, %H:%M" if "," in start else "%d.%m %H:%M"
                startTime = datetime.strptime(start, fmt)
                startTime = startTime.replace(year=publicationTime.year, tzinfo=tzinfo)
                if len(end) < 8:
                    end = start.split()[0] + " " + end
                endTime = datetime.strptime(end, fmt)
                endTime = endTime.replace(year=publicationTime.year, tzinfo=tzinfo)
                while startTime < endTime:
                    startTime2359 = startTime.replace(hour=23, minute=59, second=0)
                    bulletin = AvaBulletin(
                        publicationTime=publicationTime,
                        validTime=ValidTime(
                            startTime=startTime,
                            endTime=endTime
                            if endTime > startTime2359
                            else startTime2359,
                        ),
                        regions=[
                            Region(
                                regionID="UA-%02d" % obj["R"],
                                name=ATTNS_REGIONS[obj["R"]],
                            )
                        ],
                        dangerRatings=[DangerRating().set_mainValue_int(a["C"] + 1)],
                        avalancheProblems=[
                            AvalancheProblem(problemType=avalancheProblemTypes[a["T"]])
                        ],
                    )
                    bulletins.append(bulletin)
                    startTime = startTime2359 + timedelta(minutes=1)
        return bulletins
