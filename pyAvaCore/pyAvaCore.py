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

import threading
from datetime import date
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from urllib.request import urlopen
from pathlib import Path
import copy
import re
import sys

# avaRisk only
import pickle

# ALBINA only
import json
import logging
import logging.handlers

logging.basicConfig(
    format='[%(asctime)s] {%(module)s:%(lineno)d} %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.handlers.TimedRotatingFileHandler(filename=f'logs/pyAvaCore.log', when='midnight'),
        logging.StreamHandler(),
    ])

def et_add_parent_info(et):
    for child in et:
        child.attrib['__my_parent__'] = et
        et_add_parent_info(child)

def et_get_parent(et):
    if '__my_parent__' in et.attrib:
        return et.attrib['__my_parent__']
    else:
        return None

def fetch_cached_report(regionID, local, path):
    if Path(path + '/reports/'+regionID+local+'.pkl').is_file():
        with open(path + '/reports/'+regionID+local+'.pkl', 'rb') as input:
            return pickle.load(input)

def get_xml_as_ET(url):

    #timeout_time = 5
    #with urlopen(url, timeout=timeout_time) as response:
    
    with urlopen(url) as response:
        response_content = response.read()
    try:
        try:
            import xml.etree.cElementTree as ET
        except ImportError:
            import xml.etree.ElementTree as ET
        if "VORARLBERG" in url.upper():
            root = ET.fromstring(response_content.decode('latin-1'))
        else:
            root = ET.fromstring(response_content.decode('utf-8'))
    except Exception as e:
        print('error parsing ElementTree: ' + str(e))
    return root

def parse_xml(root):

    reports = []

    for bulletin in root.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}Bulletin'):
        report = AvaReport()
        for observations in bulletin:
            et_add_parent_info(observations)
            for locRef in observations.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}locRef'):
                report.validRegions.append(observations.attrib.get('{http://www.w3.org/1999/xlink}href'))
            for locRef in observations.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}locRef'):
                report.validRegions.append(observations.attrib.get('{http://www.w3.org/1999/xlink}href'))
            for dateTimeReport in observations.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}dateTimeReport'):
                report.repDate = try_parse_datetime(dateTimeReport.text).replace(tzinfo=timezone.utc)
            for validTime in observations.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}validTime'):
                if not (et_get_parent(validTime)):
                    for beginPosition in observations.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}beginPosition'):
                        report.timeBegin = try_parse_datetime(beginPosition.text).replace(tzinfo=timezone.utc)
                    for endPosition in observations.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}endPosition'):
                        report.timeEnd = try_parse_datetime(endPosition.text).replace(tzinfo=timezone.utc)
            for DangerRating in observations.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}DangerRating'):
                mainValueR = 0
                for mainValue in DangerRating.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}mainValue'):
                    mainValueR = int(mainValue.text)
                validElevR = "-"
                for validElevation in DangerRating.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}validElevation'):
                    validElevR = validElevation.attrib.get('{http://www.w3.org/1999/xlink}href')
                report.dangerMain.append(DangerMain(mainValueR, validElevR))
            for DangerPattern in observations.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}DangerPattern'):
                for DangerPatternType in DangerPattern.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}type'):
                    report.dangerPattern.append(DangerPatternType.text)
            i = 0
            for AvProblem in observations.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}AvProblem'):
                typeR = ""
                for avProbType in AvProblem.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}type'):
                    typeR = avProbType.text
                aspect = []
                for validAspect in AvProblem.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}validAspect'):
                    aspect.append(validAspect.get('{http://www.w3.org/1999/xlink}href'))
                validElevR = "-"
                for validElevation in AvProblem.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}validElevation'):
                    validElevR = validElevation.get('{http://www.w3.org/1999/xlink}href')
                i = i+1
                report.problemList.append(Problem(typeR, aspect, validElevR))
            for avActivityHighlights in observations.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}avActivityHighlights'):
                report.activityHighl = avActivityHighlights.text
            for avActivityComment in observations.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}avActivityComment'):
                report.activityCom = avActivityComment.text
            for snowpackStructureComment in observations.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}snowpackStructureComment'):
                report.snowStrucCom = snowpackStructureComment.text
            for tendencyComment in observations.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}tendencyComment'):
                report.tendencyCom = tendencyComment.text
        reports.append(report)

    return reports

