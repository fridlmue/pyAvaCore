import json
import urllib.request
import datetime
from datetime import timedelta

from avacore import pyAvaCore

def process_reports_it(region_id, today=datetime.datetime.today().date()):

    reports = []
    report = pyAvaCore.AvaReport()

    format = 0
    pm_available = False

    old = False

    p_code, p_zona = it_region_ref[region_id]

    url = "https://www.aineva.it/Aineva_bollettini/NivoMeteo/ServiziNivo.asmx/getZonePrevisioni?pGiorno='1'&pIdZona='" \
        + str(p_zona) + "'&pCode='" + p_code + "'&pIdBollettino=''"

    headers = {
        "Content-Type": "application/json; charset=utf-8"
        }

    req = urllib.request.Request(url, headers=headers)

    with urllib.request.urlopen(req) as response:
        content = response.read()

    aineva_object = json.loads(content)
    all_text = aineva_object['d']
    details_1x = all_text.split('£')
    details_10 = details_1x[0].split('|')
    details_11 = details_1x[1].split('|')
    details_12 = details_1x[2].split('|')

    if len(details_11) < 6:
        old = True
        url = "https://www.aineva.it/Aineva_bollettini/NivoMeteo/ServiziNivo.asmx/getZonePrevisioni?pGiorno='-1'&pIdZona='" \
            + str(p_zona) + "'&pCode='" + p_code + "'&pIdBollettino=''"
        req = urllib.request.Request(url, headers=headers)

        with urllib.request.urlopen(req) as response:
            content = response.read()

        aineva_object = json.loads(content)
        all_text = aineva_object['d']
        details_1x = all_text.split('£')
        details_10 = details_1x[0].split('|')
        details_11 = details_1x[1].split('|')
        details_12 = details_1x[2].split('|')


    '''
    # print(len(response.text))
    print(len(details_1x))
    print(len(details_10))
    print(len(details_11))
    print(len(details_12))
    # print(details_2[6])
    print(details_10)
    print(details_11)
    print(details_12)
    '''

    report.rep_date = date_from_report(details_1x[9])

    report.report_id = region_id + '_' + today.isoformat()
    report.validity_begin = datetime.datetime.combine(today, datetime.time(0,0))
    report.validity_end = datetime.datetime.combine(today, datetime.time(23,59))
    if old:
        report.validity_begin = report.validity_begin - timedelta(hours = 24)
        report.validity_end = report.validity_end - timedelta(hours = 24)


    if int(details_10[0][3]) < 6:
        report.danger_main.append(pyAvaCore.DangerMain(int(details_10[0][3]), '-'))
    else:
        print('not handled yet!')
        # ToDo Needs to check for overday change
    print(details_10[2][3])
    prefix_alti = ''
    if int(details_10[2][3]) in [1, 2, 3]:
        prefix_alti = '>'
    if int(details_10[2][3]) == 4:
        prefix_alti = '<'

    elev_data = details_11[2]
    if prefix_alti != '' and len(elev_data) < 20:
        aspects = []
        general_problem_valid_elevation = ''.join(c for c in elev_data.split('/')[0].split('-')[0] if c.isdigit())
        # ToDo Aspects are missing at the moment
        report.problem_list.append(pyAvaCore.Problem("general", aspects, prefix_alti + general_problem_valid_elevation))

    av_problem = pyAvaCore.Problem(details_10[3][5:-4].lower(), [], "-")
    if av_problem.problem_type != '':
        report.problem_list.append(av_problem)

    reports.append(report)

    return reports

def date_from_report(date):
    date = datetime.datetime.strptime(date, '%d/%m/%Y')
    return date

# Only temporary for debug
def process_all_reports_it():
    for a in it_region_ref.keys():
        m_reports = process_reports_it(a)
        for report in m_reports:
            report.cli_out()



