"""
    Copyright (C) 2022 Friedrich Mütschele and other contributors
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
import textwrap

class ValidTime:
    '''
    Defines time intervall for the validity of a Bulletin
    '''
    startTime: datetime
    '''valid time start'''
    endTime: datetime
    '''valid time end'''
    
    def __init__(self, startTime=None, endTime=None):
        if not startTime is None:
            self.startTime = startTime
        if not endTime is None:
            self.endTime = endTime

class Provider:
    '''
    Describes the provider given in the source
    ToDo: Does not yet extend the whole CAAMLv6
    '''
    name: str
    website: str #Should be URL

    def __init__(self, name=None, website=None):
        if not name is None:
            self.name = name
        if not website is None:
            self.website = website

class Source:
    '''
    Describes the source of the Report
    ToDo: Does not yet extend the whole CAAMLv6
    '''
    provider: Provider
    '''Bulletin Provider Information'''
    person: str
    '''Bulletin Author DEVIATES FROM CAAMLv6'''
    
    def __init__(self, provider_website=None, provider_name=None, person=None):
        if not provider_website is None:
            self.provider = Provider(name=provider_name, website=provider_website)
        if not person is None:
            self.persion = person

class Elevation:
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
        if not auto_select is None:
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
        else:
            return ""

class AvaCoreCustom:
    '''
    custom elements for special report content
    '''
    custom_type: str
    content: str

    def __init__(self, custom_type: str, content=None) -> None:
        self.custom_type = custom_type
        if not content is None:
            self.content = content
        else:
            self.content = ''

    def __str__(self):
        return "{'custom_type':'" + self.custom_type + "', 'content':" + self.content + "'}"

    def __repr__(self):
        return str(self)
    
class MetaData:
    '''
    MetaData for Report
    '''
    customData: typing.List[AvaCoreCustom]
    
    def __init__(self):
        self.customData = []


class DangerRating:
    '''
    Describes the Danger Ratings
    ToDo: Does not yet extend the whole CAAMLv6
    '''
    mainValue: str
    '''main value as standardized descriptive text'''
    aspects: list
    '''list of valid aspects'''
    elevation: Elevation
    '''valid elevation for DangerRating'''
    terrainFeature: str
    '''textual description of terrain, where this danger rating is applicable'''
    validTimePeriod: str # Should be 'all_day', 'earlier' and 'later'
    
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
        'no_rating': -1,
        'no_snow': 0,
        'low': 1,
        'moderate': 2,
        'considerable': 3,
        'high': 4,
        'very_high': 5
    }
    
    def __init__(self, mainValue='', ) -> None:
        self.elevation = Elevation()
        self.customData = []
    
    def get_mainValue_int(self):

      return self.values.get(self.mainValue, 0)
  
    def set_mainValue_int(self, value):
        self.mainValue = next((level_text for level_text, level_int in self.values.items() if level_int == value), None)
        
    def from_json(self, dangerRating_json):
        attributes = DangerRating.__dict__['__annotations__']
        for attribute in attributes:
            if (not attribute.startswith('__')
                and attribute in dangerRating_json):
                if attributes[attribute] in {str, datetime, list, int}:
                    setattr(self, attribute, dangerRating_json[attribute])
                elif attribute is 'elevation':
                    for elevation_attribute in dangerRating_json[attribute]:
                        setattr(self.elevation, elevation_attribute, dangerRating_json[attribute][elevation_attribute])
  
class AvalancheProblem:
    problemType: str
    '''problem type as standardized descriptive text'''
    # dangerRating: DangerRating
    # '''avalanche danger rating'''
    comment: str

    elevation: Elevation
    aspects: list
    terrainFeature: str # ToDo: Crosscheck with comment

    validTimePeriod: str # Should be 'all_day', 'earlier' and 'later'

    '''
    ToDo: Addd custom data type
    '''
        
    def __init__(self, problemType=None, comment=None, dangerRating_json=None, dangerRating=None, aspects=None, elevation=None) -> None:
        self.aspects = []
        self.elevation = Elevation()
        if not problemType is None:
            self.problemType = problemType
        if not comment is None:
            self.comment = comment
        if not dangerRating is None: # Compatibility with older parsers, deprecated
            self.elevation = dangerRating.elevation
            self.aspects = dangerRating.aspect
        if not dangerRating_json is None: # Compatibility with older parsers, deprecated
            dangerRating = dangerRating.from_json(dangerRating_json)
            self.elevation = dangerRating.elevation
            self.aspects = dangerRating.aspect
        if not aspects is None:
            self.aspects = aspects
        if not elevation is None:
            self.elevation = elevation
        
    def add_problemType(self, problem_type_text):
        '''
        All problem type texts in pre CAAMLv6 need a post processing to match the new standard
        All new problem texts contain a unterscore and can be differentiated by that
        '''
        if not '_' in problem_type_text or 'drifting_snow' in problem_type_text:
            if 'new' in problem_type_text:
                problem_type_text = 'new_snow'
            elif 'drifting' in problem_type_text or 'drifted' in problem_type_text:
                problem_type_text = 'wind_drifted_snow'
            elif 'old' in problem_type_text or 'persistent' in problem_type_text:
                problem_type_text = 'persistent_weak_layers'
            elif 'wet' in problem_type_text:
                problem_type_text = 'wet_snow'
            elif 'gliding' in problem_type_text:
                problem_type_text = 'gliding_snow'
            elif 'favourable' in problem_type_text:
                problem_type_text = 'favourable_situation'
        
        self.problemType = problem_type_text

class Tendency:
    tendencyType: str
    '''string contains decreasing, steady or increasing'''
    validTime: ValidTime
    '''valid time interval for tendency'''
    tendencyComment: str
    '''tendency comment'''
    #ToDo Add custom data
    
    def __init__(self) -> None:
        self.validTime = ValidTime()
        
    def __init__(self, tendencyType=None, validTime_json=None, tendencyComment=None) -> None:
        self.validTime = ValidTime()
        if not validTime_json is None and not len(validTime_json) is 0:
            self.validTime = ValidTime(validTime_json['startTime'], validTime_json['endTime'])
        if not tendencyType is None:
            self.tendencyType = tendencyType
        if not tendencyComment is None:
            self.tendencyComment = tendencyComment

class Region:
    name: str
    regionID: str
        
    def __init__(self, regionID, name=None) -> None:
        self.regionID = regionID
        if not name is None:
            self.name = name

class Texts:
    highlights: str
    comment: str

    def __init__(self, highlights=None, comment=None) -> None:
        if not highlights is None:
            self.highlights = highlights
        if not comment is None:
            self.comment = comment
      
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
    regions: typing.List[Region]
    '''list of Regions, where this Report is valid'''
    publicationTime: datetime
    '''Date of Bulletin'''
    validTime: ValidTime
    '''Valid TimeInterval of the Bulletin'''
    source: Source

    '''Details about the Bulletin Provider'''
    dangerRatings: typing.List[DangerRating]
    '''avalanche danger rating'''
    avalancheProblems: typing.List[AvalancheProblem]
    '''avalanche problem'''
    tendency: Tendency
    '''tendency of the av situation'''
    highlights: str
    '''very important note in the report'''
    wxSynopsis: Texts
    '''weather forecast'''
    avalancheActivity: Texts
    '''avalanche activity'''
    snowpackStructure: Texts
    '''avalanche structure '''
    travelAdvisory: Texts
    '''travel advisory'''
    metaData: MetaData

    customData: typing.List[AvaCoreCustom]

    predecessor_id: str
    '''not part of CAAMLv6 (yet)'''

    def __init__(self):
        self.regions = []
        self.validTime = ValidTime()
        self.source = Source()
        self.dangerRatings = []
        self.avalancheProblems = []
        self.tendency = Tendency()
        self.customData = []

    def get_region_list(self):
        region_list = []
        for reg in self.regions:
            region_list.append(reg.regionID)
        return region_list
    
    def from_json(self, bulletin_json):
        attributes = AvaBulletin.__dict__['__annotations__']
        for attribute in attributes:
            if (not attribute.startswith('__')
                and attribute in bulletin_json):
                if attributes[attribute] in {str, datetime}:
                    setattr(self, attribute, bulletin_json[attribute])

                elif attribute is 'regions':
                    for region in bulletin_json[attribute]:
                        self.regions.append(Region(region.get('regionID'), region.get('name')))

                elif attribute is 'dangerRatings':
                    for dangerRating_json in bulletin_json[attribute]:
                        dangerRating = DangerRating()
                        dangerRating.from_json(dangerRating_json)
                        self.dangerRatings.append(dangerRating)

                elif attribute is 'avalancheProblems':
                    for avalancheProblem_json in bulletin_json[attribute]:
                        avalancheProblem = AvalancheProblem(problemType=avalancheProblem_json.get('problemType'), comment=avalancheProblem_json.get('comment'), dangerRating_json=avalancheProblem_json.get('dangerRating'))
                        self.avalancheProblems.append(avalancheProblem)

                elif attribute is 'validTime':
                    self.validTime = ValidTime(bulletin_json[attribute]['startTime'], bulletin_json[attribute]['endTime'])

                elif attribute is 'tendency':
                    self.tendency = Tendency(bulletin_json[attribute].get('tendencyType'), bulletin_json[attribute].get('validTime'), bulletin_json[attribute].get('tendencyComment'))

                elif attribute is 'source':
                    self.source = Source
                    (bulletin_json[attribute].get('provider'), bulletin_json[attribute].get('person'))

                else:
                    print('Not handled Attribute:', attribute, attributes[attribute], type(attributes[attribute]))                   

    # def fill_std_attributes(self, to_fill, fill_with):
        
        # if 'predecessor_id' in bulletin_json:
    
    def prettify_out(self, text):
        print("\n".join(textwrap.wrap(text, width=60, initial_indent='╟─ ', subsequent_indent='║  ')))
        

    def cli_out(self):
        '''
        ToDo -- Not working at the moment
        '''
        print('╔═════ AvaReport ══════════════════════════════════════════')
        print('║ Bulletin:            ', self.bulletinID)
        if hasattr(self, 'predecessor_id'):
            print('║ This is PM-Report to:', self.predecessor_id)
        print('║ Report from:         ', self.publicationTime)
        print('║ Valid from:          ', self.validTime.startTime)
        print('║ Valid to:            ', self.validTime.endTime)
        print('║ Valid for:')
        for region in self.regions:
            print('║ ├─ ', region.regionID)

        print('╟───── Danger Rating')
        for dangerRating in self.dangerRatings:
            print('║ ', dangerRating.elevation.toString(), '➝ :', dangerRating.mainValue)


        print('╟───── Av Problems')
        for problem in self.avalancheProblems:
            try:
                print('║ Problem: ', problem.problemType, '\n║    Elevation: ', problem.elevation.toString(), '\n║    Aspects: ', problem.aspects)
            except:
                print('║ Problem: ', problem.problemType)

        '''
        if len(self.dangerpattern)  > 0:
            print('╟───── Danger Patterns')
            for dangerpattern in self.dangerpattern:
                print('║ ', dangerpattern)
        '''

        print('╟───── Bulletin Texts ─────')
        if hasattr(self, 'highlights'):
            self.prettify_out('Highlights: ' +  self.highlights)
            
        if hasattr(self.avalancheActivity, 'highlights'):
            self.prettify_out('avalancheActivityHighlights: ' +  self.avalancheActivity.highlights)
            
        if hasattr(self.avalancheActivity, 'comment'):
            self.prettify_out('avalancheActivityComment: ' +  self.avalancheActivity.comment)
            
        if hasattr(self.snowpackStructure, 'highlights'):
            self.prettify_out('snowpackStructureHighlights: ' +  self.snowpackStructure.highlights)
            
        if hasattr(self.snowpackStructure, 'comment'):
            self.prettify_out('snowpackStructureComment: ' +  self.snowpackStructure.comment)
            
        if hasattr(self.travelAdvisory, 'highlights'):
            self.prettify_out('travelAdvisoryHighlights: ' +  self.travelAdvisory.highlights)
            
        if hasattr(self.travelAdvisory, 'comment'):
            self.prettify_out('travelAdvisoryComment: ' +  self.travelAdvisory.comment)
            
        if hasattr(self.wxSynopsis, 'highlights'):
            self.prettify_out('wxSynopsisHighlights: ' +  self.wxSynopsis.highlights)
            
        if hasattr(self.wxSynopsis, 'comment'):
            self.prettify_out('wxSynopsisComment: ' +  self.wxSynopsis.comment)
            
        if hasattr(self.tendency, 'tendencyComment'):
            self.prettify_out('tendencyComment: ' +  self.tendency.tendencyComment)

        print('╚═══════════════════════════════════════════════════════════\n')