def parse_xml_vorarlberg(root):
    numberOfRegions = 6
    reports = []
    report = AvaReport()
    report.validRegions=[""]
    commentEmpty = 1
    # Common for every Report:
    for bulletin in root.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}Bulletin'):
        for detail in bulletin:
            for metaDataProperty in detail.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}metaDataProperty'):
                for dateTimeReport in metaDataProperty.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}dateTimeReport'):
                    report.repDate = try_parse_datetime(dateTimeReport.text)
            for bulletinResultsOf in detail.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}bulletinResultsOf'):
                for travelAdvisoryComment in bulletinResultsOf.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}travelAdvisoryComment'):
                    report.activityCom = travelAdvisoryComment.text
                for highlights in bulletinResultsOf.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}highlights'):
                    report.activityHighl = highlights.text
                for comment in bulletinResultsOf.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}comment'):
                    if commentEmpty:
                        report.tendencyCom = comment.text
                        commentEmpty = 0
                for wxSynopsisComment in bulletinResultsOf.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}wxSynopsisComment'):
                    report.activityCom = report.activityCom + " <br />Alpinwetterbericht der ZAMG Tirol und Vorarlberg:<br /> " + str(wxSynopsisComment.text)
                for snowpackStructureComment in bulletinResultsOf.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}snowpackStructureComment'):
                    report.snowStrucCom = snowpackStructureComment.text
                i = 0
                for AvProblem in detail.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}AvProblem'):
                    typeR = ""
                    for acProblemType in AvProblem.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}type'):
                        typeR = acProblemType.text
                    aspect = []
                    for validAspect in AvProblem.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}validAspect'):
                        aspect.append(validAspect.get('{http://www.w3.org/1999/xlink}href'))
                    validElev = "-"
                    for validElevation in AvProblem.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}validElevation'):
                        for beginPosition in validElevation.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}beginPosition'):
                            validElev = "ElevationRange_" + beginPosition.text + "Hi"
                        for endPosition in validElevation.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}endPosition'):
                            validElev = "ElevationRange_" + endPosition.text + "Lw"
                    i = i+1
                    report.problemList.append(Problem(typeR, aspect, validElev))


    for i in range(numberOfRegions+1):
        reports.append(copy.deepcopy(report))

    # Individual for the Regions:
    for bulletin in root.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}Bulletin'):
        for detail in bulletin:
            for bulletinResultsOf in detail.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}bulletinResultsOf'):
                for DangerRating in bulletinResultsOf.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}DangerRating'):
                    regionID = 7
                    for locRef in DangerRating.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}locRef'):
                        regionID = int(locRef.attrib.get('{http://www.w3.org/1999/xlink}href')[-1])
                        reports[regionID-1].validRegions[0] = locRef.attrib.get('{http://www.w3.org/1999/xlink}href')
                    for validTime in DangerRating.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}validTime'):
                        for beginPosition in validTime.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}beginPosition'):
                            reports[regionID-1].timeBegin = try_parse_datetime(beginPosition.text)
                        for endPosition in validTime.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}endPosition'):
                            reports[regionID-1].timeEnd = try_parse_datetime(endPosition.text)
                    mainValue = 0
                    validElev = "-"
                    for mainValue in DangerRating.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}mainValue'):
                        mainValue = int(mainValue.text)
                    for validElevation in DangerRating.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}validElevation'):
                        for beginPosition in validElevation.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}beginPosition'):
                            validElev = "ElevationRange_" + beginPosition.text + "Hi"
                        for endPosition in validElevation.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}endPosition'):
                            validElev = "ElevationRange_" + endPosition.text + "Lw"
                    reports[regionID-1].dangerMain.append(DangerMain(mainValue, validElev))
    return reports


