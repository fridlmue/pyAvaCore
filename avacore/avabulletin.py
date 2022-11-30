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
from dataclasses import dataclass
from datetime import datetime, timedelta, date
import re
import typing
import textwrap


class ValidTime:
    """
    Defines time intervall for the validity of a Bulletin
    """

    startTime: datetime
    """valid time start"""
    endTime: datetime
    """valid time end"""

    def __init__(self, startTime=None, endTime=None):

        if not startTime is None:
            if not isinstance(startTime, datetime):
                startTime = datetime.fromisoformat(startTime)
            self.startTime = startTime
        if not endTime is None:
            if not isinstance(endTime, datetime):
                endTime = datetime.fromisoformat(endTime)
            self.endTime = endTime


@dataclass
class Provider:
    """
    Describes the provider given in the source
    """

    name: typing.Optional[str] = None
    website: typing.Optional[str] = None


@dataclass
class Source:
    """
    Describes the source of the Report
    """

    provider: typing.Optional[Provider] = None
    """Bulletin Provider Information"""
    person: typing.Optional[str] = None
    """Bulletin Author DEVIATES FROM CAAMLv6"""


@dataclass
class Elevation:
    """
    contains a elevation band
    """

    lowerBound: typing.Optional[str] = None
    upperBound: typing.Optional[str] = None

    def auto_select(self, auto_select):
        """
        Auto-Selct from different possible ways of elevation description if it is lower or upper bound.
        """
        if not auto_select is None:
            auto_select = auto_select.replace("Forestline", "treeline")
            auto_select = auto_select.replace("Treeline", "treeline")
            if "Hi" in auto_select:
                self.lowerBound = re.sub(r"ElevationRange_(.+)Hi", r"\1", auto_select)
            if "Lo" in auto_select or "Lw" in auto_select:
                self.upperBound = re.sub(
                    r"ElevationRange_(.+)(Lo|Lw)", r"\1", auto_select
                )
            if ">" in auto_select:
                self.lowerBound = re.sub(r">(.+)", r"\1", auto_select)
            if "<" in auto_select:
                self.upperBound = re.sub(r"<(.+)", r"\1", auto_select)

    def toString(self):
        """
        Return a elevation as string.
        """
        if self.lowerBound and self.upperBound:
            return ">" + self.lowerBound + "<" + self.upperBound
        if self.lowerBound:
            return ">" + self.lowerBound
        if self.upperBound:
            return "<" + self.upperBound

        return ""


@dataclass
class MetaData:
    """
    MetaData for Report
    """

    customData: typing.Dict


class DangerRating:
    """
    Describes the Danger Ratings
    """

    mainValue: str
    """main value as standardized descriptive text"""
    aspects: list
    """list of valid aspects"""
    elevation: Elevation
    """valid elevation for DangerRating"""
    terrainFeature: str
    """textual description of terrain, where this danger rating is applicable"""
    validTimePeriod: str  # Should be 'all_day', 'earlier' and 'later'

    # --- Values form EAWS Matrix ---

    artificialDangerRating: str
    """artificial danger rating from matrix as standardized descriptive text"""
    artificialAvalancheSize: int
    """size as value from 1 to 5"""
    artificialAvalancheReleaseProbability: int
    """release probability from 1 to 4"""
    artificialHazardSiteDistribution: int
    """hazard site distribution from 1 to 5"""
    naturalDangerRating: str
    """natural danger rating from matrix as standardized descriptive text"""
    naturalAvalancheReleaseProbability: int
    """release probability from 1 to 4"""
    naturalHazardSiteDistribution: int
    """natural hazard site distribution from 1 to 5"""
    customData: typing.Dict
    """Custom Data for special reports"""

    # --- Values form EAWS Matrix ---

    values = {
        "no_rating": -1,
        "no_snow": 0,
        "low": 1,
        "moderate": 2,
        "considerable": 3,
        "high": 4,
        "very_high": 5,
    }

    def __init__(self, mainValue="", validTimePeriod="all_day") -> None:
        self.elevation = Elevation()
        self.customData = []
        self.validTimePeriod = validTimePeriod
        self.mainValue = mainValue

    def get_mainValue_int(self):
        """
        Returns danger main as int value
        """
        return self.values.get(self.mainValue, 0)

    def set_mainValue_int(self, value):
        """
        Sets danger main from int
        """
        self.mainValue = next(
            (
                level_text
                for level_text, level_int in self.values.items()
                if level_int == value
            ),
            None,
        )

    def from_json(self, dangerRating_json):
        """
        get danger rating from JSON
        """
        attributes = DangerRating.__dict__["__annotations__"]
        for attribute in attributes:
            if not attribute.startswith("__") and attribute in dangerRating_json:
                if attributes[attribute] in {str, datetime, list, int}:
                    setattr(self, attribute, dangerRating_json[attribute])
                elif attribute == "elevation":
                    for elevation_attribute in dangerRating_json[attribute]:
                        setattr(
                            self.elevation,
                            elevation_attribute,
                            dangerRating_json[attribute][elevation_attribute],
                        )


