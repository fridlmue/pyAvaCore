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
from datetime import datetime, timedelta
from typing import Any, List, Optional, TypedDict
from zoneinfo import ZoneInfo

from avacore.avabulletin import (
    AvaBulletin,
    DangerRating,
    AvalancheProblem,
    Region,
)
from avacore.avabulletins import Bulletins
from avacore.processor import JsonProcessor


class PrevisioneValangaItem(TypedDict):
    dataRif: str
    estivo: bool
    regione: Optional[str]
    colorePericolo1: str
    colorePericolo2: str
    codSett: str
    codSottoSett: str
    descSottoSett: str
    gradoPericoloImg: str
    gradoPericoloImgUrl: str
    esposizioneImg: str
    esposizioneImgUrl: str
    quoteCriticheImg: str
    quoteCriticheImgUrl: str
    situazioneTipoImg: str
    situazioneTipoImgUrl: str
    quotaN: str
    quotaS: str
    hNeve: str
    hNeveFresca: Optional[str]
    quotaNeve: Optional[str]
    stSituazione1: Any
    stSituazione2: Any


class Giorno(TypedDict):
    previsioneValanga: List[PrevisioneValangaItem]


class PrevisioniValanghe(TypedDict):
    # generated by datamodel-codegen:
    # filename:  https://servizimeteomont.csifa.carabinieri.it/api/meteomontweb/previsioni/getprevisionivalanghe/data?data=2022-12-10
    giorno0: Giorno
    giorno1: Giorno
    giorno2: Giorno
    giorno3: Giorno


class Processor(JsonProcessor):
    add_eaws_id = False
    tzinfo = ZoneInfo("Europe/Rome")

    def process_bulletin(self, region_id) -> Bulletins:
        root = self._fetch_json(self.url, {})
        return self.parse_json(region_id, root)

    def parse_json(self, region_id, data: PrevisioniValanghe) -> Bulletins:
        bulletins = Bulletins()
        for valanga in data["giorno0"]["previsioneValanga"]:
            bulletins.append(self._parse_valanga(valanga, timedelta(days=0)))
        for valanga in data["giorno1"]["previsioneValanga"]:
            bulletins.append(self._parse_valanga(valanga, timedelta(days=1)))
        for valanga in data["giorno2"]["previsioneValanga"]:
            bulletins.append(self._parse_valanga(valanga, timedelta(days=2)))
        for valanga in data["giorno3"]["previsioneValanga"]:
            bulletins.append(self._parse_valanga(valanga, timedelta(days=3)))
        return bulletins

    def _parse_valanga(
        self, valanga: PrevisioneValangaItem, delta: timedelta
    ) -> AvaBulletin:
        bulletin = AvaBulletin()
        time = bulletin.validTime
        time.startTime = (
            datetime.fromisoformat(re.sub(r"\.\d+", "", valanga["dataRif"])) + delta
        )
        time.startTime = time.startTime.replace(tzinfo=self.tzinfo)
        time.endTime = time.startTime + timedelta(days=1)
        bulletin.regions = [
            Region(
                regionID=f"IT-MeteoMont-{valanga['codSett']}-{valanga['codSottoSett']}",
                name=f"{valanga['regione']} / {valanga['descSottoSett']}",
            )
        ]
        for eaws_id in (
            eaws_id
            for (eaws_id, id) in eaws_regions.items()
            if self.add_eaws_id and id == bulletin.regions[0].regionID
        ):
            bulletin.regions.append(Region(regionID=eaws_id))
        bulletin.dangerRatings = [
            DangerRating().set_mainValue_int(int(valanga["colorePericolo1"] or "0")),
            DangerRating().set_mainValue_int(int(valanga["colorePericolo2"] or "0")),
        ]
        problemType = problemTypes.get(valanga["situazioneTipoImg"], None)
        if problemType:
            bulletin.avalancheProblems = [
                AvalancheProblem(
                    problemType=problemType,
                    # aspects=valanga["esposizioneImg"]
                )
            ]
        bulletin.customData = dict(
            MeteoMont=dict(
                snowDepth=valanga["hNeve"],
                snowDepthAltitude=valanga["quotaNeve"],
                freshSnow=valanga["hNeveFresca"],
            )
        )
        return bulletin


