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
from datetime import datetime
from datetime import timezone
from datetime import time
from datetime import timedelta
import pytz
import dateutil.parser
import copy
from avacore import pyAvaCore
from avacore.avabulletin import AvaBulletin, DangerRatingType, AvalancheProblemType, RegionType

def et_add_parent_info(element_tree):

    '''Add Parent-Info to structure an ElementTree'''

    for child in element_tree:
        child.attrib['__my_parent__'] = element_tree
        et_add_parent_info(child)

def et_get_parent(element_tree):

    '''get Parent-Info from ElementTree, when parent Info was added previously.'''

    if '__my_parent__' in element_tree.attrib:
        return element_tree.attrib['__my_parent__']
    return None

### XML-Parsers

def parse_xml(root):

    '''parses ALBINA-Style CAAML-XML. root is a ElementTree'''

    reports = []

    for bulletin in root.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}Bulletin'):
        report = AvaBulletin()
        report.bulletinID = bulletin.attrib.get('{http://www.opengis.net/gml}id')
        pm_danger_ratings = []

        pm_available = False
        for DangerRating in bulletin.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}DangerRating'):
            for validTime in DangerRating.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}validTime'):
                pm_available = True
                break

        for observations in bulletin:
            et_add_parent_info(observations)
            for locRef in observations.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}locRef'):
                loc_ref = observations.attrib.get('{http://www.w3.org/1999/xlink}href')
                if loc_ref not in report.region:
                    report.region.append(RegionType(observations.attrib.get('{http://www.w3.org/1999/xlink}href')))
            for dateTimeReport in observations.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}dateTimeReport'):
                report.publicationTime = dateutil.parser.parse(dateTimeReport.text)
            for validTime in observations.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}validTime'):
                if not et_get_parent(validTime):
                    for beginPosition in observations.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}beginPosition'):
                        report.validTime.startTime = dateutil.parser.parse(beginPosition.text)
                    for endPosition in observations.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}endPosition'):
                        report.validTime.endTime = dateutil.parser.parse(endPosition.text)
            for DangerRating in observations.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}DangerRating'):
                main_value = 0
                am_rating = True
                for mainValue in DangerRating.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}mainValue'):
                    main_value = int(mainValue.text)
                valid_elevation = "-"
                for validElevation in DangerRating.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}validElevation'):
                    valid_elevation = validElevation.attrib.get('{http://www.w3.org/1999/xlink}href')
                for beginPosition in DangerRating.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}beginPosition'):
                    validity_begin = dateutil.parser.parse(beginPosition.text)
                    if validity_begin.time() <= time(15, 0, 0):
                        am_rating = False
                        report.validTime.endTime = report.validTime.endTime.replace(hour=validity_begin.hour)
                danger_rating = DangerRatingType()
                danger_rating.set_mainValue_int(main_value)
                danger_rating.elevation.auto_select(valid_elevation)
                if am_rating:
                    report.dangerRating.append(danger_rating)
                else:
                    pm_danger_ratings.append(danger_rating)
            '''
            for DangerPattern in observations.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}DangerPattern'):
                for DangerPatternType in DangerPattern.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}type'):
                    report.dangerpattern.append(DangerPatternType.text)
            '''
            for AvProblem in observations.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}AvProblem'):
                type_r = ""
                for avProbType in AvProblem.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}type'):
                    type_r = avProbType.text
                aspect = []
                for validAspect in AvProblem.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}validAspect'):
                    aspect.append(validAspect.get('{http://www.w3.org/1999/xlink}href').upper().replace('ASPECTRANGE_', ''))
                valid_elevation = "-"
                for validElevation in AvProblem.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}validElevation'):
                    valid_elevation = validElevation.get('{http://www.w3.org/1999/xlink}href')
                comment_r = ''
                for comment in AvProblem.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}comment'):
                    comment_r = comment.text
                problem_danger_rating = DangerRatingType()
                problem_danger_rating.aspect = aspect
                problem_danger_rating.elevation.auto_select(valid_elevation)
                problem = AvalancheProblemType()
                problem.add_problemType(type_r)
                problem.dangerRating = problem_danger_rating
                if comment_r != '':
                    problem.comment = comment_r
                report.avalancheProblem.append(problem)
                # report.problem_list.append(pyAvaCore.Problem(type_r, aspect, valid_elevation))
            for avActivityHighlights in observations.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}avActivityHighlights'):
                # report.report_texts.append(pyAvaCore.ReportText('activity_hl', avActivityHighlights.text))
                report.avalancheActivityHighlights = avActivityHighlights.text
            for wxSynopsisComment in observations.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}wxSynopsisComment'):
                # report.report_texts.append(pyAvaCore.ReportText('activity_hl', avActivityHighlights.text))
                report.wxSynopsisComment = wxSynopsisComment.text
            for avActivityComment in observations.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}avActivityComment'):
                #report.report_texts.append(pyAvaCore.ReportText('activity_com', avActivityComment.text))
                report.avalancheActivityComment = avActivityComment.text
            for snowpackStructureComment in observations.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}'\
                                                              'snowpackStructureComment'):
                # report.report_texts.append(pyAvaCore.ReportText('snow_struct_com', snowpackStructureComment.text))
                report.snowpackStructureComment = snowpackStructureComment.text
            for tendencyComment in observations.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}tendencyComment'):
                # report.report_texts.append(pyAvaCore.ReportText('tendency_com', tendencyComment.text))
                report.tendency.tendencyComment = tendencyComment.text
        reports.append(report)

        if pm_available:
            pm_report = copy.deepcopy(report)
            pm_report.dangerRating = pm_danger_ratings
            pm_report.bulletinID += '_PM'
            pm_report.validTime.startTime = pm_report.validTime.startTime + timedelta(hours=12)
            pm_report.validTime.endTime = pm_report.validTime.endTime + timedelta(hours=12)
            reports.append(pm_report)

    for report in reports:
        if report.bulletinID.endswith('_PM') and any(x.bulletinID == report.bulletinID[:-3] for x in reports):
            report.predecessor_id = report.bulletinID[:-3]

    return reports