class AvalancheProblem:
    """
    Describes the Avalanche Problem
    """

    problemType: str
    """problem type as standardized descriptive text"""
    elevation: Elevation
    aspects: list
    terrainFeature: str
    validTimePeriod: str  # Should be 'all_day', 'earlier' and 'later'

    def __init__(
        # pylint: disable=too-many-arguments
        self,
        problemType=None,
        comment=None,
        dangerRating_json=None,
        dangerRating=None,
        aspects=None,
        elevation=None,
        terrainFeature=None,
    ) -> None:
        self.aspects = []
        self.elevation = Elevation()
        if not problemType is None:
            self.problemType = problemType
        if not comment is None:
            self.terrainFeature = comment
        if not terrainFeature is None:
            self.terrainFeature = terrainFeature
        if not dangerRating is None:  # Compatibility with older parsers, deprecated
            self.elevation = dangerRating.elevation
            self.aspects = dangerRating.aspect
        if (
            not dangerRating_json is None
        ):  # Compatibility with older parsers, deprecated
            dangerRating = dangerRating.from_json(dangerRating_json)
            self.elevation = dangerRating.elevation
            self.aspects = dangerRating.aspect
        if not aspects is None:
            self.aspects = aspects
        if not elevation is None:
            self.elevation = elevation

    def add_problemType(self, problem_type_text):
        """
        All problem type texts in pre CAAMLv6 need a post processing to match the new standard
        All new problem texts contain a unterscore and can be differentiated by that
        """
            if "new" in problem_type_text:
                problem_type_text = "new_snow"
        elif "drift" in problem_type_text or "wind" in problem_type_text:
            problem_type_text = "wind_slab"
            elif "old" in problem_type_text or "persistent" in problem_type_text:
                problem_type_text = "persistent_weak_layers"
            elif "wet" in problem_type_text:
                problem_type_text = "wet_snow"
            elif "gliding" in problem_type_text:
                problem_type_text = "gliding_snow"
            elif "favourable" in problem_type_text:
                problem_type_text = "favourable_situation"
        self.problemType = problem_type_text
        return self


class Tendency:
    """
    Describes the Tendency
    """

    tendencyType: str
    """string contains decreasing, steady or increasing"""
    validTime: ValidTime
    """valid time interval for tendency"""
    tendencyComment: str
    """tendency comment"""

    def __init__(
        self, tendencyType=None, validTime_json=None, tendencyComment=None
    ) -> None:
        self.validTime = ValidTime()
        if not validTime_json is None and not len(validTime_json) == 0:
            self.validTime = ValidTime(
                validTime_json["startTime"], validTime_json["endTime"]
            )
        if not tendencyType is None:
            self.tendencyType = tendencyType
        if not tendencyComment is None:
            self.tendencyComment = tendencyComment


@dataclass
class Region:
    """
    Describes a Region
    """

    regionID: str
    name: typing.Optional[str] = None


