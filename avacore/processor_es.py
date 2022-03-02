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

import json
import datetime
from datetime import timedelta
from datetime import datetime
import urllib.request
import pytz
import dateutil.parser
import re
import copy
import calendar
import locale

from avacore import pyAvaCore
from avacore.avabulletin import AvaBulletin, DangerRatingType, AvalancheProblemType, RegionType

code_dir = {
    'SOBRARBE' : 'ES-SO',
    'RIBAGORZA': 'ES-RI',
    'JACETANIA': 'ES-JA',
    'GÁLLEGO'  : 'ES-GA',
    'NAVARRA'  : 'ES-NA'
}

# https://stackoverflow.com/questions/19927654/using-dateutil-parser-to-parse-a-date-in-another-language/62581811#62581811
class LocaleParserInfo(dateutil.parser.parserinfo):
    locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
    WEEKDAYS = zip(calendar.day_abbr, calendar.day_name)
    MONTHS = list(zip(calendar.month_abbr, calendar.month_name))[1:]
    locale.setlocale(locale.LC_ALL, locale.getdefaultlocale())

def process_reports_es(today=datetime.today().date(), lang='es'):
    url = 'http://www.aemet.es/xml/montana/p18tarn1.xml'

    req = urllib.request.Request(url)

    with urllib.request.urlopen(req) as response:
        bulletin_raw = response.read()

    reports = get_reports_from_file(bulletin_raw.decode("ISO-8859-1"))

    return reports

def get_reports_from_file(aemet_reports):
    reports = []
    report = AvaBulletin()

    re_result = re.search('(?<=Día)(.*)(?=hora oficial)', aemet_reports)

    t_spain = dateutil.parser.parse(re_result.group(0)[1:-1], fuzzy=True, parserinfo=LocaleParserInfo())
    report.publicationTime = pytz.timezone("Europe/Madrid").localize(t_spain)
    report.validTime.startTime = report.publicationTime
    report.validTime.endTime = report.publicationTime + timedelta(hours=24)
    t_spain = dateutil.parser.parse(re_result.group(0)[1:-1], fuzzy=True)
    t_spain = pytz.timezone("Europe/Madrid").localize(t_spain)

    re_result = re.search('(?<=2\.- Estado del manto y observaciones recientes:)(?s:.*)(?=3\.- Evolución del manto)', aemet_reports)
    report.snowpackStructureComment = ' '.join(re_result.group(0).splitlines()[1:])

    re_result = re.search('(?<=3\.- Evolución del manto y peligro)(?s:.*)(?=4.- Predicción meteorológica)', aemet_reports)
    report.avalancheActivityComment = ' '.join(re_result.group(0).splitlines()[2:])

    re_result = re.search('(?<=4\.- Predicción meteorológica)(?s:.*)(?=5\.- Avance para)', aemet_reports)
    report.wxSynopsisComment = ' '.join(re_result.group(0).splitlines()[1:])

    re_result = re.search('(?<=5\.- Avance para el)(?s:.*)(?=</TXT_PREDICCION>)', aemet_reports)
    report.tendency.tendencyComment = ' '.join(re_result.group(0).splitlines()[1:])

    re_result = re.search('(?<=1\.- Estimación del nivel de peligro:)(?s:.*)(?=2\.- Estado del manto y observaciones recientes)', aemet_reports)
    levels = re_result.group(0).splitlines()

    last_region = ''
    region_lines = {}
    for line in levels:
        if len(line) > 2:
            if ':' in line:
                content = line.split(':')
                region_lines[content[0]] = content[1].strip()
                last_region = content[0]
            else:
                region_lines[last_region] = region_lines[last_region] + line

    for elem in region_lines:
        current_report = copy.deepcopy(report)
        current_report.regions.append(RegionType(code_dir[elem.upper()]))
        current_report.bulletinID = current_report.regions[0].regionID + '_' + str(report.publicationTime)
        sentences = region_lines[elem].split('.')
        pm_ratings_hi = 0
        pm_ratings_lw = 0
        pm_ge = 0
        pm = False
        for sentence in sentences:
            pm_sent = False
            if len(sentence) > 1:
                danger_rating = DangerRatingType()
                danger_rating2 = None
                levels = re.findall(r"\((.)\)", sentence)
                if len(levels) > 1 and not (('por debajo' in sentence) and ('por encima' in sentence)):
                    pm_sent = True
                    pm = True
                if 'por debajo' in sentence:
                    danger_rating.elevation.upperBound = re.findall(r"(\d+) m", sentence)[0]
                    if pm_sent:
                        pm_ratings_lw = int(levels[1])
                    if 'por encima' in sentence:
                        danger_rating2 = DangerRatingType()
                        danger_rating2.elevation.lowerBound = re.findall(r"(\d+) m", sentence)[0]
                        '''
                        if pm_sent:
                            pm_ratings_hi = int(levels[1])
                        '''
                elif 'por encimade' in sentence:
                    danger_rating.elevation.lowerBound = re.findall(r"(\d+) m", sentence)[0]
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
            pm_report.bulletinID = current_report.bulletinID + '_PM'
            current_report.validTime.endTime = current_report.validTime.endTime.replace(hour=12, minute=0)
            pm_report.validTime.startTime = current_report.validTime.endTime

            set = False

            for danger_rating in pm_report.dangerRatings:
                if hasattr(danger_rating.elevation, 'upperBound') and pm_ratings_lw != 0:
                    danger_rating.set_mainValue_int(pm_ratings_lw)
                    set = True
                if hasattr(danger_rating.elevation, 'lowerBound') and pm_ratings_hi != 0:
                    danger_rating.set_mainValue_int(pm_ratings_hi)
                    set = True

            if not set:
                pm_report.dangerRatings[0].set_mainValue_int(pm_ge)

            reports.append(pm_report)

        reports.append(current_report)

    return reports
