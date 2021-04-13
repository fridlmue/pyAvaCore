import json
import urllib.request
import datetime
from datetime import timedelta

from avacore import pyAvaCore

def process_reports_no(region_id, today=datetime.datetime.today().date()):
    reports = []

    report = pyAvaCore.AvaReport()

    langkey = '2' # Needs to be set by language 1 -> Norwegian, 2 -> Englisch (parts of report)

    url = "https://api01.nve.no/hydrology/forecast/avalanche/v6.0.0/api/AvalancheWarningByRegion/Detail/" + region_id[3:] + "/" + langkey + "/"

    headers = {
        "Content-Type": "application/json; charset=utf-8"
        }

    req = urllib.request.Request(url, headers=headers)

    with urllib.request.urlopen(req) as response:
        content = response.read()

    varsom_report = json.loads(content)

    current = 0 # Probably add one after 5 p.m.

    report.valid_regions.append(region_id)
    report.rep_date = datetime.datetime.fromisoformat(varsom_report[current]['PublishTime'].split('.')[0])
    report.report_id = (region_id + "_" + str(report.rep_date))

    report.validity_begin = datetime.datetime.fromisoformat(varsom_report[current]['ValidFrom'])
    report.validity_end = datetime.datetime.fromisoformat(varsom_report[current]['ValidTo'])

    report.danger_main.append(pyAvaCore.DangerMain(int(varsom_report[current]['DangerLevel']), '-'))

    for problem in varsom_report[current]['AvalancheProblems']:
        problem_type = ''
        if problem['AvalancheProblemTypeId'] == 7:
            problem_type = 'new snow'
        elif problem['AvalancheProblemTypeId'] == 10:
            problem_type = 'drifting snow'
        elif problem['AvalancheProblemTypeId'] == 30:
            problem_type = 'old snow'
        elif problem['AvalancheProblemTypeId'] == 45:
            problem_type = 'wet snow'
        elif problem['AvalancheProblemTypeId'] == 0: #???
            problem_type = 'gliding snow'
        elif problem['AvalancheProblemTypeId'] == 0: #???
            problem_type = 'favourable situation'

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

    report.report_texts.append(pyAvaCore.ReportText('activity_hl', varsom_report[current]['MainText']))
    report.report_texts.append(pyAvaCore.ReportText('activity_com', varsom_report[current]['AvalancheDanger']))
    waek_layers = ''
    if varsom_report[0]['CurrentWeaklayers'] != None:
        waek_layers = '\n' + varsom_report[0]['CurrentWeaklayers']
    report.report_texts.append(pyAvaCore.ReportText('snow_struct_com', varsom_report[current]['SnowSurface']  + waek_layers))
    report.report_texts.append(pyAvaCore.ReportText('tendency_com', varsom_report[current+1]['MainText']))

    reports.append(report)
    return reports