def parse_xml_bavaria(root):

    numberOfRegions = 6
    reports = []
    report = AvaReport()
    report.validRegions=[""]

    # Common for every Report:
    for metaData in root.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}metaDataProperty'):
        for dateTimeReport in metaData.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}dateTimeReport'):
                    report.repDate = try_parse_datetime(dateTimeReport.text)

    for bulletinMeasurements in root.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}BulletinMeasurements'):
        for travelAdvisoryComment in bulletinMeasurements.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}travelAdvisoryComment'):
            report.activityCom = travelAdvisoryComment.text
        for wxSynopsisComment in bulletinMeasurements.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}wxSynopsisComment'):
            report.activityCom = report.activityCom + " <br />Deutscher Wetterdienst - Regionale Wetterberatung München:<br /> " + str(wxSynopsisComment.text)
        for snowpackStructureComment in bulletinMeasurements.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}snowpackStructureComment'):
            report.snowStrucCom = snowpackStructureComment.text
        for highlights in bulletinMeasurements.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}comment'):
            report.activityHighl = highlights.text
        i = 0
        for avProblem in bulletinMeasurements.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}avProblem'):
            type = ""
            for avType in avProblem.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}type'):
                type = avType.text
            aspect = []
            for validAspect in avProblem.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}validAspect'):
                aspect.append(validAspect.get('{http://www.w3.org/1999/xlink}href').lower())
            validElev = "-"
            for validElevation in avProblem.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}validElevation'):
                for beginPosition in validElevation.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}beginPosition'):
                    validElev = "ElevationRange_" + beginPosition.text + "Hi"
                for endPosition in validElevation.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}endPosition'):
                    validElev = "ElevationRange_" + endPosition.text + "Lw"
            i = i+1
            report.problemList.append(Problem(type, aspect, validElev))

    for i in range(numberOfRegions+1):
        reports.append(copy.deepcopy(report))

    # Check Names of all Regions

    for bulletinResultOf in root.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}bulletinResultsOf'):
        et_add_parent_info(bulletinResultOf)
        for locRef in bulletinResultOf.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}locRef'):
            found = False
            regionID = -1
            firstFree = 100
            for index, report in enumerate(reports):
                if any(report.validRegions):
                    for region in report.validRegions:
                        if region == locRef.attrib.get('{http://www.w3.org/1999/xlink}href'):
                            found = True
                            regionID = index
                else:
                    if firstFree > index:
                        firstFree = index
            if not found:
                reports[firstFree].validRegions.append(locRef.attrib.get('{http://www.w3.org/1999/xlink}href'))
                regionID = firstFree

            DangerRating = et_get_parent(locRef)


            for validTime in DangerRating.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}validTime'):
                for beginPosition in validTime.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}beginPosition'):
                    reports[regionID].timeBegin = try_parse_datetime(beginPosition.text)
                for endPosition in validTime.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}endPosition'):
                    reports[regionID].timeEnd = try_parse_datetime(endPosition.text)
            mainValue = 0
            validElev = "-"
            for mainValue in DangerRating.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}mainValue'):
                mainValue = int(mainValue.text)
            for validElevation in DangerRating.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}validElevation'):
                for beginPosition in validElevation.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}beginPosition'):
                    validElev = "ElevationRange_" + beginPosition.text + "Hi"
                for endPosition in validElevation.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}endPosition'):
                    validElev = "ElevationRange_" + endPosition.text + "Lw"
            reports[regionID].dangerMain.append(DangerMain(mainValue, validElev))

    return reports

def get_reports(url):
    logging.info('Fetching %s', url)
    root = get_xml_as_ET(url)
    if "VORARLBERG" in url.upper():
        reports = parse_xml_vorarlberg(root)
    elif "BAYERN" in url.upper():
        reports = parse_xml_bavaria(root)
    else:
        reports = parse_xml(root)
    return reports


def try_parse_datetime(inStr):
    try:
        r_dateTime = datetime.strptime(inStr, '%Y-%m-%dT%XZ')
    except:
        try:
            r_dateTime = datetime.strptime(inStr[:19], '%Y-%m-%dT%X') # 2019-04-30T15:55:29+01:00
        except:
            r_dateTime = datetime.now()
    return r_dateTime
    
