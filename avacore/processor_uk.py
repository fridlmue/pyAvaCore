import json
import urllib.request
import datetime
from datetime import timedelta

from avacore import pyAvaCore

def process_reports_uk(today=datetime.datetime.today().date()):
    reports = []

    url = 'https://www.sais.gov.uk/api?action=getForecast' # &params=" + region_id[3:]

    # headers = {"Content-Type": "application/json; charset=utf-8"}
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

    req = urllib.request.Request(url, headers=headers)

    with urllib.request.urlopen(req) as response:
        content = response.read()

    sais_reports = json.loads(content)

    for sais_report in sais_reports:
        report = pyAvaCore.AvaReport()
        report.valid_regions.append('UK-' + sais_report['Region'])
        report.report_id = 'UK-' + sais_report['ID']

        report.rep_date = datetime.datetime.fromisoformat(sais_report['DatePublished']) # 18:00
        report.rep_date = report.rep_date.replace(hour=18)
        report.validity_begin = report.rep_date
        report.validity_end = report.validity_begin + timedelta(days=1)
        report.report_texts.append(pyAvaCore.ReportText('activity_hl', sais_report['Summary']))
        report.report_texts.append(pyAvaCore.ReportText('activity_com', 'Forecast Snow Stability: ' + sais_report['SnowStability']))
        report.report_texts.append(pyAvaCore.ReportText('snow_struct_com', \
            'Forecast Weather Influences: ' + sais_report['WeatherInfluences'] +\
            '\n' + 'Observed Weather Influences: ' + sais_report['ObservedWeatherInfluences'] +\
            '\n' + 'ObservedSnowStability: ' + sais_report['ObservedSnowStability']))

        problems = int(sais_report['KeyIcons'])

        if problems & (1<<1):
            problem_type = 'drifting snow'
            report.problem_list.append(pyAvaCore.Problem(problem_type, [], ''))
        if problems & (1<<2):
            problem_type = 'old snow'
            report.problem_list.append(pyAvaCore.Problem(problem_type, [], ''))
        if problems & (1<<3):
            problem_type = 'new snow'
            report.problem_list.append(pyAvaCore.Problem(problem_type, [], ''))
        if problems & (1<<4):
            problem_type = 'wet snow'
            report.problem_list.append(pyAvaCore.Problem(problem_type, [], ''))
        if problems & (1<<5):
            problem_type = 'Cornices'
            report.problem_list.append(pyAvaCore.Problem(problem_type, [], ''))
        if problems & (1<<6):
            problem_type = 'gliding snow'
            report.problem_list.append(pyAvaCore.Problem(problem_type, [], ''))

        report.danger_main.append(pyAvaCore.DangerMain(max(sais_report['CompassRose'][4:36]), '-'))

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
