import json
import urllib.request
from datetime import datetime
from datetime import timedelta
import pytz
import dateutil.parser

from avacore.avabulletin import AvaBulletin, DangerRatingType, AvalancheProblemType, AvaCoreCustom, ElevationType, RegionType

def process_reports_uk(today=datetime.today().date()):
    reports = []

    url = 'https://www.sais.gov.uk/api?action=getForecast' # &params=" + region_id[3:]

    # headers = {"Content-Type": "application/json; charset=utf-8"}
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

    req = urllib.request.Request(url, headers=headers)

    with urllib.request.urlopen(req) as response:
        content = response.read()

    sais_reports = json.loads(content)

    for sais_report in sais_reports:
        report = AvaBulletin()
        # report.valid_regions.append('UK-' + sais_report['Region'])
        report.regions.append(RegionType('UK-' + sais_report['Region']))
        report.bulletinID = 'UK-' + sais_report['ID']

        report.publicationTime = dateutil.parser.parse(sais_report['DatePublished']) # 18:00
        report.validTime.startTime = report.publicationTime.replace(hour=18)
        report.validTime.endTime = report.validity_begin + timedelta(days=1)
        report.avalancheActivityHighlights = sais_report['Summary']
        report.avalancheActivityComment = 'Forecast Snow Stability: ' + sais_report['SnowStability']
        report.snowpackStructureComment = 'Forecast Weather Influences: ' + sais_report['WeatherInfluences'] +\
            '\n' + 'Observed Weather Influences: ' + sais_report['ObservedWeatherInfluences'] +\
            '\n' + 'ObservedSnowStability: ' + sais_report['ObservedSnowStability']

        problems = int(sais_report['KeyIcons'])

        problem = AvalancheProblemType()

        if problems & (1<<1):
            problem = AvalancheProblemType()
            problem.problemType = 'wind_drifted_snow'
            report.avalancheProblems.append(problem)
        if problems & (1<<2):
            problem = AvalancheProblemType()
            problem.problemType = 'persistent_weak_layers'
            report.avalancheProblems.append(problem)
        if problems & (1<<3):
            problem = AvalancheProblemType()
            problem.problemType = 'new_snow'
            report.avalancheProblems.append(problem)
        if problems & (1<<4):
            problem = AvalancheProblemType()
            problem.problemType = 'wet_snow'
            report.avalancheProblems.append(problem)
        if problems & (1<<5):
            problem = AvalancheProblemType()
            #problem.problemType = 'cornice_failure'
            report.avalancheProblems.append(problem)
        if problems & (1<<6):
            problem = AvalancheProblemType()
            problem.problemType = 'gliding_snow'
            report.avalancheProblems.append(problem)

        # report.danger_main.append(pyAvaCore.DangerMain(max(sais_report['CompassRose'][4:36]), '-'))

        danger_rating = DangerRatingType()
        danger_rating.set_mainValue_int(max(sais_report['CompassRose'][4:36]))
        report.dangerRatings.append(danger_rating)

        reports.append(report)

    '''
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

        report.problem_list.append(pyAvaCore.Problem(problem_type, aspect_list, elev_prefix + str(problem['ExposedHeight1'])))

    '''
    return reports
