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
import re


from avacore.avabulletin import (
    AvaBulletin,
    DangerRating,
    AvalancheProblem,
    Elevation,
    Region,
)
from avacore.avabulletins import Bulletins
from avacore.processor import Processor as AbstractProcessor


class Processor(AbstractProcessor):
    def process_bulletin(self, region_id) -> Bulletins:
        html = self._fetch_url(self.url, {})
        self.raw_data = html
        self.raw_data_format = "html"
        return self.parse_html(region_id, html)

    def parse_html(self, region_id, html: str) -> Bulletins:
        bulletin = AvaBulletin()
        bulletin.regions = [Region(regionID=region_id, name="Livigno")]
        time = re.search(
            r'<div class="dataBollettino">.*?(?P<day>\d+)<sup>th</sup>.*(?P<month>[A-Z]{3}) (?P<year>\d+)</div>',
            html,
        )
        bulletin.validTime.startTime = datetime(
            year=int(time.group("year")),
            month=[
                datetime(2000, month, 1).strftime("%b").upper()
                for month in range(1, 13)
            ].index(time.group("month"))+1,
            day=int(time.group("day")),
        )
        delta = timedelta(days=1, seconds=-1)
        bulletin.validTime.endTime = bulletin.validTime.startTime + delta
        for (match, elevation) in zip(
            re.finditer(r'data-valore="(?P<rating>\d)"', html),
            (
                # alpine
                Elevation(lowerBound="treeline"),
                # treeline
                Elevation(lowerBound="treeline", upperBound="treeline"),
                # below treeline
                Elevation(upperBound="treeline"),
            ),
        ):
            rating_int = int(match.group("rating"))
            rating = DangerRating().set_mainValue_int(rating_int)
            rating.elevation = elevation
            bulletin.dangerRatings.append(rating)
        for match in re.finditer(r"MAIN PROBLEM \d: (?P<problem>[^<]+)", html):
            problem = AvalancheProblem().add_problemType(match.group("problem").lower())
            # FIXME: parse altitude, altitude, exposure, likelihood, av. size, trend
            bulletin.avalancheProblems.append(problem)
        return Bulletins(bulletins=[bulletin])
