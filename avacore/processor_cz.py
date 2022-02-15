"""
    Copyright (C) 2021 Friedrich Mütschele and other contributors
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


from avacore.avabulletin import AvaBulletin, DangerRatingType, AvalancheProblemType, AvaCoreCustom, ElevationType, RegionType

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
    
    '''
    current = 0
    now = datetime.now(pytz.timezone('Europe/Prague'))
    if fetch_time_dependant and now.time() > time(17, 0, 0):
        current = 1
    '''

    for bulletin in cz_report:
        report = AvaBulletin()
        report.regions.append(RegionType('CZ' + bulletin['region_abbr'].split('CZ')[1]))
        report.publicationTime = dateutil.parser.parse(bulletin['date_time'])
        report.bulletinID = (bulletin['id'])
        
        report.validTime.startTime = report.publicationTime
        report.validTime.endTime = report.publicationTime + timedelta(hours=24)
        
        danger_rating = DangerRatingType()
        danger_rating.set_mainValue_int(int(bulletin['warning_level']))
    
        report.dangerRatings.append(danger_rating)
        
        for warning in bulletin['warnings']:
            aspect_list = []
            if warning['exposition'] != 'NONE':
                for exposition in warning['exposition'].split(','):
                    aspect_list.append(exposition)
            
            problem_danger_rating = DangerRatingType()
            problem_danger_rating.aspect = aspect_list
            problem_danger_rating.elevation = ElevationType(lowerBound=warning['altitude_from'], upperBound=warning['altitude_to'])
            problem = AvalancheProblemType()
            problem.dangerRating = problem_danger_rating
            problem.add_problemType(warning['type'])
            report.avalancheProblems.append(problem)
        
        report.avalancheActivityComment = bulletin['description']
    
        reports.append(report)

    return reports
    
    '''
    report.regions.append(RegionType(region_id))
    report.publicationTime = dateutil.parser.parse(report[current]['PublishTime'].split('.')[0])
    report.bulletinID = (region_id + "_" + str(report.publicationTime))

    report.validTime.startTime = dateutil.parser.parse(report[current]['ValidFrom'])
    report.validTime.endTime = dateutil.parser.parse(report[current]['ValidTo'])

    # report.danger_main.append(pyAvaCore.DangerMain(int(varsom_report[current]['DangerLevel']), '-'))
    
    danger_rating = DangerRatingType()
    danger_rating.set_mainValue_int(int(report[current]['DangerLevel']))
    
    report.dangerRatings.append(danger_rating)

    for problem in report[current]['AvalancheProblems']:
        problem_type = ''
        if problem['AvalancheProblemTypeId'] == 7:
            problem_type = 'new_snow'
        elif problem['AvalancheProblemTypeId'] == 10:
            problem_type = 'wind_drifted_snow'
        elif problem['AvalancheProblemTypeId'] == 30:
            problem_type = 'persistent_weak_layers'
        elif problem['AvalancheProblemTypeId'] == 45:
            problem_type = 'wet_snow'
        elif problem['AvalancheProblemTypeId'] == 0: #???
            problem_type = 'gliding_snow'
        elif problem['AvalancheProblemTypeId'] == 0: #???
            problem_type = 'favourable_situation'

        aspects = ['N','NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
        aspect_list = []

        for i, c in enumerate(problem['ValidExpositions']):
            if c == '1':
                aspect_list.append(aspects[i])

        elev_prefix = ''
        if problem['ExposedHeightFill'] == 1:
            elev_prefix = '>'
        elif problem['ExposedHeightFill'] == 2:
            elev_prefix = '<'
        
        if not problem_type == '':
            problem_danger_rating = DangerRatingType()
            problem_danger_rating.aspect = aspect_list
            problem_danger_rating.elevation.auto_select(elev_prefix + str(problem['ExposedHeight1']))
            problem = AvalancheProblemType()
            problem.dangerRating = problem_danger_rating
            problem.problemType = problem_type
            report.avalancheProblems.append(problem)

    report.avalancheActivityHighlights = report[current]['MainText']
    report.avalancheActivityComment = report[current]['AvalancheDanger']
    waek_layers = ''
    if report[0]['CurrentWeaklayers'] != None:
        waek_layers = '\n' + report[0]['CurrentWeaklayers']
    report.snowpackStructureComment = report[current]['SnowSurface']  + waek_layers
    report.tendency.tendencyComment = report[current+1]['MainText']


    
    '''
