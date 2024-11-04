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

from avacore.avabulletins import Bulletins
from avacore.processor import JsonProcessor


class Processor(JsonProcessor):
    """Processor for CAAMLv6 JSON -- http://caaml.org/Schemas/BulletinEAWS/ -- http://caaml.org/Schemas/BulletinEAWS/v6.0/json/CAAMLv6_BulletinEAWS.json"""

    def parse_json(self, region_id, root) -> Bulletins:
        return Bulletins.from_dict(root)


class Processor2022(Processor):
    """Processor for intermediate CAAML format"""

    def parse_json(self, region_id, root) -> Bulletins:
        for b in root["bulletins"]:
            if "wxSynopsis" in b and isinstance(b["wxSynopsis"], dict):
                b["weatherForecast"] = b["wxSynopsis"]
            if "tendency" in b and isinstance(b["tendency"], dict):
                b["tendency"] = [b["tendency"]]
            if "avalancheProblems" in b and isinstance(b["avalancheProblems"], list):
                for p in b["avalancheProblems"]:
                    if "terrainFeature" in p:
                        p["comment"] = p["terrainFeature"]
        return super().parse_json(region_id, root)
