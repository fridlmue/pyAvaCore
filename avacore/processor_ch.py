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
from typing import List, Any, Optional, TypedDict, Iterable

from .avabulletins import Bulletins
from .avabulletin import (
    AvaBulletin,
    DangerRating,
    AvalancheProblem,
    Region,
    Texts,
    ValidTime,
)
from .processor import JsonProcessor


class Geometry(TypedDict):
    type: str
    coordinates: List[List[Any]]


class Text(TypedDict):
    de: str
    fr: str
    it: str
    en: str


class Altitude(TypedDict):
    indicator: str
    altitude: int


class Aspect(TypedDict):
    aspect_from: str
    to: str


class Dangerlevel(TypedDict):
    level: str
    reliability: None
    level_detail: Optional[str]


class Rating(TypedDict):
    dangerlevel: Dangerlevel
    majorAvalProblems: List[str]
    additionalAvalProblems: List[str]
    aspect: Optional[Aspect]
    altitude: Optional[Altitude]
    majorDangerDescription: Text
    remarks: Optional[Text]
    coreZoneText: Optional[Text]
    additionalDangerDescription: Optional[Text]


class Properties(TypedDict):
    sector_ids: List[int]
    warnregion_def_id: int
    rating: Rating
    fill: str


class Feature(TypedDict):
    type: str
    properties: Properties
    geometry: Geometry
    id: int


class Geojson(TypedDict):
    type: str
    features: List[Feature]


class Rating1(TypedDict):
    rating_type: str
    regions: None
    geojson: Geojson


class Paragraph(TypedDict):
    title_de: str
    title_fr: str
    title_it: str
    title_en: str
    de: Optional[str]
    fr: Optional[str]
    it: Optional[str]
    en: Optional[str]
    subparagraphs: Optional[List["Paragraph"]]


class SnowWeather(TypedDict):
    text_translation_delayed: None
    paragraphs: List[Paragraph]


class AvalancheMapBulletin(TypedDict):
    rating_1: Rating1
    rating_2: None
    snow_weather: SnowWeather


class AvalancheBulletin(TypedDict):
    id: int
    valid_from: str
    valid_to: str
    bulletin_type: str
    unscheduled: bool
    next_update: str
    flash: Text
    avalanche_map_bulletin: AvalancheMapBulletin
    avalanche_text_bulletin: None


class Root(TypedDict):
    # Generated using https://app.quicktype.io/
    bulletin_active: bool
    bulletin_delayed: None
    avalanche_bulletin: AvalancheBulletin


class Processor(JsonProcessor):
    """
    Fetches from the SLF: Avalanche Bulletin API -- https://api.slf.ch/bulletin/v2/
    """
    local = 'en'

    def process_bulletin(self, region_id) -> Bulletins:
        self.url, self.local = self.url.split('#', maxsplit=1)
        root = self._fetch_json(self.url, {})
        return self.parse_json(region_id, root)

    def parse_json(self, region_id: str, data: Root) -> Bulletins:
        data_bulletin = data["avalanche_bulletin"]
        data_bulletins = data_bulletin["avalanche_map_bulletin"]

        valid = ValidTime(
            startTime=datetime.fromisoformat(
                data_bulletin["valid_from"].replace("Z", "+00:00")
            ),
            endTime=datetime.fromisoformat(
                data_bulletin["valid_to"].replace("Z", "+00:00")
            ),
        )
        flash = data_bulletin["flash"][self.local]
        bulletins = Bulletins()
        for feature in data_bulletins["rating_1"]["geojson"]["features"]:
            bulletin = AvaBulletin()
            bulletins.append(bulletin)
            bulletin.bulletinID = (
                f"CH-{data['avalanche_bulletin']['id']}-{feature['id']}"
            )
            bulletin.validTime = valid
            bulletin.regions = [
                Region(f"CH-{r}") for r in feature["properties"]["sector_ids"]
            ]
            rating = feature["properties"]["rating"]
            bulletin.dangerRatings = [
                DangerRating().set_mainValue_int(int(rating["dangerlevel"]["level"][0]))
            ]
            bulletin.avalancheProblems = [
                AvalancheProblem().add_problemType(p.lower())
                for p in (
                    []
                    + rating.get("majorAvalProblems", [])
                    + rating.get("additionalAvalProblems", [])
                )
            ]
            bulletin.customData = dict(
                SLF=dict(
                    avalancheProneLocation=dict(
                        aspects=AvalancheProblem()
                        .add_aspects(rating["aspect"]["from"], rating["aspect"]["to"])
                        .aspects
                        if rating["aspect"]
                        and "from" in rating["aspect"]
                        and "to" in rating["aspect"]
                        else None,
                        elevation=rating["altitude"],
                    ),
                    dangerLevelDetail=rating["dangerlevel"]["level_detail"],
                )
            )
            bulletin.highlights = flash
            bulletin.avalancheActivity = self._parse_text(
                rating.get("majorDangerDescription", None)
            )
            bulletin.snowpackStructure = self._parse_text(
                rating.get("additionalDangerDescription", None)
            )
            paragraphs = data_bulletins["snow_weather"]["paragraphs"]
            bulletin.wxSynopsis = Texts(
                comment="\n".join(l for l in self._parse_paragraphs(paragraphs) if l)
            )
        return bulletins

    def _parse_text(self, text: Optional[Text]) -> Texts:
        return Texts(comment=text[self.local] if text and self.local in text else None)

    def _parse_paragraphs(self, paragraphs: Optional[list[Paragraph]]) -> Iterable[str]:
        for p in paragraphs or []:
            yield p.get(f"title_{self.local}", "") or ""
            yield p.get(self.local, "") or ""
            yield from self._parse_paragraphs(p.get("subparagraphs", []))
