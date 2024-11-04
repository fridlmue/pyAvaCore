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

import datetime as dt
import logging
import re
import shutil
import subprocess
import urllib
from io import BytesIO

from avacore.avabulletin import AvaBulletin, DangerRating, Region, ValidTime
from avacore.avabulletins import Bulletins
from avacore.processor import Processor as AbstractProcessor
from avacore.png import png


# https://cdn.fmi.fi/apps/avalanche-forecast/show-map.php?lang=en
# https://api.ocr.space/parse/imageurl?apikey=K81943660188957&url=https://cdn.fmi.fi/apps/avalanche-forecast/show-map.php
class Processor(AbstractProcessor):
    today: dt.datetime

    def _fetch_files(self):
        with urllib.request.urlopen(self.url) as response:
            logging.info("Fetching %s", self.url)
            data = response.read()
            self.raw_data = BytesIO(data)
            self.raw_data_format = "png"
        self.today = dt.datetime.today()
        self._ocr_today()

    def _ocr_today(self):
        if not shutil.which("tesseract"):
            return
        process = subprocess.Popen(
            ["tesseract", "-", "-"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        out_bytes, _ = process.communicate(self.raw_data.getvalue(), timeout=7)
        output = out_bytes.decode(encoding="utf-8")
        match = re.search(r"Updated (\d+.\d+.\d+ \d+:\d+)", output)
        if not match:
            return
        self.today = dt.datetime.strptime(match.group(1), "%d.%m.%Y %H:%M")
        logging.info("Obtained %s using OCR tesseract", self.today.isoformat())

    def process_bulletin(self, region_id: str) -> Bulletins:
        if not isinstance(self.raw_data, BytesIO):
            self._fetch_files()

        png_data = png.Reader(bytes=self.raw_data.getvalue())
        _, _, px, _ = png_data.read()
        px_list = list(px)
        bulletins = Bulletins()
        for [region_id, region_name, x, y] in fi_regions:
            bulletin = AvaBulletin()
            bulletin.publicationTime = self.today
            tomorrow = self.today + dt.timedelta(days=1)
            bulletin.validTime = ValidTime(
                startTime=dt.datetime.combine(tomorrow, dt.time(0, 0, 0)),
                endTime=dt.datetime.combine(tomorrow, dt.time(23, 59, 59)),
            )
            bulletin.regions.append(Region(region_id, region_name))
            color = px_list[y][3 * x : 3 * x + 3]
            if color == b"\xba\xd3\x7c":
                bulletin.dangerRatings.append(DangerRating("low"))
            elif color == b"\xff\xff\x00":
                bulletin.dangerRatings.append(DangerRating("moderate"))
            elif color == b"\xfe\x98\x00":
                bulletin.dangerRatings.append(DangerRating("considerable"))
            elif color == b"\xfe\x00\x00":
                bulletin.dangerRatings.append(DangerRating("high"))
            bulletins.append(bulletin)
        return bulletins


fi_regions = [
    ["FI-01", "Kilpisjärvi", 210, 390],
    ["FI-02", "Saariselkä", 640, 446],
    ["FI-03", "Ounas-Pallas", 440, 570],
    ["FI-04", "Ylläs-Levi", 513, 705],
    ["FI-05", "Luosto-Pyhä", 740, 705],
    ["FI-06", "Ruka", 816, 913],
]
