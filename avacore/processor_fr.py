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
from datetime import datetime
from urllib.request import urlopen, Request
import logging
import re
import string
import typing
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo


from avacore.avabulletin import (
    AvaBulletin,
    DangerRating,
    Region,
    Texts,
)
from avacore.avabulletins import Bulletins
from avacore.processor import XmlProcessor


class Processor(XmlProcessor):
    def _fetch_url(self, url, headers) -> str:
        with urlopen("https://meteofrance.com/") as response:
            session_cookie_raw = response.getheader("Set-Cookie")
        session_cookie = re.sub("mfsession=", "", session_cookie_raw.split(";")[0])

        access_token = ""
        shift_by = 13
        for c in session_cookie:
            if c.isdigit() or c in string.punctuation:
                access_token += c
            else:
                c_a = "A" if c.isupper() else "a"
                index = ord(c) - ord(c_a)
                access_token += chr(ord(c_a) + (index + shift_by) % 26)

        req = Request(url, headers=headers)
        req.add_header("Authorization", "Bearer " + access_token)
        logging.info("Fetching %s", req.full_url)
        with urlopen(req) as response_content:
            return response_content.read().decode("utf-8")

    def process_bulletin(self, region_id: str) -> Bulletins:
        if region_id == "FR":
            return self.process_all_reports_fr()
        url = self.url.format(region=region_id.removeprefix("FR-"))
        root = self._fetch_xml(url, {})
        return self.parse_xml(region_id, root)

    def process_all_reports_fr(self) -> Bulletins:
        """
        Downloads and returns all Reports for FR (iterating threw region IDs)
        """
        all_reports = Bulletins()
        all_raw_data = []
        for region in fr_regions:
            for report in self.process_bulletin(region).bulletins:
                all_reports.append(report)
            all_raw_data.append(
                self.raw_data.removeprefix("""<?xml version="1.0" encoding="utf-8"?>""")
                .strip()
                .removeprefix(
                    """<?xml-stylesheet type="text/xsl" href="../web/bra.xslt"?>"""
                )
                .strip()
            )
        raw_data = "\\n".join(all_raw_data)
        self.raw_data = f"<ROOT>{raw_data}</ROOT>"
        return all_reports

    def parse_xml(self, region_id, root: ET.ElementTree) -> Bulletins:
        """
        Process XML file for a region
        """
        for bulletins in root.iter(tag="BULLETINS_NEIGE_AVALANCHE"):
            root = bulletins

        report = AvaBulletin()
        reports = Bulletins()

        tzinfo = ZoneInfo("Europe/Paris")
        report.regions.append(Region("FR-" + root.attrib.get("ID").zfill(2)))
        report.publicationTime = datetime.fromisoformat(
            root.attrib.get("DATEBULLETIN")
        ).replace(tzinfo=tzinfo)
        report.validTime.startTime = datetime.fromisoformat(
            root.attrib.get("DATEBULLETIN")
        ).replace(tzinfo=tzinfo)
        report.validTime.endTime = datetime.fromisoformat(
            root.attrib.get("DATEVALIDITE")
        ).replace(tzinfo=tzinfo)

        am_danger_ratings: typing.List[DangerRating] = []

        for cartoucherisque in root.iter(tag="CARTOUCHERISQUE"):
            aspects = []
            danger_rating_pre = DangerRating(aspects=aspects)
            for pente in cartoucherisque.iter(tag="PENTE"):
                if pente.get("N") == "true":
                    aspects.append("N")
                if pente.get("NE") == "true":
                    aspects.append("NE")
                if pente.get("E") == "true":
                    aspects.append("E")
                if pente.get("SE") == "true":
                    aspects.append("SE")
                if pente.get("S") == "true":
                    aspects.append("S")
                if pente.get("SW") == "true":
                    aspects.append("SW")
                if pente.get("W") == "true":
                    aspects.append("W")
                if pente.get("NW") == "true":
                    aspects.append("NW")

            report.customData = {
                "MeteoFrance": {"avalancheProneLocation": {"aspects": aspects}}
            }

            for risque in cartoucherisque.iter(tag="RISQUE"):
                danger_rating = DangerRating(aspects=danger_rating_pre.aspects)
                danger_rating.set_mainValue_int(int(risque.attrib.get("RISQUE1")))
                danger_rating.elevation.auto_select(risque.attrib.get("LOC1"))
                am_danger_ratings.append(danger_rating)
                if not risque.attrib.get("RISQUE2") == "":
                    danger_rating2 = DangerRating(aspects=danger_rating_pre.aspects)
                    danger_rating2.set_mainValue_int(int(risque.attrib.get("RISQUE2")))
                    danger_rating2.elevation.auto_select(risque.attrib.get("LOC2"))
                    am_danger_ratings.append(danger_rating2)

            for resume in cartoucherisque.iter(tag="RESUME"):
                report.avalancheActivity = Texts(highlights=resume.text)

        for stabilite in root.iter(tag="STABILITE"):
            for texte in stabilite.iter(tag="TEXTE"):
                report.avalancheActivity = Texts(comment=texte.text)

        for qualite in root.iter(tag="QUALITE"):
            for texte in qualite.iter(tag="TEXTE"):
                report.snowpackStructure = Texts(comment=texte.text)

        pm_danger_ratings: typing.List[DangerRating] = []
        pm_available = False

        for cartoucherisque in root.iter(tag="CARTOUCHERISQUE"):
            danger_rating_pre = DangerRating()
            aspects = []
            for pente in cartoucherisque.iter(tag="PENTE"):
                if pente.get("N") == "true":
                    aspects.append("N")
                if pente.get("NE") == "true":
                    aspects.append("NE")
                if pente.get("E") == "true":
                    aspects.append("E")
                if pente.get("SE") == "true":
                    aspects.append("SE")
                if pente.get("S") == "true":
                    aspects.append("S")
                if pente.get("SW") == "true":
                    aspects.append("SW")
                if pente.get("W") == "true":
                    aspects.append("W")
                if pente.get("NW") == "true":
                    aspects.append("NW")

            report.customData = {
                "MeteoFrance": {"avalancheProneLocation": {"aspects": aspects}}
            }

            for risque in cartoucherisque.iter(tag="RISQUE"):
                if not risque.attrib.get("EVOLURISQUE1") == "":
                    pm_available = True
                    danger_rating_pm = DangerRating(aspects=danger_rating_pre.aspects)
                    danger_rating_pm.set_mainValue_int(
                        int(risque.attrib.get("EVOLURISQUE1"))
                    )
                    danger_rating_pm.elevation.auto_select(risque.attrib.get("LOC1"))
                    pm_danger_ratings.append(danger_rating_pm)
                else:
                    pm_danger_ratings.append(am_danger_ratings[0])
                if not risque.attrib.get("EVOLURISQUE2") == "":
                    pm_available = True
                    danger_rating_pm2 = DangerRating(aspects=danger_rating_pre.aspects)
                    danger_rating_pm2.set_mainValue_int(
                        int(risque.attrib.get("EVOLURISQUE2"))
                    )
                    danger_rating_pm2.elevation.auto_select(risque.attrib.get("LOC2"))
                    pm_danger_ratings.append(danger_rating_pm2)
                elif len(am_danger_ratings) > 1:
                    pm_danger_ratings.append(am_danger_ratings[1])

        report.bulletinID = (
            report.regions[0].regionID + "_" + str(report.publicationTime.isoformat())
        )

        for dangerRating in am_danger_ratings:
            if pm_available:
                validTimePeriod = "earlier"
            else:
                validTimePeriod = "all_day"
            dangerRating.validTimePeriod = validTimePeriod
            report.dangerRatings.append(dangerRating)

        if pm_available:
            for dangerRating in pm_danger_ratings:
                validTimePeriod = "later"
                dangerRating.validTimePeriod = validTimePeriod
                report.dangerRatings.append(dangerRating)

        reports.append(report)

        return reports


fr_regions = [
    "FR-01",
    "FR-02",
    "FR-03",
    "FR-04",
    "FR-05",
    "FR-06",
    "FR-09",
    "FR-10",
    "FR-11",
    "FR-07",
    "FR-08",
    "FR-12",
    "FR-14",
    "FR-15",
    "FR-13",
    "FR-16",
    "FR-17",
    "FR-18",
    "FR-19",
    "FR-20",
    "FR-21",
    "FR-22",
    "FR-23",
    "FR-64",
    "FR-65",
    "FR-66",
    "FR-67",
    "FR-68",
    "FR-69",
    "FR-70",
    "FR-72",
    "FR-71",
    "FR-73",
    "FR-74",
    "FR-40",
    "FR-41",
]
