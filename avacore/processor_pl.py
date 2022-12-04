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

from avacore.avabulletin import (
    AvaBulletin,
    AvalancheProblem,
    DangerRating,
    Region,
    Tendency,
    ValidTime,
)
from avacore.avabulletins import Bulletins
from avacore.processor import Processor as AbstractProcessor


class Processor(AbstractProcessor):
    def process_all_reports(self) -> Bulletins:
        return Bulletins(
            bulletins=[
                self.process_bulletin(region_id).bulletins[0] for region_id in regions
            ]
        )

    def process_bulletin(self, region_id) -> Bulletins:
        if region_id == "PL":
            return self.process_all_reports()
        url = self.url.format(region=regions[region_id])
        response: str = self._fetch_url(url, {})
        self.raw_data += response
        self.raw_data_format = "html"
        return self.parse_html(region_id, response)

    def parse_html(self, region_id: str, html: str) -> Bulletins:
        """
        Processes downloaded report
        """
        bulletin = AvaBulletin()
        bulletin.regions = [Region(regionID=region_id)]
        bulletin.validTime = ValidTime(
            startTime=re.compile(r"(\d{4})-(\d{2})-(\d{2})\ (\d{2}):(\d{2}):(\d{2})")
            .search(html)
            .group()
        )
        bulletin.validTime.endTime = bulletin.validTime.startTime + timedelta(days=1)
        bulletin.dangerRatings = [
            DangerRating(
                mainValue={
                    "no_rating_icon": "no_rating",
                    "no_snow": "no_snow",
                    "1_icon_num": "low",
                    "2_icon_num": "moderate",
                    "3_icon_num": "considerable",
                    "4_icon_num": "high",
                    "5_icon_num": "very_high",
                }.get(
                    re.compile(r"avalanche/rating/(?P<dangerLevel>[^\"]+).png")
                    .search(html)
                    .group("dangerLevel")
                )
            )
        ]

        bulletin.avalancheProblems = [
            AvalancheProblem().add_problemType(m.group("problem"))
            for m in re.finditer(
                r'avalanche/avalancheproblems/ap_(?P<problem>[^"]+).png', html
            )
        ]

        tendency = re.compile(r'avalanche/trend/(?P<tendency>[^"]+).png').search(html)
        if tendency:
            bulletin.tendency = Tendency(tendencyComment=tendency.group("tendency"))

        # TODO N-W -> N-NW-W
        # bulletin.customData = dict(
        #     PL=dict(
        #         avalancheProneLocation=dict(
        #             aspects=re.compile(r'avalanche/direction/(?P<aspects>[^"]+).png')
        #             .search(html)
        #             .group("aspects")
        #             .upper()
        #             .split("-")
        #         )
        #     )
        # )

        return Bulletins(bulletins=[bulletin])


regions = {
    "PL-01": "karkonosze",
    "PL-02": "babia-gora",
    "PL-03": "bieszczady",
    # "PL-12": "Polish Tatras",
}
