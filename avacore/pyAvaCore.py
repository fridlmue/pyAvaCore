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
from urllib.parse import urlparse
from urllib.request import urlopen
from pathlib import Path
import xml.etree.ElementTree as ET
import json
import logging

from avacore.processor_fr import process_reports_fr, process_all_reports_fr
from avacore.processor_ch import process_reports_ch
from avacore.processor_catalunya import process_reports_cat
from avacore.processor_uk import process_reports_uk
from avacore.processor_cz import process_reports_cz
from avacore.processor_norway import process_reports_no, process_all_reports_no
from avacore.processor_es import process_reports_es
from avacore.processor_is import process_reports_is
from avacore.processor_caamlv5 import parse_xml, parse_xml_bavaria
from avacore.processor_ad import parse_xml as parse_xml_ad

config = configparser.ConfigParser()
config.read(f"{__file__}.ini")

### XML-Helpers


def get_xml_as_et(url):
    """
    returns the xml-file from url as ElementTree
    """

    with urlopen(url) as response:
        response_content = response.read()
    try:
        root = ET.fromstring(response_content.decode("utf-8"))
    except Exception as r_e:  # pylint: disable=broad-except
        print("error parsing ElementTree: " + str(r_e))
    return root


def get_reports(region_id, local="en", cache_path=str(Path("cache")), from_cache=False):
    # pylint: disable=too-many-branches
    """
    returns array of AvaReports for requested region_id and provider information
    """

    url = ""
    region_id = region_id.upper()
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
        if region_id == "NO":
            reports = process_all_reports_no()
        else:
            reports = process_reports_no(region_id)
        _, provider = get_report_url(region_id, local)
    elif region_id.startswith("GB"):
        reports = process_reports_uk()
        _, provider = get_report_url(region_id, local)
    elif region_id.startswith("IS"):
        reports = process_reports_is()
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
    elif region_id.startswith("AD"):
        logging.info('Fetching %s', url)
        url, provider = get_report_url(region_id, local)
        root = get_xml_as_et(url)
        reports = parse_xml_ad(root)
    else:
        url, provider = get_report_url(region_id, local)

        logging.info("Fetching %s", url)
        root = get_xml_as_et(url)

        if region_id.startswith("SI"):
            reports = parse_xml_bavaria(root, "slovenia")
        else:
            reports = parse_xml(root)

    relevant_reports = []

    for report in reports:
        found_one = False
        for region in report.get_region_list():
            if region.startswith(region_id):
                found_one = True
                break
        if found_one:
            relevant_reports.append(report)

    return relevant_reports, provider, url


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


class JSONEncoder(json.JSONEncoder):
    """JSON serialization of datetime"""

    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        try:
            return o.toJSON()
        except:  # pylint: disable=bare-except
            return o.__dict__
