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
import re
import typing

class ValidTimeType:
    '''
    Defines time intervall for the validity of a Bulletin
    '''
    startTime: datetime
    '''valid time start'''
    endTime: datetime
    '''valid time end'''

class SourceType:
    '''
    Describes the source of the Report
    ToDo: Does not yet extend the whole CAAMLv6
    '''
    provider: str
    '''Bulletin Provider Information'''
    person: str
    '''Bulletin Author'''

class ElevationType:
    '''
    contains a elevation band
    '''
    lowerBound: str
    upperBound: str

    def __init__(self, lowerBound='', upperBound='', auto_select='') -> None:
        if lowerBound != '':
            self.lowerBound = lowerBound
        if upperBound != '':
            self.upperBound = upperBound

        if auto_select != '':
            self.auto_select(auto_select)

    def auto_select(self, auto_select):
        auto_select = auto_select.replace('Forestline', 'Treeline')
        if 'Hi' in auto_select:
            self.lowerBound = re.sub(r'ElevationRange_(.+)Hi', r'\1', auto_select)
        if 'Lo' in auto_select or 'Lw' in auto_select:
            self.upperBound = re.sub(r'ElevationRange_(.+)(Lo|Lw)', r'\1', auto_select)
        if '>' in auto_select:
            self.lowerBound = re.sub(r'>(.+)', r'\1', auto_select)
        if '<' in auto_select:
            self.upperBound = re.sub(r'<(.+)', r'\1', auto_select)

    def toString(self):
        if hasattr(self,'lowerBound') and hasattr(self,'upperBound'):
            return ">" + self.lowerBound + "<" + self.upperBound
        if hasattr(self,'lowerBound'):
            return ">"+ self.lowerBound
        if hasattr(self,'upperBound'):
            return "<"+ self.upperBound
        
class AvaCoreCustom:
    '''
    custom elements for special report content
    '''
    custom_type: str
    content: str

    def __init__(self, custom_type: str, content="") -> None:
        self.custom_type = custom_type
        self.content = content

    def __str__(self):
        return "{'custom_type':'" + self.custom_type + "', 'content':" + self.content + "'}"

    def __repr__(self):
        return str(self)


class DangerRatingType:
    '''
    Describes the Danger Ratings
    ToDo: Does not yet extend the whole CAAMLv6
    '''
    mainValue: str
    '''main value as standardized descriptive text'''
    aspect: list
    '''list of valid aspects'''
    elevation: ElevationType
    '''valid elevation for DangerRating'''
    terrainFeature: str
    '''textual description of terrain, where this danger rating is applicable'''
    
    # --- Values form EAWS Matrix ---
    
    artificialDangerRating: str
    '''artificial danger rating from matrix as standardized descriptive text'''
    artificialAvalancheSize: int
    '''size as value from 1 to 5'''
    artificialAvalancheReleaseProbability: int
    '''release probability from 1 to 4'''
    artificialHazardSiteDistribution: int
    '''hazard site distribution from 1 to 5'''
    naturalDangerRating: str
    '''natural danger rating from matrix as standardized descriptive text'''
    naturalAvalancheReleaseProbability: int
    '''release probability from 1 to 4'''
    naturalHazardSiteDistribution: int
    '''natural hazard site distribution from 1 to 5'''
    customData: typing.List[AvaCoreCustom]
    '''Custom Data for special reports'''
    
    # --- Values form EAWS Matrix ---
    
    values = {
        'low': 1,
        'moderate': 2,
        'considerable': 3,
        'high': 4,
        'very_high': 5
    }
    
    def __init__(self, mainValue='', ) -> None:
        self.elevation = ElevationType()
        self.customData = []
    
    def get_mainValue_int(self):

      return self.values.get(self.mainValue, 0)
  
    def set_mainValue_int(self, value):
        self.mainValue = next((level_text for level_text, level_int in self.values.items() if level_int == value), None)
  
class AvalancheProblemType:
    problemType: str
    '''problem type as standardized descriptive text'''
    dangerRating: DangerRatingType
    '''avalanche danger rating'''
    comment: str

    '''
    ToDo: Addd custom data type
    '''

    def __init__(self) -> None:
        self.dangerRating = DangerRatingType

