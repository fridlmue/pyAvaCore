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

from avacore.avabulletin import AvaBulletin
from avacore.avabulletins import Bulletins
from avacore.processor import JsonProcessor

regions = {
    "RKRK": "PL-01",
    "RBBG": "PL-02",
    "RBSZ": "PL-03",
}


class Processor(JsonProcessor):
    """Processor for the GOPR avalanche bulletin API -- https://lawiny.gopr.pl/"""

    lang = "EN"

    def parse_json(self, region_id, data) -> Bulletins:
        bulletins = Bulletins()
        for report in data["bulletins"]:
            if report.get("lang") != self.lang:
                continue
            report_regions = [
                {"regionID": regions[r["regionId"]], "name": r.get("name")}
                for r in report.get("regions", [])
                if r.get("regionId") in regions
            ]
            if not report_regions or not report.get("validTime", {}).get("startTime"):
                continue
            tendency = report.get("tendency") or []
            if isinstance(tendency, dict):
                tendency = [tendency]
            bulletin = AvaBulletin.from_dict(
                {
                    "bulletinID": report.get("bulletinId"),
                    "lang": report["lang"].lower(),
                    "publicationTime": report["publicationTime"],
                    "validTime": {"startTime": report["validTime"]["startTime"]},
                    "regions": report_regions,
                    "dangerRatings": report.get("dangerRatings", []),
                    "avalancheProblems": report.get("avalancheProblems", []),
                    "tendency": tendency,
                    "source": report.get("source"),
                    "highlights": report.get("highlights"),
                    "avalancheActivity": report.get("avalancheActivity"),
                    "snowpackStructure": report.get("snowpackStructure"),
                    "travelAdvisory": report.get("travelAdvisory"),
                    "weatherForecast": report.get("weatherForecast"),
                    "weatherReview": report.get("weatherReview"),
                }
            )
            bulletin.validTime.endTime = bulletin.validTime.startTime + timedelta(
                days=1
            )
            bulletins.append(bulletin)

        return bulletins