def get_report_url(regionID, local=''): #You can ignore "provider" return value by url, _ = getReportsUrl
     # Euregio-Region Tirol, Südtirol, Trentino
    if ("AT-07" in regionID) or ("IT-32-BZ" in regionID) or ("IT-32-TN" in regionID):
        url = "https://avalanche.report/albina_files/latest/en.xml"
        provider = "The displayed information is provided by an open data API on https://avalanche.report by: Avalanche Warning Service Tirol, Avalanche Warning Service Südtirol, Avalanche Warning Service Trentino."
        if "DE" in local.upper():
            url  = "https://avalanche.report/albina_files/latest/de.xml"
            provider = "Die dargestellten Informationen werden über eine API auf https://avalanche.report abgefragt. Diese wird bereitgestellt von: Avalanche Warning Service Tirol, Avalanche Warning Service Südtirol, Avalanche Warning Service Trentino."

    # Kärnten
    if "AT-02" in regionID:
        url = "https://www.avalanche-warnings.eu/public/kaernten/caaml"
        provider = "Die dargestellten Informationen werden über eine API auf https://www.avalanche-warnings.eu abgefragt. Diese wird bereitgestellt vom: Lawinenwarndienst Kärnten (https://lawinenwarndienst.ktn.gv.at)."

    # Salzburg
    if regionID.startswith("AT-05"):
        url = "https://www.avalanche-warnings.eu/public/salzburg/caaml/en"
        provider = "Die dargestellten Informationen werden über eine API auf https://www.avalanche-warnings.eu abgefragt. Diese wird bereitgestellt vom: Lawinenwarndienst Salzburg (https://lawine.salzburg.at)."
        if "DE" in local.upper():
            url = "https://www.avalanche-warnings.eu/public/salzburg/caaml"
            provider = "The displayed information is provided by an open data API on https://www.avalanche-warnings.eu by: Avalanche Warning Service Salzburg (https://lawine.salzburg.at)."

    # Steiermark
    if regionID.startswith("AT-06"):
        url = "https://www.avalanche-warnings.eu/public/steiermark/caaml/en"
        provider = "The displayed information is provided by an open data API on https://www.avalanche-warnings.eu by: Avalanche Warning Service Steiermark (https://www.lawine-steiermark.at)."
        if "DE" in local.upper():
            url = "https://www.avalanche-warnings.eu/public/steiermark/caaml"
            provider = "Die dargestellten Informationen werden über eine API auf https://www.avalanche-warnings.eu abgefragt. Diese wird bereitgestellt vom: Lawinenwarndienst Steiermark (https://www.lawine-steiermark.at)."

    # Oberösterreich
    if regionID.startswith("AT-04"):
        url = "https://www.avalanche-warnings.eu/public/oberoesterreich/caaml"
        provider = "Die dargestellten Informationen werden über eine API auf https://www.avalanche-warnings.eu abgefragt. Diese wird bereitgestellt vom: Lawinenwarndienst Oberösterreich (https://www.land-oberoesterreich.gv.at/lawinenwarndienst.htm)."

    # Niederösterreich - Noch nicht angelegt
    if "AT-03" in regionID:
        url = "https://www.avalanche-warnings.eu/public/niederoesterreich/caaml"
        provider = "Die dargestellten Informationen werden über eine API auf https://www.avalanche-warnings.eu abgefragt. Diese wird bereitgestellt vom: Lawinenwarndienst Niederösterreich (https://www.lawinenwarndienst-niederoesterreich.at)."

    #Vorarlberg
    if regionID.startswith("AT-08"):
        url = "https://warndienste.cnv.at/dibos/lawine_en/avalanche_bulletin_vorarlberg_en.xml"
        provider = "The displayed information is provided by an open data API on https://warndienste.cnv.at by: Landeswarnzentrale Vorarlberg - http://www.vorarlberg.at/lawine"
        if "DE" in local.upper():
            url = "http://warndienste.cnv.at/dibos/lawine/avalanche_bulletin_vorarlberg_de.xml"
            provider = "Die dargestellten Informationen werden über eine API auf https://warndienste.cnv.at abgefragt. Diese wird bereitgestellt von der Landeswarnzentrale Vorarlberg - http://www.vorarlberg.at/lawine"

    #Bavaria
    if regionID.startswith("BY"):
        url = "https://www.lawinenwarndienst-bayern.de/download/lagebericht/caaml_en.xml"
        provider = "The displayed ihe displayed information is provided by an open data API on https://www.lawinenwarndienst-bayern.de/ by: Avalanche warning centre at the Bavarian State Office for the Environment - https://www.lawinenwarndienst-bayern.de/"
        if "DE" in local.upper():
            url = "https://www.lawinenwarndienst-bayern.de/download/lagebericht/caaml.xml"
            provider = "Die dargestellten Informationen werden über eine API auf https://www.lawinenwarndienst-bayern.de abgefragt. Diese wird bereitgestellt von der Lawinenwarnzentrale Bayern (https://www.lawinenwarndienst-bayern.de)."

    #Val d'Aran
    if regionID.startswith("ES-CT-L"):
        url = "https://conselharan2.cyberneticos.net/albina_files_local/latest/en.xml"
        provider = "The displayed ihe displayed information is provided by an open data API on https://lauegi.conselharan.org/ by: Conselh Generau d'Aran - https://lauegi.conselharan.org/"
        if "DE" in local.upper():
            url = "https://conselharan2.cyberneticos.net/albina_files_local/latest/de.xml"
            provider = "Die dargestellten Informationen werden über eine API auf https://lauegi.conselharan.org/ abgefragt. Diese wird bereitgestellt von Conselh Generau d'Aran (https://lauegi.conselharan.org/)."
            
    return url, provider 

