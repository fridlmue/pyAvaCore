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
from datetime import datetime
from datetime import timedelta
from datetime import time
import pytz
import dateutil.parser
import logging


from avacore.avabulletin import AvaBulletin, DangerRating, AvalancheProblem, Elevation, Region, Texts

def process_reports_cz():
    url = "https://www.horskasluzba.cz/cz/avalanche-json"

    headers = {
        "Content-Type": "application/json; charset=utf-8"
        }

    req = urllib.request.Request(url, headers=headers)

    logging.info('Fetching %s', req.full_url)
    with urllib.request.urlopen(req) as response:
        content = response.read()

    horskasluzba_report = json.loads(content)

    reports = get_reports_fromjson(horskasluzba_report)
    
    return reports

def get_reports_fromjson(cz_report, fetch_time_dependant=True):
    reports = []

    for bulletin in cz_report:
        report = AvaBulletin()
        report.regions.append(Region('CZ-' + bulletin['region_id']))
        report.publicationTime = pytz.timezone("Europe/Prague").localize(dateutil.parser.parse(bulletin['date_time']))
        report.bulletinID = (bulletin['id'])
        
        report.validTime.startTime = report.publicationTime
        report.validTime.endTime = report.publicationTime + timedelta(hours=24)
        
        danger_rating = DangerRating()
        danger_rating.set_mainValue_int(int(bulletin['warning_level']))
    
        report.dangerRatings.append(danger_rating)
        
        for warning in bulletin['warnings']:
            aspect_list = []
            if warning['exposition'] != 'NONE':
                for exposition in warning['exposition'].replace(' ', '').split(','):
                    aspect_list.append(exposition)
            
            problem = AvalancheProblem()
            if not "ALL" in aspect_list:
                problem.aspects = aspect_list
            problem.elevation = Elevation(lowerBound=warning['altitude_from'], upperBound=warning['altitude_to'])
            problem.add_problemType(warning['type'])
            report.avalancheProblems.append(problem)
        
        report.avalancheActivity = Texts(comment=bulletin['description'])
    
        reports.append(report)

    return reports
