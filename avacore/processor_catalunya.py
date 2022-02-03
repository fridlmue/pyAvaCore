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
import urllib.request
import datetime
from datetime import timedelta
import pytz
import dateutil.parser

from avacore import pyAvaCore
from avacore.avabulletin import AvaBulletin, DangerRatingType, AvalancheProblemType, RegionType

code_dir = {
    '1': 'ES-CT-L-04',
    '2': 'ES-CT-RF',
    '3': 'ES-CT-PA',
    '4': 'ES-CT-PP',
    '5': 'ES-CT-VN',
    '6': 'ES-CT-PR',
    '7': 'ES-CT-TF'
}

def process_reports_cat(today=datetime.datetime.today().date(), lang='es'):

    reports = []

    lang_dir = {
        'en': 3,
        'ca': 1,
        'es': 2
    }
    
    if lang not in lang_dir:
        lang = 'es'

    url = "https://bpa.icgc.cat/api/query?id=512&values="+str(today)+";"+str(lang_dir[lang])

    headers = {
        "Content-Type": "application/json; charset=utf-8"
        }

    req = urllib.request.Request(url, headers=headers)

    with urllib.request.urlopen(req) as response:
        content = response.read()

    icgc_reports = json.loads(content)
    
    reports = get_reports_fromjson(icgc_reports)
    
    return reports


def get_reports_fromjson(icgc_reports):
    reports = []
    report = AvaBulletin()

    for icgc_report in icgc_reports:
        region_id = code_dir[icgc_report['id_zona']]
        
        report = AvaBulletin()

        report.publicationTime = pytz.timezone("Europe/Madrid").localize(dateutil.parser.parse(icgc_report['databutlleti']))
        report.bulletinID = region_id + '_' + str(report.publicationTime)
        report.regions.append(RegionType(region_id)) # Region ID check with regions shape
        report.validTime.startTime = pytz.timezone("Europe/Madrid").localize(dateutil.parser.parse(icgc_report['datavalidesabutlleti']+'T00:00'))
        report.validTime.endTime = pytz.timezone("Europe/Madrid").localize(dateutil.parser.parse(icgc_report['datavalidesabutlleti']+'T23:59'))

        report.avalancheActivityHighlights = icgc_report['perill_text']
        report.avalancheActivityComment =  icgc_report['text_estat_mantell']
        report.snowpackStructureComment = icgc_report['text_distribucio']
        report.tendency.tendencyComment = icgc_report['text_tendencia']

        danger_rating = DangerRatingType()
        danger_rating.set_mainValue_int(int(icgc_report['grau_perill_primari']))
        report.dangerRatings.append(danger_rating)
        if not icgc_report['grau_perill_secundari'] == None:
            danger_rating_2 = DangerRatingType()
            danger_rating_2.set_mainValue_int(int(icgc_report['grau_perill_secundari']))
            report.dangerRatings.append(danger_rating_2)

        for problem in icgc_report['problems']:
            problem_type = ''
            if problem['id_tipus_situacio'] == '1':
                problem_type = 'new snow'
            elif problem['id_tipus_situacio'] == '2':
                problem_type = 'drifting snow'
            elif problem['id_tipus_situacio'] == '3':
                problem_type = 'old snow'
            elif problem['id_tipus_situacio'] == '4':
                problem_type = 'wet snow'
            elif problem['id_tipus_situacio'] == '5':
                problem_type = 'gliding snow'
            elif problem['id_tipus_situacio'] == '6':
                problem_type = 'favourable situation'
                
            problem = AvalancheProblemType()
            problem.add_problemType(problem_type)
            report.avalancheProblems.append(problem)

        reports.append(report)

    return reports
