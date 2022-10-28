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

from abc import ABC, abstractmethod
import json
import logging
from typing import Any
import urllib.request
from pathlib import Path

from avacore.avabulletins import Bulletins
import avacore.processor_norway


class Processor(ABC):
    local = "en"
    cache_path = str(Path("cache"))
    from_cache = False

    # def __init__(self) -> None:
    #     super().__init__()
    #     self.reports = Bulletins()

    @abstractmethod
    def process_bulletin(self, region_id: str) -> Bulletins:
        pass

    def _fetch_json(self, url: str, headers) -> Any:
        req = urllib.request.Request(url, headers=headers)
        logging.info("Fetching %s", req.full_url)
        with urllib.request.urlopen(req) as response:
            content = response.read()
        # self.reports.append_raw_data("json", content.decode("utf-8"))
        return json.loads(content)


def new_processor(region: str) -> Processor:
    if region == "NO":
        return avacore.processor_norway.Processor()
    return None