it_region_ref = {
    'IT-21-VB-03': ['Piemonte', 1],
    'IT-21-VB-02': ['Piemonte', 2],
    'IT-21-VB-01': ['Piemonte', 3],
    'IT-21-VC-01': ['Piemonte', 4],
    'IT-21-TO-03': ['Piemonte', 5],
    'IT-21-TO-01': ['Piemonte', 6],
    'IT-21-TO-04': ['Piemonte', 7],
    'IT-21-TO-02': ['Piemonte', 8],
    'IT-21-CN-03': ['Piemonte', 9],
    'IT-21-CN-01': ['Piemonte', 10],
    'IT-21-CN-02': ['Piemonte', 11],
    'IT-21-CN-04': ['Piemonte', 12],
    'IT-21-CN-05': ['Piemonte', 13],
    'IT-23-AO-A01': ['Aosta', 1],
    'IT-23-AO-A02': ['Aosta', 2],
    'IT-23-AO-A03': ['Aosta', 3],
    'IT-23-AO-A04': ['Aosta', 4],
    'IT-23-AO-A05': ['Aosta', 5],
    'IT-23-AO-B06': ['Aosta', 6],
    'IT-23-AO-B07': ['Aosta', 7],
    'IT-23-AO-B08': ['Aosta', 8],
    'IT-23-AO-B09': ['Aosta', 9],
    'IT-23-AO-B10': ['Aosta', 10],
    'IT-23-AO-B11': ['Aosta', 11],
    'IT-23-AO-C12': ['Aosta', 12],
    'IT-23-AO-C13': ['Aosta', 13],
    'IT-23-AO-D14': ['Aosta', 14],
    'IT-23-AO-D15': ['Aosta', 15],
    'IT-23-AO-D16': ['Aosta', 16],
    'IT-23-AO-D17': ['Aosta', 17],
    'IT-23-AO-D18': ['Aosta', 18],
    'IT-23-AO-D19': ['Aosta', 19],
    'IT-23-AO-D20': ['Aosta', 20],
    'IT-23-AO-C21': ['Aosta', 21],
    'IT-23-AO-D22': ['Aosta', 22],
    'IT-23-AO-A23': ['Aosta', 23],
    'IT-23-AO-A24': ['Aosta', 24],
    'IT-23-AO-B25': ['Aosta', 25],
    'IT-23-AO-A26': ['Aosta', 26],
    'IT-25-BS-01': ['Lombardia', 1],
    'IT-25-BG-01': ['Lombardia', 2],
    'IT-25-BG-02': ['Lombardia', 3],
    'IT-25-BS-02': ['Lombardia', 4],
    'IT-25-LC-01': ['Lombardia', 5],
    'IT-25-VA-01': ['Lombardia', 6],
    'IT-25-SO-02': ['Lombardia', 7],
    'IT-25-SO-01': ['Lombardia', 8],
    'IT-25-SO-03': ['Lombardia', 9],
    'IT-34-VI-01': ['Veneto', 1],
    'IT-34-VR-01': ['Veneto', 2],
    'IT-34-BL-06': ['Veneto', 3],
    'IT-34-BL-05': ['Veneto', 4],
    'IT-34-BL-02': ['Veneto', 5],
    'IT-34-BL-03': ['Veneto', 6],
    'IT-34-BL-04': ['Veneto', 7],
    'IT-34-BL-01': ['Veneto', 8],
    'IT-36-UD-01': ['Friuli', 1],
    'IT-36-UD-02': ['Friuli', 2],
    'IT-36-UD-03': ['Friuli', 3],
    'IT-36-UD-04': ['Friuli', 4],
    'IT-36-UD-05': ['Friuli', 5],
    'IT-36-PN-01': ['Friuli', 6],
    'IT-36-PN-02': ['Friuli', 7],
    'IT-57-MC-01': ['Marche', 1],
    'IT-57-AP-01': ['Marche', 2],
    'IT-57-PU-01': ['Marche', 3],
    'IT-57-AP-02': ['Marche', 4],
    }



