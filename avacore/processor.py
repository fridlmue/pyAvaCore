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
import xml.etree.ElementTree as ET

from avacore.avabulletins import Bulletins


class Processor(ABC):
    local = "en"
    cache_path = str(Path("cache"))
    from_cache = False

    # def __init__(self) -> None:
    #     super().__init__()
    #     self.reports = Bulletins()

    @abstractmethod
    def process_bulletin(self, region_id: str) -> Bulletins:
        """
        Downloads and returns requested Avalanche Bulletins
        """


class JsonProcessor(Processor):
    @abstractmethod
    def parse_json(self, region_id: str, data: Any) -> Bulletins:
        """
        Builds the CAAML JSONs form the original JSON formats.
        """

    def parse_json_file(self, region_id: str, file: str) -> Bulletins:
        """
        Builds the CAAML JSONs form the original JSON read from given file.
        """
        data = json.loads(Path(file).read_text(encoding="utf-8"))
        return self.parse_json(region_id, data)

    def _fetch_json(self, url: str, headers) -> Any:
        req = urllib.request.Request(url, headers=headers)
        logging.info("Fetching %s", req.full_url)
        with urllib.request.urlopen(req) as response:
            content = response.read()
        # self.reports.append_raw_data("json", content.decode("utf-8"))
        return json.loads(content)


class XmlProcessor(Processor):
    @abstractmethod
    def parse_xml(self, region_id: str, root: ET.Element) -> Bulletins:
        """
        Builds the CAAML JSONs form the original XML formats.
        """

    def parse_xml_file(self, region_id: str, file: str) -> Bulletins:
        """
        Builds the CAAML JSONs form the original XML read from given file.
        """
        data = ET.fromstring(Path(file).read_text(encoding="utf-8"))
        return self.parse_xml(region_id, data)

    def _fetch_xml(self, url: str, headers) -> ET.Element:
        req = urllib.request.Request(url, headers=headers)
        logging.info("Fetching %s", req.full_url)
        with urllib.request.urlopen(req) as response:
            content = response.read().decode("utf-8")
        # self.reports.append_raw_data("xml", content)
        return ET.fromstring(content)