def parse_xml_vorarlberg(root):

    '''parses Vorarlberg-Style CAAML-XML. root is a ElementTree'''

    reports = []
    report = pyAvaCore.AvaBulletin()
    comment_empty = 1

    # Common for every Report:

    report_id = ''
    for bulletin in root.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}Bulletin'):
        report_id = bulletin.attrib.get('{http://www.opengis.net/gml}id')

    activity_com = ''
    for bulletin in root.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}Bulletin'):
        for detail in bulletin:
            for metaDataProperty in detail.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}metaDataProperty'):
                for dateTimeReport in metaDataProperty.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}dateTimeReport'):
                    report.publicationTime = dateutil.parser.parse(dateTimeReport.text)
            for bulletinResultsOf in detail.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}bulletinResultsOf'):
                for travelAdvisoryComment in bulletinResultsOf.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}'\
                                                                    'travelAdvisoryComment'):
                    activity_com = travelAdvisoryComment.text
                for highlights in bulletinResultsOf.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}highlights'):
                    # report.report_texts.append(pyAvaCore.ReportText('activity_hl', highlights.text))
                    report.avalancheActivityHighlights = highlights.text
                for comment in bulletinResultsOf.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}comment'):
                    if comment_empty:
                        # report.report_texts.append(pyAvaCore.ReportText('tendency_com', comment.text))
                        report.tendency.tendencyComment = comment.text
                        comment_empty = 0
                for wxSynopsisComment in bulletinResultsOf.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}'\
                                                                'wxSynopsisComment'):
                    report.wxSynopsisComment = wxSynopsisComment.text
                for snowpackStructureComment in bulletinResultsOf.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}'\
                                                                       'snowpackStructureComment'):
                    # report.report_texts.append(pyAvaCore.ReportText('snow_struct_com', snowpackStructureComment.text))
                    report.snowpackStructureComment = snowpackStructureComment.text
                for AvProblem in detail.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}AvProblem'):
                    type_r = ""
                    for ac_problemt_type in AvProblem.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}type'):
                        type_r = ac_problemt_type.text
                    aspect = []
                    for validAspect in AvProblem.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}validAspect'):
                        aspect.append(validAspect.get('{http://www.w3.org/1999/xlink}href').upper().replace(\
                            'ASPECTRANGE_', '').replace('O', 'E'))
                    valid_elevation = "-"
                    for validElevation in AvProblem.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}validElevation'):
                        if '{http://www.w3.org/1999/xlink}href' in validElevation.attrib:
                            if "Treeline" in validElevation.attrib.get('{http://www.w3.org/1999/xlink}href'):
                                if "Hi" in validElevation.attrib.get('{http://www.w3.org/1999/xlink}href'):
                                    valid_elevation = ">Treeline"
                                if "Lo" in validElevation.attrib.get('{http://www.w3.org/1999/xlink}href'):
                                    valid_elevation = "<Treeline"
                        else:
                            for beginPosition in validElevation.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS\
                                                                     beginPosition'):
                                valid_elevation = "ElevationRange_" + beginPosition.text + "Hi"
                            for endPosition in validElevation.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}endPosition'):
                                valid_elevation = "ElevationRange_" + endPosition.text + "Lw"
                    #report.problem_list.append(pyAvaCore.Problem(type_r, aspect, valid_elevation))
                    problem_danger_rating = DangerRatingType()
                    problem_danger_rating.aspect = aspect
                    problem_danger_rating.elevation.auto_select(valid_elevation)
                    problem = AvalancheProblemType()
                    problem.add_problemType(type_r)
                    problem.dangerRating = problem_danger_rating
                    report.avalancheProblem.append(problem)

    # report.report_texts.append(pyAvaCore.ReportText('activity_com', activity_com))
    report.avalancheActivityComment = activity_com

    for bulletinResultOf in root.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}bulletinResultsOf'):
        et_add_parent_info(bulletinResultOf)

        loc_list = []

        for locRef in bulletinResultOf.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}locRef'):
            current_loc_ref = locRef.attrib.get('{http://www.w3.org/1999/xlink}href')

            DangerRating = et_get_parent(locRef)
            validity_begin = ""
            validity_end = ""
            main_value = 0
            valid_elevation = "-"

            for validTime in DangerRating.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}validTime'):
                for beginPosition in validTime.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}beginPosition'):
                    validity_begin = dateutil.parser.parse(beginPosition.text)
                for endPosition in validTime.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}endPosition'):
                    validity_end = dateutil.parser.parse(endPosition.text)
            main_value = 0
            for main_value in DangerRating.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}mainValue'):
                main_value = int(main_value.text)
            for validElevation in DangerRating.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}validElevation'):
                if '{http://www.w3.org/1999/xlink}href' in validElevation.attrib:
                    valid_elevation = validElevation.attrib.get('{http://www.w3.org/1999/xlink}href')
                    '''
                    if "Treeline" in validElevation.attrib.get('{http://www.w3.org/1999/xlink}href'):
                        if "Hi" in validElevation.attrib.get('{http://www.w3.org/1999/xlink}href'):
                            valid_elevation = ">Treeline"
                        if "Lo" in validElevation.attrib.get('{http://www.w3.org/1999/xlink}href'):
                            valid_elevation = "<Treeline"
                    '''
                else:
                    for beginPosition in validElevation.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}beginPosition'):
                        if not 'Keine' in beginPosition.text:
                            valid_elevation = "ElevationRange_" + beginPosition.text + "Hi"
                    for endPosition in validElevation.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}endPosition'):
                        if not 'Keine' in endPosition.text:
                            valid_elevation = "ElevationRange_" + endPosition.text + "Lw"

            danger_rating = DangerRatingType()
            danger_rating.set_mainValue_int(main_value)
            danger_rating.elevation.auto_select(valid_elevation)

            loc_list.append([current_loc_ref, validity_begin, validity_end, danger_rating])

    loc_ref_list = []
    del_index = []

    for index, loc_elem in enumerate(loc_list):
        if loc_elem[1].time() < time(11, 0, 0):
            if not any(loc_elem[0] in loc_ref for loc_ref in loc_ref_list):
                c_report = copy.deepcopy(report)
                c_report.region.append(RegionType(loc_elem[0]))
                c_report.bulletinID = report_id + '-' + loc_elem[0]
                c_report.validTime.startTime = loc_elem[1]
                c_report.validTime.endTime = loc_elem[2]
                c_report.dangerRating.append(loc_elem[3])
                loc_ref_list.append(loc_elem[0])
                reports.append(c_report)
                del_index.append(index)

    loc_list = [i for j, i in enumerate(loc_list) if j not in del_index]
    del_index = []

    for index, loc_elem in enumerate(loc_list):
        if loc_elem[1].time() < time(11, 0, 0):
            report_elem_number = loc_ref_list.index(loc_elem[0])
            if reports[report_elem_number].validTime.startTime > loc_elem[2]:
                reports[report_elem_number].validTime.endTime = loc_elem[2]
            if not (reports[report_elem_number].dangerRating[0].mainValue == loc_elem[3].mainValue and \
                reports[report_elem_number].dangerRating[0].elevation.toString() == loc_elem[3].elevation.toString()): 
                        
                reports[report_elem_number].dangerRating.append(loc_elem[3])
            del_index.append(index)

    loc_list = [i for j, i in enumerate(loc_list) if j not in del_index]
    del_index = []

    for index, loc_elem in enumerate(loc_list):
        if not any((loc_elem[0] + '_PM') in loc_ref for loc_ref in loc_ref_list):
            report_elem_number = loc_ref_list.index(loc_elem[0])
            c_report = copy.deepcopy(reports[report_elem_number])
            loc_ref_list.append(loc_elem[0] + '_PM')

            c_report.bulletinID = report_id + '-' + loc_elem[0] + '_PM'
            c_report.validTime.startTime = loc_elem[1]
            c_report.validTime.endTime = loc_elem[2]
            c_report.predecessor_id = report_id + '-' + loc_elem[0]

            c_report.dangerRating = []
            c_report.dangerRating.append(loc_elem[3])

            reports.append(c_report)
            del_index.append(index)

    loc_list = [i for j, i in enumerate(loc_list) if j not in del_index]
    del_index = []

    for index, loc_elem in enumerate(loc_list):
        report_elem_number = loc_ref_list.index(loc_elem[0] + '_PM')
        for danger_main in reports[report_elem_number].dangerRating:
            if danger_main.elevation.toString() == loc_elem[3].elevation.toString():
                danger_main.mainValue = loc_elem[3].mainValue

    return reports


