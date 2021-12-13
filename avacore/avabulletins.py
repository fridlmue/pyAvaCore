import typing
from .avabulletin import AvaBulletin, DangerRatingType
from .geojson import Feature, FeatureCollection


class Bulletins:
    """
    Class for the AvaBulletin collection
    Follows partly CAAMLv6 caaml:Bulletins
    """

    bulletins: typing.List[AvaBulletin]

    def max_danger_ratings(self):
        ratings = dict()
        for bulletin in self.bulletins:
            for region in bulletin.regions:
                regionID = region.regionID
                for danger in bulletin.dangerRatings:
                    if (
                        Bulletins.region_without_elevation(regionID)
                        or not danger.elevation
                        or danger.elevation.toString() == ""
                        or danger.elevation.toString().startswith("<")
                    ):
                        key = f"{regionID}:low"
                        ratings[key] = max(
                            danger.get_mainValue_int(), ratings.get(key, 0)
                        )
                    if (
                        Bulletins.region_without_elevation(regionID)
                        or not danger.elevation
                        or danger.elevation.toString() == ""
                        or danger.elevation.toString().startswith(">")
                    ):
                        key = f"{regionID}:high"
                        ratings[key] = max(
                            danger.get_mainValue_int(), ratings.get(key, 0)
                        )
        return ratings

    def augment_geojson(self, geojson: FeatureCollection):
        for feature in geojson.features:
            self.augment_feature(feature)

    def augment_feature(self, feature: Feature):
        id = feature.properties.id
        elevation = feature.properties.elevation

        def affects_region(b: AvaBulletin):
            return id in [r.regionID for r in b.regions]

        def affects_danger(d: DangerRatingType):
            if Bulletins.region_without_elevation(id):
                return True
            elif not d.elevation:
                return True
            elif not (
                hasattr(d.elevation, "lowerBound") or hasattr(d.elevation, "upperBound")
            ):
                return True
            elif hasattr(d.elevation, "upperBound") and elevation == "low":
                return True
            elif hasattr(d.elevation, "lowerBound") and elevation == "high":
                return True
            else:
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
    def region_without_elevation(id: str):
        return (
            id.startswith("CH-")
            or id.startswith("IT-21-")
            or id.startswith("IT-23-")
            or id.startswith("IT-25-")
            or id.startswith("IT-25-")
            or id.startswith("IT-34-")
            or id.startswith("IT-36-")
            or id.startswith("IT-57-")
            or id.startswith("FR-")
        )
