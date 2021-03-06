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

from datetime import date
import typing

from .avabulletin import AvaBulletin, DangerRating
from .geojson import Feature, FeatureCollection


class Bulletins:
    """
    Class for the AvaBulletin collection
    Follows partly CAAMLv6 caaml:Bulletins
    """

    bulletins: typing.List[AvaBulletin]

    def main_date(self) -> date:
        """
        Returns Main validity date of Reports
        """
        return self.bulletins[0].main_date()

    def main_dates(self, protect_overwrite_now=None) -> typing.Set[date]:
        """
        Returns Main validity dates of Reports

        protect_override_now expects the date_time "now" to remove the bulletins,
        that are from the day before.
        """

        validity_dates = {
            d for bulletin in self.bulletins for d in bulletin.main_dates()
        }

        if protect_overwrite_now is not None:
            validityDate_iter = validity_dates.copy()
            for validity_date in validityDate_iter:
                if validity_date < protect_overwrite_now.date():
                    validity_dates.remove(validity_date)

            if (
                len(validity_dates) > 1
                and min(validity_dates) == protect_overwrite_now.date()
                and protect_overwrite_now.hour > 14
            ):
                validity_dates.remove(min(validity_dates))

        return validity_dates

    def strip_wrong_day_reports(self, validity_date):
        """
        Returns only Bulletins of validityDate in main_dates
        """
        rel_bulletins = []

        for bulletin in self.bulletins:
            if validity_date in bulletin.main_dates():
                rel_bulletins.append(bulletin)
        return rel_bulletins

    def max_danger_ratings(self, validity_date):
        # pylint: disable=too-many-branches
        # pylint: disable=too-many-statements
        # pylint: disable=too-many-nested-blocks
        """
        Returns a Dict containing the main danger ratings (total, high, low, am, pm)
        """
        ratings = {}
        for bulletin in self.strip_wrong_day_reports(validity_date):

            for region in bulletin.regions:
                local_ratings = {}
                regionId = region.regionId

                if len(bulletin.dangerRatings) > 1:
                    remove = []
                    for i in range(0, len(bulletin.dangerRatings) - 1):
                        if (
                            bulletin.dangerRatings[i].elevation.toString()
                            == bulletin.dangerRatings[i + 1].elevation.toString()
                            and bulletin.dangerRatings[i].validTimePeriod
                            == bulletin.dangerRatings[i + 1].validTimePeriod
                        ):
                            if (
                                bulletin.dangerRatings[i].get_mainValue_int()
                                > bulletin.dangerRatings[i + 1].get_mainValue_int()
                            ):
                                remove.append(i + 1)
                            else:
                                remove.append(i)
                    for j in remove:
                        del bulletin.dangerRatings[j]

                for danger in bulletin.dangerRatings:

                    key_elev = ""
                    key_time = ""

                    if danger.elevation.toString().startswith(">"):
                        key_elev = ":high"
                    elif danger.elevation.toString().startswith("<"):
                        key_elev = ":low"

                    if danger.validTimePeriod == "earlier":
                        key_time = ":am"
                    elif danger.validTimePeriod == "later":
                        key_time = ":pm"

                    local_ratings[
                        f"{regionId}{key_elev}{key_time}"
                    ] = danger.get_mainValue_int()

                    if key_elev == "":
                        local_ratings[
                            f"{regionId}:high{key_time}"
                        ] = danger.get_mainValue_int()
                        local_ratings[
                            f"{regionId}:low{key_time}"
                        ] = danger.get_mainValue_int()

                    if key_time == "":
                        if key_elev == "":
                            local_ratings[
                                f"{regionId}:high:am"
                            ] = danger.get_mainValue_int()
                            local_ratings[
                                f"{regionId}:high:pm"
                            ] = danger.get_mainValue_int()
                            local_ratings[
                                f"{regionId}:low:am"
                            ] = danger.get_mainValue_int()
                            local_ratings[
                                f"{regionId}:low:pm"
                            ] = danger.get_mainValue_int()
                        else:
                            local_ratings[
                                f"{regionId}{key_elev}:am"
                            ] = danger.get_mainValue_int()
                            local_ratings[
                                f"{regionId}{key_elev}:pm"
                            ] = danger.get_mainValue_int()

                # Fill missing ratings for the current Region
                if not f"{regionId}:low" in local_ratings:
                    if (
                        f"{regionId}:low:am" in local_ratings
                        and f"{regionId}:low:pm" in local_ratings
                    ):
                        local_ratings[f"{regionId}:low"] = max(
                            local_ratings[f"{regionId}:low:am"],
                            local_ratings[f"{regionId}:low:pm"],
                        )
                    elif f"{regionId}:low:am" in local_ratings:
                        local_ratings[f"{regionId}:low"] = local_ratings[
                            f"{regionId}:low:am"
                        ]
                    elif f"{regionId}:low:pm" in local_ratings:
                        local_ratings[f"{regionId}:low"] = local_ratings[
                            f"{regionId}:low:pm"
                        ]
                    elif f"{regionId}:high" in local_ratings:
                        local_ratings[f"{regionId}:low"] = local_ratings[
                            f"{regionId}:high"
                        ]

                if not f"{regionId}:high" in local_ratings:
                    if (
                        f"{regionId}:high:am" in local_ratings
                        and f"{regionId}:high:pm" in local_ratings
                    ):
                        local_ratings[f"{regionId}:high"] = max(
                            local_ratings[f"{regionId}:high:am"],
                            local_ratings[f"{regionId}:high:pm"],
                        )
                    elif f"{regionId}:high:am" in local_ratings:
                        local_ratings[f"{regionId}:high"] = local_ratings[
                            f"{regionId}:high:am"
                        ]
                    elif f"{regionId}:high:pm" in local_ratings:
                        local_ratings[f"{regionId}:high"] = local_ratings[
                            f"{regionId}:high:pm"
                        ]
                    elif f"{regionId}:low" in local_ratings:
                        local_ratings[f"{regionId}:high"] = local_ratings[
                            f"{regionId}:low"
                        ]

                if (
                    not f"{regionId}:high:am" in local_ratings
                    and not f"{regionId}:high:pm" in local_ratings
                ):
                    local_ratings[f"{regionId}:high:am"] = local_ratings[
                        f"{regionId}:high:pm"
                    ] = local_ratings[f"{regionId}:high"]

                if (
                    not f"{regionId}:low:am" in local_ratings
                    and not f"{regionId}:low:pm" in local_ratings
                ):
                    local_ratings[f"{regionId}:low:am"] = local_ratings[
                        f"{regionId}:low:pm"
                    ] = local_ratings[f"{regionId}:low"]

                key = f"{regionId}:high"
                if not key in local_ratings:
                    local_ratings[key] = max(
                        local_ratings[f"{key}:am"], local_ratings[f"{key}:pm"]
                    )

                key = f"{regionId}:low"
                if not key in local_ratings:
                    local_ratings[key] = max(
                        local_ratings[f"{key}:am"], local_ratings[f"{key}:pm"]
                    )

                key = regionId
                local_ratings[f"{key}:am"] = max(
                    local_ratings[f"{key}:high:am"], local_ratings[f"{key}:low:am"]
                )

                local_ratings[f"{key}:pm"] = max(
                    local_ratings[f"{key}:high:pm"], local_ratings[f"{key}:low:pm"]
                )

                local_ratings[key] = max(local_ratings.values())

                ratings.update(local_ratings)

        # return 0 independent of "no_snow" or "no_rating"
        for key, value in ratings.items():
            if value == -1:
                ratings[key] = 0

        return ratings

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
            return idx in [r.regionId for r in b.regions]

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

    def from_json(self, bulletins_json):
        """
        read bulletions from CAAMLv6 JSON
        """
        self.bulletins = []
        for bulletin_json in bulletins_json["bulletins"]:
            bulletin = AvaBulletin()
            bulletin.from_json(bulletin_json)
            self.bulletins.append(bulletin)