def parse_xml_bavaria(root, location='bavaria', today = ''):

    '''parses Bavarian-Style CAAML-XML. root is a ElementTree. Also works for Slovenia with minor modification'''
    
    if today == '':
        now = datetime.now(timezone('Europe/Ljubljana'))
        if now.time() > time(17, 0, 1):
            today = now.date() + timedelta(days=1)
        else:
            today = now.date()

    reports = []
    report = AvaBulletin()

    report_id = ''
    for bulletin in root.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}Bulletin'):
        report_id = bulletin.attrib.get('{http://www.opengis.net/gml}id')

    # Common for every Report:
    for metaData in root.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}metaDataProperty'):
        for dateTimeReport in metaData.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}dateTimeReport'):
            if location == 'slovenia':
                time_i = dateutil.parser.parse(dateTimeReport.text, ignoretz = True)
                report.publicationTime =  pytz.timezone("Europe/Berlin").localize(time_i)
            else:
                report.publicationTime = dateutil.parser.parse(dateTimeReport.text)


    activity_com = ''

    for bulletinMeasurements in root.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}BulletinMeasurements'):
        for travelAdvisoryComment in bulletinMeasurements.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}'\
                                                               'travelAdvisoryComment'):
            activity_com = travelAdvisoryComment.text

        for wxSynopsisComment in bulletinMeasurements.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}wxSynopsisComment'):
            report.wxSynopsisComment = wxSynopsisComment.text
        for snowpackStructureComment in bulletinMeasurements.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}'\
                                                                  'snowpackStructureComment'):
            report.snowpackStructureComment = snowpackStructureComment.text
        for highlights in bulletinMeasurements.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}comment'):
            report.avalancheActivityHighlights = highlights.text

        '''
        for DangerPattern in bulletinMeasurements.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}DangerPattern'):
            for DangerPatternType in DangerPattern.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}type'):
                report.dangerpattern.append(DangerPatternType.text)
        '''

        av_problem_tag = 'avProblem' if location == 'bavaria' else 'AvProblem'

        for avProblem in bulletinMeasurements.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}' + av_problem_tag):
            type_r = ""
            for avType in avProblem.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}type'):
                type_r = avType.text
            aspect = []
            for validAspect in avProblem.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}validAspect'):
                aspect.append(validAspect.get('{http://www.w3.org/1999/xlink}href').upper().replace('ASPECTRANGE_', ''))
            valid_elevation = "-"
            for validElevation in avProblem.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}validElevation'):
                for beginPosition in validElevation.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}beginPosition'):
                    if not 'Keine' in beginPosition.text:
                        valid_elevation = "ElevationRange_" + beginPosition.text + "Hi"
                for endPosition in validElevation.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}endPosition'):
                    if not 'Keine' in endPosition.text:
                        valid_elevation = "ElevationRange_" + endPosition.text + "Lw"
            # report.problem_list.append(pyAvaCore.Problem(type_r, aspect, valid_elevation))
            problem_danger_rating = DangerRatingType()
            problem_danger_rating.aspect = aspect
            problem_danger_rating.elevation.auto_select(valid_elevation)
            problem = AvalancheProblemType()
            problem.add_problemType(type_r)
            problem.dangerRating = problem_danger_rating
            report.avalancheProblem.append(problem)

    report.avalancheActivityComment = activity_com

    for bulletinResultOf in root.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}bulletinResultsOf'):
        et_add_parent_info(bulletinResultOf)

        loc_list = []

        for locRef in bulletinResultOf.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}locRef'):
            current_loc_ref = locRef.attrib.get('{http://www.w3.org/1999/xlink}href')

            DangerRating = et_get_parent(locRef)
            validity_begin = ""
            validity_end = ""
            main_value = 0
            valid_elevation = "-"

            for validTime in DangerRating.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}validTime'):
                for beginPosition in validTime.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}beginPosition'):
                    # validity_begin = dateutil.parser.parse(beginPosition.text)
                    if location == 'slovenia':
                        time_i = dateutil.parser.parse(beginPosition.text, ignoretz = True)
                        validity_begin =  pytz.timezone("Europe/Berlin").localize(time_i)
                    else:
                        validity_begin = dateutil.parser.parse(beginPosition.text)
                for endPosition in validTime.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}endPosition'):
                    if location == 'slovenia':
                        time_i = dateutil.parser.parse(endPosition.text, ignoretz = True)
                        validity_end =  pytz.timezone("Europe/Berlin").localize(time_i)
                    else:
                        validity_end = dateutil.parser.parse(endPosition.text)
            main_value = 0
            for main_value in DangerRating.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}mainValue'):
                main_value = int(main_value.text)
            for validElevation in DangerRating.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}validElevation'):
                for beginPosition in validElevation.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}beginPosition'):
                    if not ('Keine' in beginPosition.text or beginPosition.text == '0'):
                        valid_elevation = "ElevationRange_" + beginPosition.text + "Hi"
                for endPosition in validElevation.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}endPosition'):
                    if not ('Keine' in endPosition.text or endPosition.text == '3000'):
                        valid_elevation = "ElevationRange_" + endPosition.text + "Lw"

            danger_rating = DangerRatingType()
            danger_rating.set_mainValue_int(main_value)
            danger_rating.elevation.auto_select(valid_elevation)
            loc_list.append([current_loc_ref, validity_begin, validity_end, danger_rating])
            # loc_list.append([current_loc_ref, validity_begin, validity_end, pyAvaCore.DangerMain(main_value, valid_elevation)])

    loc_ref_list = []
    del_index = []

    if location == 'slovenia':
        loc_list = [i for j, i in enumerate(loc_list) if i[1].date() == today]

    for index, loc_elem in enumerate(loc_list):
        if loc_elem[1].time() == time(0, 0, 0):
            if not any(loc_elem[0] in loc_ref for loc_ref in loc_ref_list):
                c_report = copy.deepcopy(report)
                c_report.region.append(RegionType(loc_elem[0]))
                c_report.bulletinID = report_id + '-' + loc_elem[0]
                c_report.validTime.startTime = loc_elem[1]
                c_report.validTime.endTime = loc_elem[2]
                c_report.dangerRating.append(loc_elem[3])
                loc_ref_list.append(loc_elem[0])
                reports.append(c_report)
                del_index.append(index)

    loc_list = [i for j, i in enumerate(loc_list) if j not in del_index]
    del_index = []

    for index, loc_elem in enumerate(loc_list):
        if loc_elem[1].time() == time(0, 0, 0):
            report_elem_number = loc_ref_list.index(loc_elem[0])
            if reports[report_elem_number].validTime.endTime > loc_elem[2]:
                reports[report_elem_number].validTime.endTime = loc_elem[2]
            if not (reports[report_elem_number].dangerRating[0].mainValue == loc_elem[3].mainValue and \
                reports[report_elem_number].dangerRating[0].elevation.toString() == loc_elem[3].elevation.toString()): 
                reports[report_elem_number].dangerRating.append(loc_elem[3])
            del_index.append(index)

    loc_list = [i for j, i in enumerate(loc_list) if j not in del_index]
    del_index = []

    for index, loc_elem in enumerate(loc_list):
        if not any((loc_elem[0] + '_PM') in loc_ref for loc_ref in loc_ref_list):
            report_elem_number = loc_ref_list.index(loc_elem[0])
            c_report = copy.deepcopy(reports[report_elem_number])
            loc_ref_list.append(loc_elem[0] + '_PM')

            c_report.bulletinID = report_id + '-' + loc_elem[0] + '_PM'
            c_report.validTime.startTime = loc_elem[1]
            c_report.validTime.endTime = loc_elem[2]
            c_report.predecessor_id = report_id + '-' + loc_elem[0]
            for dangerRating in c_report.dangerRating:
                if dangerRating.elevation.toString() == loc_elem[3].elevation.toString():
                    dangerRating.mainValue = loc_elem[3].mainValue
            reports.append(c_report)
            del_index.append(index)

    loc_list = [i for j, i in enumerate(loc_list) if j not in del_index]
    del_index = []

    for index, loc_elem in enumerate(loc_list):
        report_elem_number = loc_ref_list.index(loc_elem[0] + '_PM')
        for danger_main in reports[report_elem_number].dangerRating:
            if danger_main.elevation.toString() == loc_elem[3].elevation.toString():
                danger_main.mainValue = loc_elem[3].mainValue

    return reports