def issue_report(region_id, local, path, from_cache = False, cli_out = False, send_other_side = True):

    url = "https://api.avalanche.report/albina/api/bulletins"
    reports = []
    provider = ""
    
    url, provider = get_report_url(region_id, local)
    
   
    cached = True
    if not from_cache:
        try:
            reports.extend(get_reports(url))
        except:
            matching_report = fetch_cached_report(region_id, local, path)


        Path(path + "/reports/").mkdir(parents=True, exist_ok=True)

        for report in reports:
            for current_region_id in report.validRegions:
                with open(path + '/reports/'+current_region_id+local+'.pkl', 'wb') as f:
                    pickle.dump(report, f, pickle.HIGHEST_PROTOCOL)
            for ID in report.validRegions:
                if ID == region_id:
                  matching_report = report
                  cached = False
    else:
         matching_report = fetch_cached_report(region_id, local, path)
    
    if send_other_side:
        send_to_other_side(matching_report, provider, cached)
    
    if cli_out:
        cli_print_report(matching_report, provider, cached)
        
def send_to_other_side(matching_report, provider, cached): # Should be part of avaRisk not pyAvaCore
    import pyotherside
    try:
        matching_report
    except NameError:
        pyotherside.send('dangerLevel', "Problem resolving Region")
        pyotherside.send('provider', "Couldn't find the RegionID in the Report. Probably it is not served at the moment.")

        pyotherside.send('finished', False)
    else:
        dangerLevel = 0
        try:
            for elem in matching_report.dangerMain:
                if elem['mainValue'] > dangerLevel:
                    dangerLevel = elem['mainValue']
        except:
            pyotherside.send('finished', False)
        pyotherside.send('dangerLevel', dangerLevel)
        pyotherside.send('dangerLevel_h', matching_report.dangerMain[0]['mainValue'])
        if (len(matching_report.dangerMain) > 1):
            pyotherside.send('dangerLevel_l', matching_report.dangerMain[1]['mainValue'])
            pyotherside.send('dangerLevel_alti', matching_report.dangerMain[0]['validElev'])
        else:
            pyotherside.send('dangerLevel_l', matching_report.dangerMain[0]['mainValue'])
        pyotherside.send('highlights', matching_report.activityHighl)
        pyotherside.send('comment',matching_report.activityCom.replace("&nbsp;", " "))
        pyotherside.send('structure', matching_report.snowStrucCom.replace("&nbsp;", " "))
        pyotherside.send('tendency', matching_report.tendencyCom.replace("&nbsp;", " "))
        pyotherside.send('repDate', matching_report.repDate)
        pyotherside.send('validFrom', matching_report.timeBegin)
        pyotherside.send('validTo', matching_report.timeEnd)
        pyotherside.send('numberOfDPatterns', len(matching_report.problemList))
        pyotherside.send('dPatterns', str(matching_report.problemList).replace("'", '"'))
        pyotherside.send('provider', provider)

        pyotherside.send('cached', cached)
        pyotherside.send('finished', True)

