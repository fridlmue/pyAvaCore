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

from datetime import timedelta
import urllib.request
import re
import copy

import pytz
import dateutil.parser

from avacore.avabulletin import (
    AvaBulletin,
    DangerRating,
    Region,
    Texts,
)

code_dir = {
    "SOBRARBE": "ES-SO",
    "RIBAGORZA": "ES-RI",
    "JACETANIA": "ES-JA",
    "GÁLLEGO": "ES-GA",
    "NAVARRA": "ES-NA",
}


class LocaleParserInfo(dateutil.parser.parserinfo):
    """
    Provide local parser info for ES
    https://stackoverflow.com/questions/19927654/using-dateutil-parser-to-parse-a-date-in-another-language/62581811#62581811
    """

    WEEKDAYS = [
        ("Mon", "Monday"),
        ("Tue", "Tuesday"),
        ("Wed", "Wednesday"),
        ("Thu", "Thursday"),
        ("Fri", "Friday"),
        ("Sat", "Saturday"),
        ("Sun", "Sunday"),
    ]
    MONTHS = [
        ("ene", "enero"),
        ("feb", "febrero"),
        ("mar", "marzo"),
        ("abr", "abril"),
        ("may", "mayo"),
        ("jun", "junio"),
        ("jul", "julio"),
        ("ago", "agosto"),
        ("sep", "septiembre"),
        ("oct", "octubre"),
        ("nov", "noviembre"),
        ("dic", "diciembre"),
    ]


def process_reports_es():
    """
    Downloads and returns requested Avalanche Bulletins
    """
    url = "http://www.aemet.es/xml/montana/p18tarn1.xml"

    req = urllib.request.Request(url)

    with urllib.request.urlopen(req) as response:
        bulletin_raw = response.read()

    reports = get_reports_from_file(bulletin_raw.decode("ISO-8859-1"))

    return reports


def get_reports_from_file(aemet_reports):
    # pylint: disable=too-many-statements
    # pylint: disable=too-many-branches
    # pylint: disable=too-many-locals
    """
    Processes downloaded report from file
    """
    reports = []
    report = AvaBulletin()

    re_result = re.search(r"(?<=Día)(.*)(?=hora oficial)", aemet_reports)

    t_spain = dateutil.parser.parse(
        re_result.group(0)[1:-1], fuzzy=True, parserinfo=LocaleParserInfo()
    )
    report.publicationTime = pytz.timezone("Europe/Madrid").localize(t_spain)
    report.validTime.startTime = report.publicationTime
    report.validTime.endTime = report.publicationTime + timedelta(hours=24)
    t_spain = dateutil.parser.parse(re_result.group(0)[1:-1], fuzzy=True)
    t_spain = pytz.timezone("Europe/Madrid").localize(t_spain)

    re_result = re.search(
        r"(?<=2\.- Estado del manto y observaciones recientes:)(?s:.*)(?=3\.- Evolución del manto)",
        aemet_reports,
    )
    report.snowpackStructure = Texts(
        comment=" ".join(re_result.group(0).splitlines()[1:])
    )

    re_result = re.search(
        r"(?<=3\.- Evolución del manto y peligro)(?s:.*)(?=4.- Predicción meteorológica)",
        aemet_reports,
    )
    report.avalancheActivity = Texts(
        comment=" ".join(re_result.group(0).splitlines()[2:])
    )

    re_result = re.search(
        r"(?<=4\.- Predicción meteorológica)(?s:.*)(?=5\.- Avance para)", aemet_reports
    )
    report.wxSynopsis = Texts(comment=" ".join(re_result.group(0).splitlines()[1:]))

    re_result = re.search(
        r"(?<=5\.- Avance para el)(?s:.*)(?=</TXT_PREDICCION>)", aemet_reports
    )
    report.tendency.tendencyComment = " ".join(re_result.group(0).splitlines()[1:])

    re_result = re.search(
        r"(?<=1\.- Estimación del nivel de peligro:)(?s:.*)(?=2\.- Estado del manto y observaciones recientes)",
        aemet_reports,
    )
    levels = re_result.group(0).splitlines()

    last_region = ""
    region_lines = {}
    for line in levels:
        if len(line) > 2:
            if ":" in line:
                content = line.split(":")
                region_lines[content[0]] = content[1].strip()
                last_region = content[0]
            else:
                region_lines[last_region] = region_lines[last_region] + " " + line

    for elem, item in region_lines.items():
        current_report = copy.deepcopy(report)
        current_report.regions.append(Region(code_dir[elem.upper()]))
        current_report.bulletinID = (
            current_report.regions[0].regionId + "_" + str(report.publicationTime)
        )
        sentences = item.split(".")
        pm_ratings_hi = 0
        pm_ratings_lw = 0
        pm_ge = 0
        pm = False
        for sentence in sentences:
            pm_sent = False
            if len(sentence) > 1:
                danger_rating = DangerRating()
                danger_rating2 = None
                levels = re.findall(r"\((.)\)", sentence)
                if len(levels) > 1 and ("evolucionando" in sentence):
                    pm_sent = True
                    pm = True
                if "pordebajo" in sentence.replace(" ", ""):
                    danger_rating.elevation.upperBound = re.findall(
                        r"(\d+) m", sentence
                    )[0]
                    if pm_sent:
                        pm_ratings_lw = int(levels[1])
                    if "porencima" in sentence.replace(" ", ""):
                        danger_rating2 = DangerRating()
                        danger_rating2.elevation.lowerBound = re.findall(
                            r"(\d+) m", sentence
                        )[0]
                elif "porencima" in sentence.replace(" ", ""):
                    danger_rating.elevation.lowerBound = re.findall(
                        r"(\d+) m", sentence
                    )[0]
                    if pm_sent:
                        pm_ratings_hi = int(levels[1])
                elif pm:
                    pm_ge = int(levels[1])
                danger_rating.set_mainValue_int(int(levels[0]))
                current_report.dangerRatings.append(danger_rating)

                if danger_rating2 is not None:
                    danger_rating2.set_mainValue_int(int(levels[1]))
                    current_report.dangerRatings.append(danger_rating2)

        if pm:
            pm_report = copy.deepcopy(current_report)
            pm_report.bulletinID = current_report.bulletinID + "_PM"
            current_report.validTime.endTime = current_report.validTime.endTime.replace(
                hour=12, minute=0
            )
            pm_report.validTime.startTime = current_report.validTime.endTime

            rating_set = False

            for danger_rating in pm_report.dangerRatings:
                if (
                    hasattr(danger_rating.elevation, "upperBound")
                    and pm_ratings_lw != 0
                ):
                    danger_rating.set_mainValue_int(pm_ratings_lw)
                    rating_set = True
                if (
                    hasattr(danger_rating.elevation, "lowerBound")
                    and pm_ratings_hi != 0
                ):
                    danger_rating.set_mainValue_int(pm_ratings_hi)
                    rating_set = True

            if not rating_set:
                pm_report.dangerRatings[0].set_mainValue_int(pm_ge)

            reports.append(pm_report)

        reports.append(current_report)

    return reports
