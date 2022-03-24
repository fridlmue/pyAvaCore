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

from datetime import date, datetime, timedelta
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
        validityDate: datetime = self.bulletins[0].validTime.startTime
        if validityDate.hour > 15:
            validityDate = validityDate + timedelta(days=1)
        return validityDate.date()


    def max_danger_ratings(self):
        ratings = dict()
        for bulletin in self.bulletins:
            
            bulletin.cli_out()

            for region in bulletin.regions:
                local_ratings = dict()
                regionId = region.regionId
                # Check for available information in Bulletin
                
                for danger in bulletin.dangerRatings:
                    if (danger.elevation.toString().startswith("<")):
                        key = f"{regionId}:high"
                    elif (danger.elevation.toString().startswith(">")):
                        key = f"{regionId}:low"
                    else:
                        key = f"{regionId}"
                    
                    if (danger.validTimePeriod == 'earlier'):
                        key = key + ':am'
                    elif (danger.validTimePeriod == 'later'):
                        key = key + ':pm'
                    
                    local_ratings[key] = danger.get_mainValue_int()
                    
                    if not 'high' in key and not 'low' in key:
                        local_ratings[key + ':high'] = danger.get_mainValue_int()
                        local_ratings[key + ':low'] = danger.get_mainValue_int()
                    
                    if 'all_day' in danger.validTimePeriod:
                        if not 'high' in key and not 'low' in key:
                            local_ratings[key + ':high:am'] = danger.get_mainValue_int()
                            local_ratings[key + ':low:am'] = danger.get_mainValue_int()
                            local_ratings[key + ':high:pm'] = danger.get_mainValue_int()
                            local_ratings[key + ':low:pm'] = danger.get_mainValue_int()
                        else:
                            local_ratings[key + ':am'] = danger.get_mainValue_int()
                            local_ratings[key + ':pm'] = danger.get_mainValue_int()
                    
                # Fill missing ratings for the current Region
                if not f"{regionId}:low" in local_ratings:
                    if f"{regionId}:low:am" in local_ratings.keys() and f"{regionId}:low:pm" in local_ratings.keys():
                        local_ratings[f"{regionId}:low"] = max(local_ratings[f"{regionId}:low:am"], local_ratings[f"{regionId}:low:pm"])
                    elif f"{regionId}:low:am" in local_ratings.keys():
                        local_ratings[f"{regionId}:low"] = local_ratings[f"{regionId}:low:am"]
                    elif f"{regionId}:low:pm" in local_ratings.keys():
                        local_ratings[f"{regionId}:low"] = local_ratings[f"{regionId}:low:pm"]
                    elif f"{regionId}:high" in local_ratings.keys():
                        local_ratings[f"{regionId}:low"] = local_ratings[f"{regionId}:high"]
                        
                if not f"{regionId}:high" in local_ratings:
                    if f"{regionId}:high:am" in local_ratings.keys() and f"{regionId}:high:pm" in local_ratings.keys():
                        local_ratings[f"{regionId}:high"] = max(local_ratings[f"{regionId}:high:am"], local_ratings[f"{regionId}:high:pm"])
                    elif f"{regionId}:high:am" in local_ratings.keys():
                        local_ratings[f"{regionId}:high"] = local_ratings[f"{regionId}:high:am"]
                    elif f"{regionId}:high:pm" in local_ratings.keys():
                        local_ratings[f"{regionId}:high"] = local_ratings[f"{regionId}:high:pm"]
                    elif f"{regionId}:low" in local_ratings.keys():
                        local_ratings[f"{regionId}:high"] = local_ratings[f"{regionId}:low"]
                
                if not f"{regionId}:high:am" in local_ratings and not not f"{regionId}:high:pm" in local_ratings:
                    local_ratings[f"{regionId}:high:am"] = local_ratings[f"{regionId}:high:pm"] = local_ratings[f"{regionId}:high"]
                    
                if not f"{regionId}:low:am" in local_ratings and not not f"{regionId}:low:pm" in local_ratings:
                    local_ratings[f"{regionId}:low:am"] = local_ratings[f"{regionId}:low:pm"] = local_ratings[f"{regionId}:low"]
                
                '''
                if not f"{regionId}:high" in local_ratings:
                    if f"{regionId}:low" in local_ratings.keys():
                        local_ratings[f"{regionId}:high"] = local_ratings[f"{regionId}:low"]
                    else:
                        local_ratings[f"{regionId}:low"] = max(local_ratings[f"{regionId}:low:am"], local_ratings[f"{regionId}:low:pm"])
                '''
                
                key = f"{regionId}:high"
                if not key in local_ratings.keys():
                    local_ratings[key] = max(local_ratings[f"{key}:am"], local_ratings[f"{key}:pm"])
                
                key = f"{regionId}:low"
                if not key in local_ratings.keys():
                    local_ratings[key] = max(local_ratings[f"{key}:am"], local_ratings[f"{key}:pm"])
                    
                key = regionId
                local_ratings[f"{key}:am"] = max(local_ratings[f"{key}:high:am"], local_ratings[f"{key}:low:am"])
                    
                local_ratings[f"{key}:pm"] = max(local_ratings[f"{key}:high:pm"], local_ratings[f"{key}:low:pm"])

                local_ratings[key] = max(local_ratings.values())
                
                ratings.update(local_ratings)
            
            '''
            for region in bulletin.regions:
                regionId = region.regionId
                for danger in bulletin.dangerRatings:
                    if (
                        not danger.elevation
                        or danger.elevation.toString() == ""
                        or danger.elevation.toString().startswith("<")
                    ):
                        pm = ''
                        if hasattr(bulletin, 'predecessor_id'):
                            pm = ':pm'
                            key = f"{regionId}:low"
                            if key in ratings:
                                ratings[f"{key}:am"] = ratings.pop(key)
                        key = f"{regionId}:low{pm}"
                        ratings[key] = max(
                            danger.get_mainValue_int(), ratings.get(key, 0)
                        )
                        if pm == '' and key+':pm' in ratings and not key+':am' in ratings:
                            ratings[f"{key}:am"] = ratings[key]
                    if (
                        not danger.elevation
                        or danger.elevation.toString() == ""
                        or danger.elevation.toString().startswith(">")
                    ):
                        pm = ''
                        if hasattr(bulletin, 'predecessor_id'):
                            pm = ':pm'
                            key = f"{regionId}:high"
                            if key in ratings:
                                ratings[f"{key}:am"] = ratings.pop(key)
                        key = f"{regionId}:high{pm}"
                        ratings[key] = max(
                            danger.get_mainValue_int(), ratings.get(key, 0)
                        )
                        if pm == '' and key+':pm' in ratings and not key+':am' in ratings:
                            ratings[f"{key}:am"] = ratings[key]

            for region in bulletin.regions:
                regionId = region.regionId
                sel_ratings = [value for key,value in ratings.items() if regionId in key]
                sel_keys = [key for key,value in ratings.items() if regionId in key]
                                
                try:
                    if not f"{regionId}:low" in ratings:
                        ratings[f"{regionId}:low"] = ratings[f"{regionId}:high"]
                        
                    if not f"{regionId}:high" in ratings:
                        ratings[f"{regionId}:high"] = ratings[f"{regionId}:low"]
                except:
                    pass
                
                try:
                    if not ('am' in sel_keys[0]) and not ('pm' in sel_keys[0]):
                        key = f"{regionId}:high"
                        ratings[f"{key}:am"] = ratings[key]
                        ratings[f"{key}:pm"] = ratings[key]
                        key = f"{regionId}:low"
                        ratings[f"{key}:am"] = ratings[key]
                        ratings[f"{key}:pm"] = ratings[key]
                except:
                    pass

                try:
                    sel_ratings = [value for key,value in ratings.items() if regionId in key]
                    key = f"{regionId}:high"
                    ratings[key] = max(ratings[f"{key}:am"], ratings[f"{key}:pm"])
                    
                    key = f"{regionId}:low"    
                    ratings[key] = max(ratings[f"{key}:am"], ratings[f"{key}:pm"])
                        
                    key = regionId
                    sel_ratings = [value for key,value in ratings.items() if regionId in key]
                    # if not f"{key}:am" in sel_keys:
                    ratings[f"{key}:am"] = max(ratings[f"{key}:high:am"], ratings[f"{key}:low:am"])
                        
                    # if not f"{key}:pm" in sel_keys:
                    ratings[f"{key}:pm"] = max(ratings[f"{key}:high:pm"], ratings[f"{key}:low:pm"])
                    
                    sel_ratings = [value for key,value in ratings.items() if regionId in key]
                    # if not key in sel_keys:
                    ratings[key] = max(sel_ratings)
                except:
                    # Probably PM report was before AM report in JSON
                    pass
            '''


        # return 0 independent of "no_snow" or "no_rating"
        for key, value in ratings.items():
            if value == -1:
                ratings[key] = 0

        return ratings

    def augment_geojson(self, geojson: FeatureCollection):
        for feature in geojson.features:
            self.augment_feature(feature)

    def augment_feature(self, feature: Feature):
        id = feature.properties.id
        elevation = feature.properties.elevation

        def affects_region(b: AvaBulletin):
            return id in [r.regionId for r in b.regions]

        def affects_danger(d: DangerRating):
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

    def from_json(self, bulletins_json):
        self.bulletins = []
        for bulletin_json in bulletins_json['bulletins']:
            bulletin = AvaBulletin()
            bulletin.from_json(bulletin_json)
            self.bulletins.append(bulletin)
