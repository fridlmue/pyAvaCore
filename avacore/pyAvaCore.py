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
from typing import List, Tuple
from urllib.parse import urlparse
from urllib.request import urlopen
from pathlib import Path
import xml.etree.ElementTree as ET
import logging

from avacore.avabulletin import AvaBulletin
from avacore.avabulletins import Bulletins

from avacore.processor_fr import process_reports_fr, process_all_reports_fr
from avacore.processor_ch import process_reports_ch
from avacore.processor_catalunya import process_reports_cat
from avacore.processor_uk import process_reports_uk
from avacore.processor_cz import process_reports_cz
# from avacore.processor_norway import process_reports_no, process_all_reports_no
from avacore.processor_es import process_reports_es
from avacore.processor_is import process_reports_is
from avacore.processor_caamlv5 import parse_xml, parse_xml_bavaria
from avacore.processor_ad import parse_xml_ad
from avacore.processor_sk import process_reports_sk

import avacore.processor_norway

config = configparser.ConfigParser()
config.read(f"{__file__}.ini")


def get_bulletins(
    region_id,
    local="en",
    cache_path=str(Path("cache")),
    from_cache=False,
) -> Bulletins:
    # pylint: disable=too-many-branches
    # pylint: disable=too-many-statements
    """
    returns Bulletins object for requested region_id and provider information
    """

    url = ""
    region_id = region_id.upper()
    reports: Bulletins
    if region_id.startswith("FR"):
        if region_id == "FR":
            reports = process_all_reports_fr()
        else:
            reports = process_reports_fr(region_id)
        _, provider = get_report_url(region_id, local)
    elif region_id.startswith("CH"):
        reports = process_reports_ch(lang=local, path=cache_path, cached=from_cache)
        url, provider = get_report_url(region_id, local)
    elif region_id.startswith("NO"):
        processor = avacore.processor_norway.Processor()
        reports = processor.process_bulletin(region_id)
        _, provider = get_report_url(region_id, local)
    elif region_id.startswith("GB"):
        reports = process_reports_uk()
        _, provider = get_report_url(region_id, local)
    elif region_id.startswith("IS"):
        reports = process_reports_is(local)
        _, provider = get_report_url(region_id, local)
    elif region_id.startswith("CZ"):
        reports = process_reports_cz()
        _, provider = get_report_url(region_id, local)
    elif region_id.startswith("ES") and not region_id.startswith("ES-CT"):
        reports = process_reports_es()
        url, provider = get_report_url(region_id, local)
    elif (
        region_id.startswith("ES-CT")
        and not region_id.startswith("ES-CT-L")
        or region_id.startswith("ES-CT-L-04")
    ):
        reports = process_reports_cat()
        _, provider = get_report_url(region_id, local)
    elif region_id.startswith("SK"):
        logging.info("Fetching %s", url)
        url, provider = get_report_url(region_id, local)
        reports = process_reports_sk()
    else:
        url, provider = get_report_url(region_id, local)

        logging.info("Fetching %s", url)
        with urlopen(url) as response:
            content = response.read().decode("utf-8")
        try:
            root = ET.fromstring(content)
        except Exception as r_e:  # pylint: disable=broad-except
            print("error parsing ElementTree: " + str(r_e))

        if region_id.startswith("SI"):
            reports = parse_xml_bavaria(root, "slovenia")
        elif region_id.startswith("AD"):
            reports = parse_xml_ad(root)
        else:
            reports = parse_xml(root)
        reports.append_raw_data("xml", content)

    reports.bulletins = [
        report
        for report in reports.bulletins
        if any(region.startswith(region_id) for region in report.get_region_list())
    ]
    reports.append_provider(provider, url)
    return reports


def get_reports(
    region_id,
    local="en",
    cache_path=str(Path("cache")),
    from_cache=False,
) -> Tuple[List[AvaBulletin], str, str]:
    """
    returns array of AvaReports for requested region_id and provider information
    """
    bulletins = get_bulletins(
        region_id=region_id,
        local=local,
        cache_path=cache_path,
        from_cache=from_cache,
    )
    provider = bulletins.customData["provider"]
    url = bulletins.customData["url"]
    return bulletins.bulletins, provider, url


def get_report_url(region_id, local=""):
    """
    returns the valid URL for requested region_id
    """

    region_id_prefix = region_id
    while not region_id_prefix in config.keys():
        if region_id_prefix.startswith("SI"):
            region_id_prefix = "SI"
        else:
            region_id_prefix = "-".join(region_id_prefix.split("-")[:-1])

    name = config[region_id_prefix]["name"]
    url = config[region_id_prefix]["url"]
    if f"url.{local}" in config[region_id_prefix]:
        url = config[region_id_prefix][f"url.{local}"]
    netloc = urlparse(url).netloc
    if local.upper() == "DE":
        provider = f"Die dargestellten Informationen werden bereitgestellt von: {name}. ({netloc})"
    else:
        provider = f"The displayed information is provided by: {name}. ({netloc})"
    return url, provider
