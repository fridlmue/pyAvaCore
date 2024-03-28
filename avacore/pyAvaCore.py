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

import dataclasses
import datetime as dt
import json
from datetime import datetime
from pathlib import Path
from warnings import warn
from typing import Optional, List, Tuple, TypedDict

import avacore.processors
from avacore.avabulletin import AvaBulletin
from avacore.avabulletins import Bulletins


def get_bulletins(region_id, *, date="", lang="en") -> Bulletins:
    """
    returns Bulletins object for requested region_id and provider information
    """
    warn("Use BulletinProvider.get().download_bulletins() instead", DeprecationWarning)
    provider = BulletinProvider.get(region_id, date=date, lang=lang)
    return provider.download_bulletins()


def get_reports(region_id, lang="en") -> Tuple[List[AvaBulletin], str, str]:
    """
    returns array of AvaReports for requested region_id and provider information
    """
    warn("Use BulletinProvider.get().download_bulletins() instead", DeprecationWarning)
    bulletins = get_bulletins(region_id=region_id, lang=lang)
    provider = bulletins.customData["provider"]
    url = bulletins.customData["url"]
    return bulletins.bulletins, provider, url


@dataclasses.dataclass
class BulletinProvider:
    lang: str
    name: str
    region: str
    url: str
    website: str

    def download_bulletins(self) -> Bulletins:
        """
        Downloads, augments and returns requested Avalanche Bulletins
        """
        processor = avacore.processors.new_processor(self.region)
        processor.url = self.url
        reports = processor.process_bulletin(self.region)
        reports.append_raw_data(processor.raw_data_format, processor.raw_data)
        reports.bulletins = [
            report
            for report in reports.bulletins
            if any(
                region.startswith(self.region) for region in report.get_region_list()
            )
        ]
        reports.append_provider(self.name, self.website)
        reports.append_main_date()
        return reports

    @classmethod
    def get(cls, region_id, *, date="", lang="") -> "BulletinProvider":
        """
        returns the valid URL for requested region_id
        """
        if region_id == "IT-MeteoMont":
            region = ConfigRegion.of_config("IT-21")
            aws_name = "METEOMONT Carabinieri"
        elif region_id == "IT-Livigno":
            region = ConfigRegion.of_config("IT-25-SO-LI")
            aws_name = "ALPSOLUT"
        else:
            region = ConfigRegion.of_config(
                {"NO-3016": "NO", "PL-01": "PL"}.get(region_id, region_id)
            )
            aws_name = "AINEVA" if region_id.startswith("IT") else ""
        aws = region["aws"]
        if aws_name:
            aws = [a for a in aws if aws_name in a["name"]]
        if len(aws) != 1:
            raise ValueError()
        urls = aws[0]["url"]
        url = urls["api.date"] if date else urls.get(f"api.{lang}", urls["api"])
        url = url.format(
            date=date or datetime.today().date(),
            lang=lang,
            region="{region}",
        )
        website = urls.get(
            lang, next(url for (la, url) in urls.items() if len(la) == 2)
        )

        return BulletinProvider(
            lang=lang,
            name=aws[0]["name"],
            region=region_id,
            url=url,
            website=website,
        )


class ConfigURL(TypedDict):
    mail: Optional[str] = None
    en: Optional[str] = None
    de: Optional[str] = None
    api: str = ""
    # api:date
    api_date: Optional[str] = None


class ConfigAws(TypedDict):
    name: str
    url: ConfigURL


class ConfigRegion(TypedDict):
    id: str
    aws: List[ConfigAws]

    @classmethod
    def of_config(cls, region_id) -> "ConfigRegion":
        json_str = Path(f"{__file__}.json").read_text(encoding="utf-8")
        config: List["ConfigRegion"] = json.loads(json_str)
        return next(c for c in config if c["id"] == region_id)


def parse_dates(date_str: str) -> List[str]:
    """Parses a singleton date, a space separated list of dates or a date interval"""
    if not date_str:
        return [None]
    if "/" not in date_str:
        return date_str.split()
    # ISO 8601 interval
    [start_str, end_str] = date_str.split("/")
    start_date = dt.date.fromisoformat(start_str)
    end_date = dt.date.fromisoformat(end_str)
    dates: List[str] = []
    while start_date <= end_date:
        dates.append(start_date.isoformat())
        start_date += dt.timedelta(days=1)
    return dates