problemTypes = {
    "neveBagnata.jpg": "wet_snow",
    "neveFresca.jpg": "new_snow",
    "neveScivolosa.jpg": "gliding_snow",
    "neveVecchia.jpg": "persistent_weak_layers",
    "neveVentata.jpg": "wind_slab",
}

eaws_regions = {
    "IT-21-CN-01": "IT-MeteoMont-06-7",
    "IT-21-CN-02": "IT-MeteoMont-06-6",
    "IT-21-CN-03": "IT-MeteoMont-06-5",
    "IT-21-CN-04": "IT-MeteoMont-06-5",
    "IT-21-CN-05": "IT-MeteoMont-06-5",
    "IT-21-TO-02": "IT-MeteoMont-06-4",
    "IT-21-TO-03": "IT-MeteoMont-06-4",
    "IT-21-TO-04": "IT-MeteoMont-06-3",
    "IT-21-TO-05": "IT-MeteoMont-06-3",
    "IT-21-VB-01": "IT-MeteoMont-06-2",
    "IT-21-VB-02": "IT-MeteoMont-06-1",
    "IT-21-VB-03": "IT-MeteoMont-06-1",
    "IT-21-VC-01": "IT-MeteoMont-06-2",
    "IT-23-AO-01": "IT-MeteoMont-VA-1",
    "IT-23-AO-02": "IT-MeteoMont-VA-1",
    "IT-23-AO-04": "IT-MeteoMont-VA-1",
    "IT-23-AO-05": "IT-MeteoMont-VA-1",
    "IT-23-AO-06": "IT-MeteoMont-VA-1",
    "IT-23-AO-07": "IT-MeteoMont-VA-1",
    "IT-23-AO-08": "IT-MeteoMont-VA-1",
    "IT-23-AO-09": "IT-MeteoMont-VA-1",
    "IT-23-AO-10": "IT-MeteoMont-VA-1",
    "IT-23-AO-11": "IT-MeteoMont-VA-1",
    "IT-23-AO-12": "IT-MeteoMont-VA-1",
    "IT-23-AO-13": "IT-MeteoMont-VA-1",
    "IT-23-AO-14": "IT-MeteoMont-VA-1",
    "IT-23-AO-15": "IT-MeteoMont-VA-1",
    "IT-23-AO-16": "IT-MeteoMont-VA-1",
    "IT-23-AO-17": "IT-MeteoMont-VA-1",
    "IT-23-AO-18": "IT-MeteoMont-VA-1",
    "IT-23-AO-19": "IT-MeteoMont-VA-1",
    "IT-23-AO-20": "IT-MeteoMont-VA-1",
    "IT-23-AO-21": "IT-MeteoMont-VA-1",
    "IT-23-AO-22": "IT-MeteoMont-VA-1",
    "IT-23-AO-23": "IT-MeteoMont-VA-1",
    "IT-23-AO-24": "IT-MeteoMont-VA-1",
    "IT-23-AO-25": "IT-MeteoMont-VA-1",
    "IT-23-AO-26": "IT-MeteoMont-VA-1",
    "IT-25-BG-01": "IT-MeteoMont-04-2",
    "IT-25-BG-02": "IT-MeteoMont-04-3",
    "IT-25-BS-01": "IT-MeteoMont-04-1",
    "IT-25-BS-02": "IT-MeteoMont-04-3",
    "IT-25-LC-01": "IT-MeteoMont-04-3",
    "IT-25-SO-01": "IT-MeteoMont-04-1",
    "IT-25-SO-02": "IT-MeteoMont-04-1",
    "IT-25-SO-03": "IT-MeteoMont-04-1",
    "IT-32-BZ-01-01": "IT-MeteoMont-TR-1",
    "IT-32-BZ-01-02": "IT-MeteoMont-TR-1",
    "IT-32-BZ-02-01": "IT-MeteoMont-TR-1",
    "IT-32-BZ-02-02": "IT-MeteoMont-TR-1",
    "IT-32-BZ-03": "IT-MeteoMont-TR-1",
    "IT-32-BZ-04-01": "IT-MeteoMont-TR-1",
    "IT-32-BZ-04-02": "IT-MeteoMont-TR-1",
    "IT-32-BZ-05-01": "IT-MeteoMont-TR-1",
    "IT-32-BZ-05-02": "IT-MeteoMont-TR-1",
    "IT-32-BZ-05-03": "IT-MeteoMont-TR-1",
    "IT-32-BZ-06": "IT-MeteoMont-TR-1",
    "IT-32-BZ-07-01": "IT-MeteoMont-TR-1",
    "IT-32-BZ-07-02": "IT-MeteoMont-TR-1",
    "IT-32-BZ-08-01": "IT-MeteoMont-TR-1",
    "IT-32-BZ-08-02": "IT-MeteoMont-TR-1",
    "IT-32-BZ-08-03": "IT-MeteoMont-TR-1",
    "IT-32-BZ-09": "IT-MeteoMont-TR-1",
    "IT-32-BZ-10": "IT-MeteoMont-TR-1",
    "IT-32-BZ-11": "IT-MeteoMont-TR-1",
    "IT-32-BZ-12": "IT-MeteoMont-TR-1",
    "IT-32-BZ-13": "IT-MeteoMont-TR-1",
    "IT-32-BZ-14": "IT-MeteoMont-TR-1",
    "IT-32-BZ-15": "IT-MeteoMont-TR-1",
    "IT-32-BZ-16": "IT-MeteoMont-TR-1",
    "IT-32-BZ-17": "IT-MeteoMont-TR-1",
    "IT-32-BZ-18-01": "IT-MeteoMont-TR-1",
    "IT-32-BZ-18-02": "IT-MeteoMont-TR-1",
    "IT-32-BZ-19": "IT-MeteoMont-TR-1",
    "IT-32-BZ-20": "IT-MeteoMont-TR-1",
    "IT-32-TN-01": "IT-MeteoMont-TR-1",
    "IT-32-TN-02": "IT-MeteoMont-TR-1",
    "IT-32-TN-03": "IT-MeteoMont-TR-1",
    "IT-32-TN-04": "IT-MeteoMont-TR-1",
    "IT-32-TN-05": "IT-MeteoMont-TR-1",
    "IT-32-TN-06": "IT-MeteoMont-TR-1",
    "IT-32-TN-07": "IT-MeteoMont-TR-1",
    "IT-32-TN-08": "IT-MeteoMont-TR-1",
    "IT-32-TN-09": "IT-MeteoMont-TR-1",
    "IT-32-TN-10": "IT-MeteoMont-TR-1",
    "IT-32-TN-11": "IT-MeteoMont-TR-1",
    "IT-32-TN-12": "IT-MeteoMont-TR-1",
    "IT-32-TN-13": "IT-MeteoMont-TR-1",
    "IT-32-TN-14": "IT-MeteoMont-TR-1",
    "IT-32-TN-15": "IT-MeteoMont-TR-1",
    "IT-32-TN-16": "IT-MeteoMont-TR-1",
    "IT-32-TN-17": "IT-MeteoMont-TR-1",
    "IT-32-TN-18": "IT-MeteoMont-TR-1",
    "IT-32-TN-19": "IT-MeteoMont-TR-1",
    "IT-32-TN-20": "IT-MeteoMont-TR-1",
    "IT-32-TN-21": "IT-MeteoMont-TR-1",
    "IT-34-BL-02": "IT-MeteoMont-02-1",
    "IT-34-BL-03": "IT-MeteoMont-02-1",
    "IT-34-BL-06": "IT-MeteoMont-02-3",
    "IT-34-VI-01": "IT-MeteoMont-02-3",
    "IT-34-VR-01": "IT-MeteoMont-02-3",
    "IT-36-UD-01": "IT-MeteoMont-01-3",
    "IT-36-UD-03": "IT-MeteoMont-01-1",
    "IT-36-UD-04": "IT-MeteoMont-01-1",
}
