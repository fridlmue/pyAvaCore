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
from datetime import timedelta
from pathlib import Path
import pytz
import urllib.request
import zipfile
import copy
import base64
import json

from avacore import pyAvaCore
from avacore.png import png
from avacore.avabulletin import AvaBulletin, DangerRatingType, AvalancheProblemType, AvaCoreCustom, ElevationType, RegionType


def fetch_files_ch(lang, path):
    '''
    Downloads the swiss avalanche zip for the slf app together with the region mapping information
    '''
    Path(path + '/swiss/').mkdir(parents=True, exist_ok=True)
    url = 'https://www.slf.ch/avalanche/mobile/bulletin_'+lang+'.zip'
    urllib.request.urlretrieve(url, path + '/swiss/bulletin_'+lang+'.zip')

    try:
        urllib.request.urlretrieve('https://www.slf.ch/avalanche/bulletin/'+lang+'/gk_region2pdf.txt', path + '/swiss/gk_region2pdf.txt')
    except:
        open(path + '/swiss/gk_region2pdf.txt', 'a').close()
        

    with zipfile.ZipFile(path + '/swiss/bulletin_'+lang+'.zip', 'r') as zip_ref:
        zip_ref.extractall(path + '/swiss/')


def get_prone_locations(img_text):
    '''
    Extract dangerous aspects from png
    '''
    imgdata = base64.b64decode(img_text)
    png_data = png.Reader(bytes=imgdata)

    _, _, px, _ = png_data.read()

    px_list = list(px)

    aspects = []

    if px_list[20][129] == 0:
        aspects.append('NNE')
    if px_list[25][145] == 0:
        aspects.append('ENE')
    if px_list[31][145] == 0:
        aspects.append('ESE')
    if px_list[36][129] == 0:
        aspects.append('SSE')
    if px_list[36][101] == 0:
        aspects.append('SSW')
    if px_list[31][77] == 0:
        aspects.append('WSW')
    if px_list[25][77] == 0:
        aspects.append('WNW')
    if px_list[20][101] == 0:
        aspects.append('NNW')

    return aspects

def process_reports_ch(path, lang="en", cached=False):
    '''
    Download the reports for CH
    '''
    
    reports = []
    
    if not cached:
        fetch_files_ch(lang, path)

    if Path(path + '/swiss/gk_region2pdf.txt').is_file():

        # Receives validity information from text.json
        with open(path + '/swiss/text.json') as fp:
            data = json.load(fp)

        # region_id = region_id[-4:]

        common_report = pyAvaCore.AvaBulletin()

        begin, end = data['validity'].split('/')

        date_time_now = datetime.now()

        common_report.publicationTime = pytz.timezone("Europe/Zurich").localize(datetime.strptime(str(date_time_now.year) + '-' + begin[begin.find(':')+2:-1], '%Y-%d.%m., %H:%M'))
        common_report.validTime.startTime = common_report.publicationTime
        if common_report.validTime.startTime.hour == 17:
            common_report.validTime.endTime = common_report.validTime.startTime + timedelta(days=1)
        elif common_report.validTime.startTime.hour == 8:
            common_report.validTime.endTime = common_report.validTime.startTime + timedelta(hours=9)
        else: # Shourld not happen
            common_report.validTime.endTime = pytz.timezone("Europe/Zurich").localize(datetime.strptime(str(date_time_now.year) + '-' + end[end.find(':')+2:], '%Y-%d.%m., %H:%M'))

        bulletinIDs = []

        # Receives the ID of the report that matches the selected region_id
        with open(path + '/swiss/gk_region2pdf.txt') as fp:
            for line in fp:
                bulletinID = line.split('_')[5][:-5]
                bulletinID_pm = None
                if len(bulletinID) > 7:
                    bulletinID_pm = bulletinID[7:]
                    bulletinID = bulletinID[:7]
                if bulletinID not in bulletinIDs:
                    bulletinIDs.append(bulletinID)
                    new_report = copy.deepcopy(common_report)
                    new_report.bulletinID = bulletinID
                    reports.append(new_report)
                if not bulletinID_pm is None and bulletinID_pm not in bulletinIDs:
                    bulletinIDs.append(bulletinID_pm)
                    new_report = copy.deepcopy(common_report)
                    new_report.bulletinID = bulletinID_pm
                    new_report.predecessor_id = bulletinID
                    reports.append(new_report)
                elif not bulletinID_pm is None:
                    if not bulletinID in reports[bulletinIDs.index(bulletinID_pm)].predecessor_id:
                        reports[bulletinIDs.index(bulletinID_pm)].predecessor_id += ('_' + bulletinID)
                reports[bulletinIDs.index(bulletinID)].region.append(RegionType("CH-" + line[:4]))
                if not bulletinID_pm is None:
                    reports[bulletinIDs.index(bulletinID_pm)].region.append(RegionType("CH-" + line[:4]))

        for report in reports:
            # Opens the matching Report-File
            folder = '1'
            if hasattr(report, 'predecessor_id'):
                folder = '2'

            with open(path + '/swiss/'+folder+'/dst' + report.bulletinID + '.html', encoding="utf-8") as f:
                text = f.read()

            # Isolates the relevant Danger Information
            text_pos = text.find('data-level=')+len('data-level=')+1
            
            danger_rating = DangerRatingType()
            danger_rating.set_mainValue_int(int(text[text_pos:text_pos+1]))
            # danger_rating.elevation.auto_select(valid_elevation)
            
            report.dangerRating.append(danger_rating)

            # Isolates the prone location Image
            text_pos = text.find('src="data:image/png;base64,')+len('src="data:image/png;base64,')
            subtext = text[text_pos:]
            prone_locations_img = AvaCoreCustom('prone_locations_img')
            prone_locations_img.content = subtext[:subtext.find('"')]
            general_problem_locations = ''
            if len(prone_locations_img.content) < 1000: # Sometimes no Picture is attached
                prone_locations_img.content = '-'
            else:
                general_problem_locations = get_prone_locations(prone_locations_img.content)
            report.dangerRating[0].customData.append(prone_locations_img)

            # Isolates the prone location Text
            text_pos = subtext.find('alt="')+len('alt="')
            subtext = subtext[text_pos:]
            prone_locations_text = AvaCoreCustom('prone_locations_text')
            prone_locations_text.content = subtext[:subtext.find('"')]
            if prone_locations_text.content == 'Content-Type':
                prone_locations_text.content = '-'
            else:
                valid_elevation = ''.join(c for c in prone_locations_text.content if c.isdigit())
                report.dangerRating[0].elevation = ElevationType(valid_elevation)

            report.dangerRating[0].customData.append(prone_locations_text)
            report.dangerRating[0].aspect = general_problem_locations
            
            # report.dangerRating[0].customData.append(pyAvaCore.Problem("general", general_problem_locations, general_problem_valid_elevation))

            # Remove Image from html, sometimes no Picture is attached
            html_report_local = AvaCoreCustom('html_report_local')
            try:
                split1 = text.split('<img')
                split2 = split1[1].split('">')
                html_report_local.content = split1[0]+'"'.join(split2[1:])

            except:
                html_report_local.content = text
            report.dangerRating[0].customData.append(html_report_local)

            # Retreives the Weather and Snow Information
            text = ""
            with open(path + '/swiss/sdwetter.html', encoding="utf-8") as f:
                text = f.read()

            html_weather_snow = AvaCoreCustom('html_weather_snow')
            html_weather_snow.content = text
            report.dangerRating[0].customData.append(html_weather_snow)

        return reports
    