@dataclass
class Texts:
    """
    Describes Texts in the Bulletin with highlights and comment
    """

    highlights: typing.Optional[str] = None
    comment: typing.Optional[str] = None


class AvaBulletin:
    # pylint: disable=too-many-instance-attributes
    """
    Class for the AvaBulletin
    Follows partly CAAMLv6 caaml:BulletinType
    """

    bulletinID: str
    """ID of the Bulletin"""
    reportLang: str
    """language of the Bulletin"""
    regions: typing.List[Region]
    """list of Regions, where this Report is valid"""
    publicationTime: datetime
    """Date of Bulletin"""
    validTime: ValidTime
    """Valid TimeInterval of the Bulletin"""
    source: Source

    """Details about the Bulletin Provider"""
    dangerRatings: typing.List[DangerRating]
    """avalanche danger rating"""
    avalancheProblems: typing.List[AvalancheProblem]
    """avalanche problem"""
    tendency: Tendency
    """tendency of the av situation"""
    highlights: str
    """very important note in the report"""
    wxSynopsis: Texts
    """weather forecast"""
    avalancheActivity: Texts
    """avalanche activity"""
    snowpackStructure: Texts
    """avalanche structure """
    travelAdvisory: Texts
    """travel advisory"""
    metaData: MetaData

    customData: typing.Dict

    predecessor_id: str
    """not part of CAAMLv6 (yet)"""

    def __init__(self):
        self.regions = []
        self.validTime = ValidTime()
        self.source = Source()
        self.dangerRatings = []
        self.avalancheProblems = []
        self.tendency = Tendency()
        self.customData = []

    def get_region_list(self):
        """
        returns valid region IDs as list.
        """
        return [r.regionID for r in self.regions]

    def from_json(self, bulletin_json):
        # pylint: disable=too-many-branches
        """
        convert to avaBulletin from JSON
        """
        attributes = AvaBulletin.__dict__["__annotations__"]
        for attribute in attributes:
            if not attribute.startswith("__") and attribute in bulletin_json:
                if attributes[attribute] in {str, datetime, dict}:
                    setattr(self, attribute, bulletin_json[attribute])

                elif (
                    str(attributes[attribute]) == "<class 'avacore.avabulletin.Texts'>"
                ):
                    highlights = None
                    comments = None
                    if hasattr(bulletin_json[attribute], "highlights"):
                        highlights = bulletin_json[attribute]["highlights"]
                    if hasattr(bulletin_json[attribute], "comment"):
                        highlights = bulletin_json[attribute]["comment"]
                    setattr(self, attribute, Texts(highlights, comments))

                elif attribute == "regions":
                    for region in bulletin_json[attribute]:
                        self.regions.append(
                            Region(region.get("regionID"), region.get("name"))
                        )

                elif attribute == "dangerRatings":
                    for dangerRating_json in bulletin_json[attribute]:
                        dangerRating = DangerRating()
                        dangerRating.from_json(dangerRating_json)
                        self.dangerRatings.append(dangerRating)

                elif attribute == "avalancheProblems":
                    for avalancheProblem_json in bulletin_json[attribute]:
                        avalancheProblem = AvalancheProblem(
                            problemType=avalancheProblem_json.get("problemType"),
                            comment=avalancheProblem_json.get("comment"),
                            dangerRating_json=avalancheProblem_json.get("dangerRating"),
                        )
                        self.avalancheProblems.append(avalancheProblem)

                elif attribute == "validTime":
                    self.validTime = ValidTime(
                        bulletin_json[attribute]["startTime"],
                        bulletin_json[attribute]["endTime"],
                    )

                elif attribute == "tendency":
                    self.tendency = Tendency(
                        bulletin_json[attribute].get("tendencyType"),
                        bulletin_json[attribute].get("validTime"),
                        bulletin_json[attribute].get("tendencyComment"),
                    )

                elif attribute == "source":
                    if hasattr(bulletin_json[attribute], "provider"):
                        self.source = Source(
                            provider=bulletin_json[attribute]["provider"]
                        )
                    elif hasattr(bulletin_json[attribute], "person"):
                        self.source = Source(person=bulletin_json[attribute]["website"])

                elif attribute == "customData":
                    self.customData = bulletin_json[attribute]

                else:
                    print(
                        "Not handled Attribute:",
                        attribute,
                        attributes[attribute],
                        type(attributes[attribute]),
                    )

    def main_date(self) -> date:
        """
        Returns Main validity date of Report
        """
        validityDate: datetime = self.validTime.startTime
        if validityDate.hour >= 15:
            validityDate = validityDate + timedelta(days=1)

        return validityDate.date()

    def main_dates(self) -> typing.Generator[date, typing.Any, typing.Any]:
        """
        Returns Main validity dates of Report
        """
        validityDate: datetime = self.validTime.startTime

        if validityDate.hour >= 15:
            validityDate = validityDate + timedelta(days=1)

        while True:
            yield validityDate.date()
            distance = self.validTime.endTime - validityDate
            validityDate = validityDate + timedelta(days=1)
            if distance < timedelta(days=1):
                break
            if distance < timedelta(days=2) and validityDate.hour <= 12:
                break

    @staticmethod
    def prettify_out(text):
        """
        Prettified output for text elements
        """
        print(
            "\n".join(
                textwrap.wrap(
                    text, width=60, initial_indent="╟─ ", subsequent_indent="║  "
                )
            )
        )

    def print_if_attr_exists(self, element, attribute):
        """
        Print text element if Attribute exists
        """
        if hasattr(self, element):
            if hasattr(getattr(self, element), attribute):
                if not getattr(getattr(self, element), attribute) is None:
                    self.prettify_out(
                        element
                        + " "
                        + attribute.capitalize()
                        + ": "
                        + getattr(getattr(self, element), attribute)
                    )

    def cli_out(self):
        """
        Terminal output on CLI
        """
        print("╔═════ AvaReport ══════════════════════════════════════════")
        print("║ Bulletin:            ", self.bulletinID)
        if hasattr(self, "predecessor_id"):
            print("║ This is PM-Report to:", self.predecessor_id)
        print("║ Report from:         ", self.publicationTime)
        print("║ Valid from:          ", self.validTime.startTime)
        print("║ Valid to:            ", self.validTime.endTime)
        print("║ Valid for:")
        for region in self.regions:
            print("║ ├─ ", region.regionID)

        print("╟───── Danger Rating")
        for dangerRating in self.dangerRatings:
            print(
                "║ ",
                dangerRating.validTimePeriod,
                dangerRating.elevation.toString(),
                "➝ :",
                dangerRating.mainValue,
            )

        print("╟───── Av Problems")
        for problem in self.avalancheProblems:
            try:
                print(
                    "║ Problem: ",
                    problem.validTimePeriod,
                    problem.problemType,
                    "\n║    Elevation: ",
                    problem.elevation.toString(),
                    "\n║    Aspects: ",
                    problem.aspects,
                )
            except:  # pylint: disable=bare-except
                print("║ Problem: ", problem.problemType)

        print("╟───── Bulletin Texts ─────")
        if hasattr(self, "highlights"):
            self.prettify_out("Highlights: " + self.highlights)

        self.print_if_attr_exists("avalancheActivity", "highlights")
        self.print_if_attr_exists("avalancheActivity", "comment")

        self.print_if_attr_exists("snowpackStructure", "highlights")
        self.print_if_attr_exists("snowpackStructure", "comment")

        self.print_if_attr_exists("travelAdvisory", "highlights")
        self.print_if_attr_exists("travelAdvisory", "comment")

        self.print_if_attr_exists("wxSynopsis", "highlights")
        self.print_if_attr_exists("wxSynopsis", "comment")

        if hasattr(self.tendency, "tendencyComment"):
            self.prettify_out("tendencyComment: " + self.tendency.tendencyComment)

        print("╚═══════════════════════════════════════════════════════════\n")
