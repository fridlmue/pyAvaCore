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

import configparser
import dataclasses
import datetime as dt
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

import avacore.processors
from avacore.avabulletin import AvaBulletin
from avacore.avabulletins import Bulletins

config = configparser.ConfigParser()
config.read_string(Path(f"{__file__}.ini").read_text(encoding="utf-8"))


def get_bulletins(region_id, *, date="", lang="en") -> Bulletins:
    # pylint: disable=too-many-branches
    # pylint: disable=too-many-statements
    """
    returns Bulletins object for requested region_id and provider information
    """
    processor = avacore.processors.new_processor(region_id)
    provider = get_report_provider(region_id, date=date, lang=lang)
    processor.url = provider.url

    reports = processor.process_bulletin(region_id)
    reports.append_raw_data(processor.raw_data_format, processor.raw_data)
    reports.bulletins = [
        report
        for report in reports.bulletins
        if any(region.startswith(region_id) for region in report.get_region_list())
    ]
    reports.append_provider(provider.name, provider.website)
    return reports


def get_reports(region_id, lang="en") -> Tuple[List[AvaBulletin], str, str]:
    """
    returns array of AvaReports for requested region_id and provider information
    """
    bulletins = get_bulletins(region_id=region_id, lang=lang)
    provider = bulletins.customData["provider"]
    url = bulletins.customData["url"]
    return bulletins.bulletins, provider, url


def get_config(region_id: str, option: str, fallback="") -> str:
    """
    returns the requested option for the requested region_id
    """
    while (
        not config.has_section(region_id)
        and not config.has_option(region_id, option)
        and "-" in region_id
    ):
        region_id = region_id[0 : region_id.rindex("-")]
    return config.get(region_id, option, fallback=fallback)


@dataclasses.dataclass
class BulletinProvider:
    lang: str
    name: str
    region: str
    url: str
    website: str


def get_report_provider(region_id, *, date="", lang="") -> BulletinProvider:
    """
    returns the valid URL for requested region_id
    """
    url = get_config(region_id, "url.date" if date else f"url.{lang}")
    if not url:
        url = get_config(region_id, "url")
    url = url.format(
        date=date or datetime.today().date(),
        lang=lang,
        region="{region}",
    )

    return BulletinProvider(
        lang=lang,
        name=get_config(region_id, "name"),
        region=region_id,
        url=url,
        website=get_config(region_id, "website"),
    )


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