class TendencyType:
    tendencyType: str
    '''string contains decreasing, steady or increasing'''
    validTime: ValidTimeType
    '''valid time interval for tendency'''
    comment: str
    '''Tendency comment'''
    #ToDo Add custom data
    
    def __init__(self) -> None:
        self.validTime = ValidTimeType()
    
class RegionType:
    name: str
    regionID: str
    
    def __init__(self, regionID) -> None:
        self.regionID = regionID
      
class AvaBulletin:
    '''
    Class for the AvaBulletin
    Follows partly CAAMLv6 caaml:BulletinType
    ToDo: MetaData type is generally missing
    '''
    bulletinID: str
    '''ID of the Bulletin'''
    reportLang: str
    '''language of the Bulletin'''
    region: typing.List[RegionType]
    '''list of Regions, where this Report is valid'''
    publicationTime: datetime
    '''Date of Bulletin'''
    validTime: ValidTimeType
    '''Valid TimeInterval of the Bulletin'''
    source: SourceType
    '''Details about the Bulletin Provider'''
    dangerRating: typing.List[DangerRatingType]
    '''avalanche danger rating'''
    avalancheProblem: typing.List[AvalancheProblemType]
    '''avalanche problem'''
    tendency: TendencyType
    '''tendency of the av situation'''
    highlights: str
    '''very important note in the report'''
    wxSynopsisHighlights: str
    '''weather forecast highlights'''
    wxSynopsisComment: str
    '''Weather forecast comment'''
    avalancheActivityHighlights: str
    '''avalanche activity highlights'''
    avalancheActivityComment: str
    '''avalanche activity comment'''
    snowpackStructureHighlights: str
    '''avalanche structure highlights'''
    snowpackStructureComment: str
    '''snowpack structure comment'''
    travelAdvisoryHighlights: str
    '''travel advisory highlights'''
    travelAdvisoryComment: str
    '''travel advisory comment'''
    tendencyComment: str
    '''tendency comment'''

    predecessor_id: str
    '''not part of CAAMLv6 (yet)'''

    def __init__(self):
        self.region = []
        self.validTime = ValidTimeType()
        self.source = SourceType()
        self.dangerRating = []
        self.avalancheProblem = []
        self.tendency = TendencyType()

    def get_region_list(self):
        region_list = []
        for reg in self.region:
            region_list.append(reg.regionID)
        return region_list

    def cli_out(self):
        '''
        ToDo -- Not working at the moment
        '''
        print('╔═════ AvaReport ', self.reportId, ' ══════')
        if hasattr(self, 'predecessor_id'):
            print('║ This is PM-Report to: ', self.predecessor_id)
        print('║ Report from:          ', self.publicationTime)
        print('║ Validity:             ', self.validity_begin, ' -> ', self.validity_end)
        print('║ Valid for:')
        for region in self.region:
            print('║ |- ', region)

        print('╟───── Danger Rating')
        for danger_main in self.danger_main:
            if danger_main.valid_elevation != None:
                print('║ ', danger_main.valid_elevation, ' -> : ', danger_main.main_value)
            else:
                print('║ ', danger_main.main_value, ' in entire range')

        print('╟───── Av Problems')
        for problem in self.problem_list:
            print('║ Problem: ', problem.problem_type, ' Elevation: ', problem.valid_elevation, ' Aspects: ', problem.aspect)

        if len(self.dangerpattern)  > 0:
            print('╟───── Danger Patterns')
            for dangerpattern in self.dangerpattern:
                print('║ ', dangerpattern)

        print('╟───── Av Texts (if not html or img)')
        for texts in self.report_texts:
            if texts.text_type != 'html_report_local' and texts.text_type != 'prone_locations_img' and \
                texts.text_type != 'html_weather_snow':
                print('║ ', texts.text_type, ': ', texts.text_content)

        print('╚══════════════════════════════════════════')

def clean_elevation(elev: str):
    '''
    Cleans up the elevation description. Should move to the XML-Parsers.
    '''
    if elev in ['', '-', 'ElevationRange_Keine H\u00f6hengrenzeHi']:
        return None
    elev = re.sub(r'ElevationRange_(.+)Hi', r'>\1', elev)
    elev = re.sub(r'ElevationRange_(.+)(Lo|Lw)', r'<\1', elev)
    elev = elev.replace('Forestline', 'Treeline')
    return elev
