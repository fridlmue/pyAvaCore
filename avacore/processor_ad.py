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
from datetime import timedelta
import re
import copy
import pytz
import dateutil.parser
from avacore.avabulletin import (
    Region,
    DangerRating,
    AvaBulletin,
)

ad_ids = {"nord": "AD-01", "centre": "AD-02", "sud": "AD-03"}


def parse_xml(root):

    """parses Andora Danger Ratgin XML"""

    bulletins = []

    bulletin = AvaBulletin()
    bulletin.publicationTime = pytz.timezone("Europe/Paris").localize(
        dateutil.parser.parse(root.find("date").text)
    )
    bulletin.validTime.startTime = bulletin.publicationTime
    bulletin.validTime.endTime = bulletin.publicationTime + timedelta(
        hours=23, minutes=59, seconds=59
    )

    for geopos in root.iter("gp"):
        local_bulletin = copy.deepcopy(bulletin)
        local_bulletin.regions.append(Region(ad_ids[geopos.attrib["id"]]))
        local_bulletin.bulletinID = (
            f'{ad_ids[geopos.attrib["id"]]}_{bulletin.publicationTime}'
        )

        for neige in geopos.iter("neige"):
            if "risc" in neige.attrib["data"]:
                idstate = neige.attrib["idstate"]

                if "damunt" in idstate:
                    ratings = idstate.split("damunt")
                    validity = ["all_day", "all_day"]
                    elevation = [">", "<"]

                elif 'escala-allau' in idstate:
                    results = re.findall(r"\d*(\d-\d|\d)", idstate)
                    ratings = []
                    loc_validity = ['earlier', 'later']
                    validity = []
                    loc_elevation = ["<", ">"]
                    elevation = []
                    for idx, result in enumerate(results):
                        if '-' in result:
                            loc_ratings = result.split('-')
                            for idy, loc_rating in enumerate(loc_ratings):
                                validity.append(loc_validity[idy])
                                elevation.append(loc_elevation[idx])
                                ratings.append(loc_rating)
                        else:
                            validity.append('all_day')
                            elevation.append(loc_elevation[idx])
                            ratings.append(result)

                elif '-' in idstate:
                    levels = idstate.split('-')
                    ratings = idstate.split('-')
                    elevation = ['', '']
                    validity = ['earlier', 'later']

                else:
                    ratings = [idstate]
                    validity = ["all_day"]
                    elevation = [""]

                for idx, rating in enumerate(ratings):
                    dangerRating = DangerRating()
                    dangerRating.set_mainValue_int(int(rating))
                    dangerRating.validTimePeriod = validity[idx]
                    dangerRating.elevation.auto_select(elevation[idx])
                    local_bulletin.dangerRatings.append(dangerRating)

        bulletins.append(local_bulletin)

    return bulletins
