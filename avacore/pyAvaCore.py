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
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

import avacore.processors
from avacore.avabulletin import AvaBulletin
from avacore.avabulletins import Bulletins

config = configparser.ConfigParser()
config.read_string(Path(f"{__file__}.ini").read_text(encoding="utf-8"))


def get_bulletins(region_id, *, date="", local="en") -> Bulletins:
    # pylint: disable=too-many-branches
    # pylint: disable=too-many-statements
    """
    returns Bulletins object for requested region_id and provider information
    """
    region_id = region_id.upper()
    processor = avacore.processors.new_processor(region_id)
    processor.url, provider = get_report_url(region_id, date=date,local=local)

    reports = processor.process_bulletin(region_id)
    reports.append_raw_data(processor.raw_data_format, processor.raw_data)
    reports.bulletins = [
        report
        for report in reports.bulletins
        if any(region.startswith(region_id) for region in report.get_region_list())
    ]
    reports.append_provider(provider, processor.url)
    return reports


def get_reports(region_id, local="en") -> Tuple[List[AvaBulletin], str, str]:
    """
    returns array of AvaReports for requested region_id and provider information
    """
    bulletins = get_bulletins(region_id=region_id, local=local)
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


def get_report_url(region_id, *, date="", local="") -> Tuple[str, str]:
    """
    returns the valid URL for requested region_id
    """
    url = get_config(region_id, "url.date" if date else f"url.{local}")
    if not url:
        url = get_config(region_id, "url")
    url = url.format(
        date=date or datetime.today().date(),
        local=local,
        region="{region}",
    )

    name = get_config(region_id, "name")
    return url, name
