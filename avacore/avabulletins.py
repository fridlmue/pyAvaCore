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

from dataclasses import dataclass, field
from datetime import date, datetime
import json
import typing
from typing import Optional, Any, List, Callable

from .MetaData import MetaData

from .avajson import JSONEncoder
from .avabulletin import AvaBulletin, DangerRating, Provider, ValidTimePeriod, Elevation
from .geojson import Feature, FeatureCollection


@dataclass
class Bulletins:
    """JSON schema for EAWS avalanche bulletin collection following the CAAMLv6 schema"""

    bulletins: List[AvaBulletin] = field(default_factory=list)
    customData: Any = None
    metaData: Optional[MetaData] = None

    def __getitem__(self, item):
        return self.bulletins[item]

    def __len__(self):
        return len(self.bulletins)

    def append(self, bulletin: AvaBulletin):
        """
        Appends a bulletin
        """
        self.bulletins.append(bulletin)

    def append_raw_data(self, file_extension: str, data: str):
        """
        Stores the given raw data as customData
        """
        self.customData = self.customData or {}
        self.customData["file_extension"] = file_extension
        self.customData["data"] = data

    def append_provider(self, provider_name: str, website: str):
        """
        Stores the given provider/url as source/provider on each bulletin
        """
        for bulletin in self.bulletins:
            if not bulletin.source.provider:
                bulletin.source.provider = Provider()
            bulletin.source.provider.name = provider_name
            bulletin.source.provider.website = website

    def append_main_date(self):
        for bulletin in self.bulletins:
            bulletin.customData = bulletin.customData or {}
            bulletin.customData.update(
                dict(ALBINA=dict(mainDate=bulletin.main_date().isoformat()))
            )

    def main_date(self) -> date:
        """
        Returns Main validity date of Reports
        """
        if not self.bulletins:
            return None
        return self.bulletins[0].main_date()

    def main_dates(
        self, protect_overwrite_now: typing.Optional[datetime] = None
    ) -> typing.Set[date]:
        """
        Returns Main validity dates of Reports

        protect_override_now expects the date_time "now" to remove the bulletins,
        that are from the day before.
        """

        validity_dates = {
            date
            for bulletin in self.bulletins
            for date in bulletin.main_dates()
            if protect_overwrite_now is None or date >= protect_overwrite_now.date()
        }

        if (
            len(validity_dates) > 1
            and protect_overwrite_now is not None
            and min(validity_dates) == protect_overwrite_now.date()
            and protect_overwrite_now.hour > 14
        ):
            validity_dates.remove(min(validity_dates))

        return validity_dates

    def all_avalanche_problems(self, validity_date, region_id=""):
        """
        Returns a Dict containing a list of all avalanche problems
        """
        return self._to_dict(
            validity_date,
            region_id,
            lambda bulletin, elevation, validTimePeriod: [
                r.problemType
                for r in bulletin.avalancheProblems
                if (not r.elevation or r.elevation.matches_elevation(elevation))
                and validTimePeriod.matches_valid_time_period(r.validTimePeriod)
            ],
        )

    def max_danger_ratings(self, validity_date, region_id=""):
        """
        Returns a Dict containing the main danger ratings (total, high, low, am, pm)
        """
        return self._to_dict(
            validity_date,
            region_id,
            lambda bulletin, elevation, validTimePeriod: max(
                [
                    r.get_mainValue_int()
                    for r in bulletin.dangerRatings
                    if (not r.elevation or r.elevation.matches_elevation(elevation))
                    and validTimePeriod.matches_valid_time_period(r.validTimePeriod)
                ]
                or [0]
            ),
        )

    def _to_dict(
        self,
        validity_date,
        region_id,
        to_value: Callable[
            [
                AvaBulletin,
                Elevation,
                ValidTimePeriod,
            ],
            Any,
        ],
    ):
        return {
            key: to_value(bulletin, elevation, validTimePeriod)
            for bulletin in self.bulletins
            for region in bulletin.regions
            for validTimePeriod in [
                ValidTimePeriod.all_day,
                ValidTimePeriod.earlier,
                ValidTimePeriod.later,
            ]
            for elevation in ["", "low", "high"]
            if validity_date in bulletin.main_dates()
            if (
                key := ":".join(
                    s
                    for s in [
                        region.regionID,
                        elevation,
                        validTimePeriod.to_am_pm(),
                    ]
                    if s
                )
            )
            if (not region_id or key.startswith(region_id))
        }

    def augment_geojson(self, geojson: FeatureCollection):
        """
        Augment geojson with features.
        """
        for feature in geojson.features:
            self.augment_feature(feature)

    def augment_feature(self, feature: Feature):
        """
        Augment features with danger rating in information
        """
        idx = feature.properties.id
        elevation = feature.properties.elevation

        def affects_region(b: AvaBulletin):
            return idx in [r.regionID for r in b.regions]

        def affects_danger(d: DangerRating):
            if not d.elevation:
                return True
            if not (
                hasattr(d.elevation, "lowerBound") or hasattr(d.elevation, "upperBound")
            ):
                return True
            if hasattr(d.elevation, "upperBound") and elevation == "low":
                return True
            if hasattr(d.elevation, "lowerBound") and elevation == "high":
                return True

            return False

        bulletins = [b for b in self.bulletins if affects_region(b)]
        dangers = [
            d.get_mainValue_int()
            for b in bulletins
            for d in b.dangerRatings
            if affects_danger(d)
        ]
        if not dangers:
            return
        feature.properties.max_danger_rating = max(dangers)

    @staticmethod
    def from_dict(obj: Any) -> "Bulletins":
        assert isinstance(obj, dict)
        return Bulletins(
            bulletins=[AvaBulletin.from_dict(b) for b in obj.get("bulletins", [])],
            customData=obj.get("customData"),
            metaData=obj.get("metaData"),
        )

    def to_json(self) -> str:
        """write bulletins as CAAMLv6 JSON string"""
        return json.dumps(self, cls=JSONEncoder, indent=2, sort_keys=True)