def cli_print_report(matching_report, provider, cached):
    try:
        matching_report
    except NameError:
        print('dangerLevel', "Problem resolving Region")
        print('provider', "Couldn't find the RegionID in the Report. Probably it is not served at the moment.")
        
        print('finished')
    else:

        dangerLevel = 0
        for elem in matching_report.dangerMain:
          if elem['mainValue'] > dangerLevel:
              dangerLevel = elem['mainValue']

        print('dangerLevel', dangerLevel)
        print('dangerLevel_h', matching_report.dangerMain[0]['mainValue'])
        if (len(matching_report.dangerMain) > 1):
            print('dangerLevel_l', matching_report.dangerMain[1]['mainValue'])
            print('dangerLevel_alti', matching_report.dangerMain[0]['validElev'])
        else:
            print('dangerLevel_l', matching_report.dangerMain[0]['mainValue'])
        print('highlights', matching_report.activityHighl)
        print('comment',matching_report.activityCom)
        print('structure', matching_report.snowStrucCom)
        print('tendency', matching_report.tendencyCom)
        print('repDate', matching_report.repDate)
        print('validFrom', matching_report.timeBegin.isoformat())
        print(matching_report.timeBegin.tzinfo)
        print('validTo', matching_report.timeEnd)
        print('numberOfDPatterns', len(matching_report.problemList))
        print('dPatterns', str(matching_report.problemList).replace("'", '"'))
        print('provider', provider)

        print('finished')
        
        print(matching_report.validRegions)

class Downloader:
    def __init__(self):
        self.bgthread = threading.Thread()
        self.bgthread.start()

    def download(self, regionID, local, path):
        if self.bgthread.is_alive():
            return
        self.bgthread = threading.Thread(target=issue_report(regionID, local, path))
        self.bgthread.start()

    def cached(self, regionID, local, path):
        issue_report(regionID, local, path, fromCache=True)
        
class Problem:
    type: str
    aspect: list
    validElev: str
    
    def __init__(self, type: str, aspect: list, validElev: str) -> None:
        self.type = type
        self.aspect = aspect
        self.validElev = validElev

class DangerMain:
    mainValue: int
    validElev: str
    
    def __init__(self, mainValue: int, validElev: str):
        self.mainValue = mainValue
        self.validElev = validElev

class AvaReport:
    def __init__(self):
        self.validRegions = []          # list of Regions
        self.repDate = ""               # Date of Report
        self.timeBegin = ""             # valid Ttime start
        self.timeEnd = ""               # valid time end
        self.dangerMain = []            # danger Value and elev
        self.dangerPattern = []         # list of Patterns
        self.problemList = []           # list of Problems with Sublist of Aspect&Elevation
        self.activityHighl = "none"     # String avalanche activity highlits text
        self.activityCom = "none"       # String avalanche comment text
        self.snowStrucCom = "none"      # String comment on snowpack structure
        self.tendencyCom = "none"       # String comment on tendency

def clean_elevation(elev: str):
    if elev in ['', '-', 'ElevationRange_Keine H\u00f6hengrenzeHi']:
        return None
    elev = re.sub(r'ElevationRange_(.+)Hi', r'>\1', elev)
    elev = re.sub(r'ElevationRange_(.+)(Lo|Lw)', r'<\1', elev)
    elev = elev.replace('Forestline', 'Treeline')
    return elev

def dumper(obj):
    if type(obj) is datetime:
        return obj.isoformat()
    try:
        return obj.toJSON()
    except:
        return obj.__dict__

def download_region(regionID):
    url, _ = get_report_url(regionID)
    reports = get_reports(url)
    report: AvaReport
    for report in reports:
        if type(report.timeBegin) is datetime:
            validityDate = report.timeBegin
            if validityDate.hour > 15:
                validityDate = validityDate + timedelta(days=1)
            validityDate = validityDate.date().isoformat()
        report.activityHighl = None
        report.activityCom = None
        report.snowStrucCom = None
        report.tendencyCom = None
        report.validRegions = [r.replace('AT8R', 'AT-08-0') for r in report.validRegions]
        for danger in report.dangerMain:
            danger.validElev = clean_elevation(danger.validElev)
        for problem in report.problemList:
            problem.validElev = clean_elevation(problem.validElev)
            problem.aspect = [a.upper().replace('ASPECTRANGE_', '') for a in problem.aspect]

    directory = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
    with urlopen(url) as http, open(f'{directory}/{validityDate}-{regionID}.xml', mode='wb') as f:
        logging.info('Writing %s to %s', url, f.name)
        f.write(http.read())
    with open(f'{directory}/{validityDate}-{regionID}.json', mode='w', encoding='utf-8') as f:
        logging.info('Writing %s', f.name)
        json.dump(reports, fp=f, default=dumper, indent=2)

if __name__ == "__main__":
    regions = ["AT-02", "AT-03", "AT-04", "AT-05", "AT-06", "AT-08", "BY"]
    for regionID in regions:
        try:
            download_region(regionID)
        except Exception as e:
            logging.error('Failed to download %s', regionID, exc_info=e)
