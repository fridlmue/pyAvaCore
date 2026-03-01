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

import datetime
import logging
import re
import subprocess
import urllib.request
from io import BytesIO

from avacore.avabulletin import AvaBulletin, DangerRating, Region, Texts, ValidTime
from avacore.avabulletins import Bulletins
from avacore.processor import TextProcessor


class Processor(TextProcessor):
    regions = {
        "RO-1": "Rodnei",
        "RO-2": "Călimani-Bistriței",
        "RO-3": "Bucegi",
        "RO-4": "Făgăraș",
        "RO-5": "Parâng-Șureanu",
        "RO-6": "Țarcu-Godeanu",
        "RO-7": "Vlădeasa",
    }

    def process_bulletin(self, region_id) -> Bulletins:
        self._fetch_pdf()
        text = self._convert_to_text()
        return self.parse_text(region_id, text)

    def parse_text(self, region_id, text: str) -> Bulletins:
        matches = [
            datetime.datetime.strptime(s, "%d.%m.%Y ora %H")
            for s in re.findall(r"\d{2}\.\d{2}\.20\d{2} ora \d{2}", text)
        ]
        bulletins: list[AvaBulletin] = []
        for regionID, name in self.regions.items():
            t = re.search(name.upper() + r".*\n\nRISC (?P<mainValue>\d)", text)
            bulletin = AvaBulletin(
                avalancheActivity=Texts(comment=text),
                lang="ro",
                regions=[Region(regionID=regionID, name=name)],
                validTime=ValidTime(startTime=matches[0], endTime=matches[1]),
                dangerRatings=[
                    DangerRating().set_mainValue_int(int(t.group("mainValue")))
                ]
                if t
                else [],
            )
            bulletins.append(bulletin)
        return Bulletins(bulletins=bulletins)

    def _fetch_pdf(self) -> None:
        with urllib.request.urlopen(self.url) as response:
            logging.info("Fetching %s", self.url)
            data = response.read()
            self.raw_data = BytesIO(data)
            self.raw_data_format = "pdf"

    def _convert_to_text(self) -> str:
        p = subprocess.Popen(
            args=["pdftotext", "-", "-"],  # dnf install poppler-utils
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        logging.info("Running command %s", p.args)
        (output, *_) = p.communicate(input=self.raw_data.getvalue(), timeout=30)
        return output.decode("utf-8")
