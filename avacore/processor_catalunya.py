import json
import urllib.request
import datetime
from datetime import timedelta

from avacore import pyAvaCore

def process_reports_cat(today=datetime.datetime.today().date()):

    reports = []

    lang = {
        'en':3,
        'ca':1,
        'es':2
    }

    url = "https://bpa.icgc.cat/api/query?id=512&values="+str(today)+";"+str(lang['es'])

    headers = {
        "Content-Type": "application/json; charset=utf-8"
        }

    req = urllib.request.Request(url, headers=headers)

    with urllib.request.urlopen(req) as response:
        content = response.read()

    icgc_reports = json.loads(content)

    for icgc_report in icgc_reports:
        report = pyAvaCore.AvaReport()

        report.rep_date = icgc_report['databutlleti']
        report.report_id = 'ES-CT-ICGC-'+ icgc_report['id_zona'] + '_' + str(report.rep_date)
        report.valid_regions.append('ES-CT-ICGC-'+ icgc_report['id_zona'])
        report.validity_begin = datetime.datetime.combine( \
            datetime.datetime.strptime(icgc_report['datavalidesabutlleti'], '%Y-%m-%d'), datetime.time(0,0))
        report.validity_end = datetime.datetime.combine( \
            datetime.datetime.strptime(icgc_report['datavalidesabutlleti'], '%Y-%m-%d'), datetime.time(23,59))

        report.report_texts.append(pyAvaCore.ReportText('activity_hl', icgc_report['perill_text']))
        report.report_texts.append(pyAvaCore.ReportText('activity_com', icgc_report['text_estat_mantell']))
        report.report_texts.append(pyAvaCore.ReportText('snow_struct_com', icgc_report['text_distribucio']))
        report.report_texts.append(pyAvaCore.ReportText('tendency_com', icgc_report['text_tendencia']))

        report.danger_main.append(pyAvaCore.DangerMain(int(icgc_report['grau_perill_primari']), '-'))
        if not icgc_report['grau_perill_secundari'] == None:
            report.danger_main.append(pyAvaCore.DangerMain(int(icgc_report['grau_perill_secundari']), '-'))

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
            report.problem_list.append(pyAvaCore.Problem(problem_type, [], '-'))

        reports.append(report)

    return reports
