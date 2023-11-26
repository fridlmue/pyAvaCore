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
from dataclasses import dataclass, field
from datetime import datetime, timedelta, date
import re
import typing
from typing import Optional, Any, List, Union
from enum import Enum
import textwrap

from .MetaData import MetaData


class Aspect(Enum):
    """An aspect can be defined as a set of aspects. The aspects are the expositions as in a
    eight part (45°) segments. The allowed aspects are the four main cardinal directions and
    the four intercardinal directions.
    """

    E = "E"
    N = "N"
    NE = "NE"
    NW = "NW"
    S = "S"
    SE = "SE"
    SW = "SW"
    W = "W"
    na = "n/a"


class DangerRatingValue(Enum):
    """Danger rating value, according to EAWS danger scale definition."""

    considerable = "considerable"
    high = "high"
    low = "low"
    moderate = "moderate"
    no_rating = "no_rating"
    no_snow = "no_snow"
    very_high = "very_high"


class ExpectedAvalancheFrequency(Enum):
    """Expected frequency of lowest snowpack stability, according to the EAWS definition. Three
    stage scale (few, some, many).
    """

    few = "few"
    many = "many"
    none = "none"
    some = "some"


class AvalancheProblemType(Enum):
    """Expected avalanche problem, according to the EAWS avalanche problem definition."""

    cornices = "cornices"
    favourable_situation = "favourable_situation"
    gliding_snow = "gliding_snow"
    new_snow = "new_snow"
    no_distinct_avalanche_problem = "no_distinct_avalanche_problem"
    persistent_weak_layers = "persistent_weak_layers"
    wet_snow = "wet_snow"
    wind_slab = "wind_slab"


class ExpectedSnowpackStability(Enum):
    """Snowpack stability, according to the EAWS definition. Four stage scale (very poor, poor,
    fair, good).
    """

    fair = "fair"
    good = "good"
    poor = "poor"
    very_poor = "very_poor"


class ValidTimePeriod(Enum):
    """Valid time period can be used to limit the validity of an element to an earlier or later
    period. It can be used to distinguish danger ratings or avalanche problems.
    """

    all_day = "all_day"
    earlier = "earlier"
    later = "later"


class TendencyType(Enum):
    decreasing = "decreasing"
    increasing = "increasing"
    steady = "steady"


@dataclass
class ValidTime:
    """Valid time defines two ISO 8601 timestamps in UTC or with time zone information.

    Date and Time from and until this bulletin is valid. ISO 8601 Timestamp in UTC or with
    time zone information.
    """

    endTime: Optional[datetime] = None
    startTime: Optional[datetime] = None

    def __init__(
        self,
        startTime: Union[datetime, str, None] = None,
        endTime: Union[datetime, str, None] = None,
    ):
        if isinstance(startTime, str):
            startTime = datetime.fromisoformat(startTime.replace("Z", "+00:00"))
        self.startTime = startTime
        if isinstance(endTime, str):
            endTime = datetime.fromisoformat(endTime.replace("Z", "+00:00"))
        self.endTime = endTime

    @staticmethod
    def from_dict(obj: Any) -> "ValidTime":
        if not obj:
            return None
        assert isinstance(obj, dict)
        return ValidTime(
            startTime=obj.get("startTime"),
            endTime=obj.get("endTime"),
        )


@dataclass
class Person:
    """Details on a person."""

    customData: Any = None
    metaData: Optional[MetaData] = None
    name: Optional[str] = None
    website: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> "Person":
        if not obj:
            return None
        assert isinstance(obj, dict)
        return Person(
            customData=obj.get("customData"),
            metaData=obj.get("metaData"),
            name=obj.get("name"),
            website=obj.get("website"),
        )


@dataclass
class Provider:
    """Information about the bulletin provider. Defines the name, website and/or contactPerson
    (which could be the author) of the issuing AWS.
    """

    customData: Any = None
    contactPerson: Optional[Person] = None
    metaData: Optional[MetaData] = None
    name: Optional[str] = None
    website: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> "Provider":
        if not obj:
            return None
        assert isinstance(obj, dict)
        return Provider(
            customData=obj.get("customData"),
            contactPerson=Person.from_dict(obj.get("contactPerson")),
            metaData=obj.get("metaData"),
            name=obj.get("name"),
            website=obj.get("website"),
        )


@dataclass
class Source:
    """Details about the issuer/AWS of the bulletin.

    Information about the bulletin source. Either as in a person or with a provider element
    to specify details about the AWS.
    """

    person: Optional[Person] = None
    provider: Optional[Provider] = None

    @staticmethod
    def from_dict(obj: Any) -> "Source":
        if not obj:
            return None
        assert isinstance(obj, dict)
        return Source(
            person=Person.from_dict(obj.get("person")),
            provider=Provider.from_dict(obj.get("provider")),
        )


@dataclass
class Elevation:
    """Elevation describes either an elevation range below a certain bound (only upperBound is
    set to a value) or above a certain bound (only lowerBound is set to a value). If both
    values are set to a value, an elevation band is defined by this property. The value uses
    a numeric value, not more detailed than 100m resolution. Additionally to the numeric
    values also 'treeline' is allowed.
    """

    lowerBound: Optional[str] = None
    upperBound: Optional[str] = None

    def auto_select(self, auto_select):
        """
        Auto-Selct from different possible ways of elevation description if it is lower or upper bound.
        """
        if auto_select is not None:
            auto_select = auto_select.replace("Forestline", "treeline")
            auto_select = auto_select.replace("Treeline", "treeline")
            if "Hi" in auto_select:
                self.lowerBound = re.sub(r"ElevationRange_(.+)Hi", r"\1", auto_select)
            if "Lo" in auto_select or "Lw" in auto_select:
                self.upperBound = re.sub(
                    r"ElevationRange_(.+)(Lo|Lw)", r"\1", auto_select
                )
            if "><" in auto_select and len(auto_select) > 2:
                self.lowerBound = re.sub(r"><(.+)", r"\1", auto_select)
                self.upperBound = re.sub(r"><(.+)", r"\1", auto_select)
            elif ">" in auto_select and len(auto_select) > 1:
                self.lowerBound = re.sub(r">(.+)", r"\1", auto_select)
            elif "<" in auto_select and len(auto_select) > 1:
                self.upperBound = re.sub(r"<(.+)", r"\1", auto_select)

    @staticmethod
    def from_dict(obj: Any) -> "Elevation":
        if not obj:
            return None
        assert isinstance(obj, dict)
        return Elevation(
            lowerBound=str(obj.get("lowerBound")) if obj.get("lowerBound") else None,
            upperBound=str(obj.get("upperBound")) if obj.get("upperBound") else None,
        )

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
class DangerRating:
    """Defines a danger rating, its elevation constraints and the valid time period. If
    validTimePeriod or elevation are constrained for a rating, it is expected to define a
    dangerRating for all the other cases.
    """

    mainValue: Optional[DangerRatingValue] = None
    aspects: Optional[List[Aspect]] = None
    elevation: Optional[Elevation] = field(default_factory=Elevation)
    validTimePeriod: ValidTimePeriod = "all_day"
    customData: Any = None
    metaData: Optional[MetaData] = None

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
        return self

    @staticmethod
    def from_dict(obj: typing.Dict) -> "DangerRating":
        if not obj:
            return None
        assert isinstance(obj, dict)
        return DangerRating(
            mainValue=obj.get("mainValue"),
            aspects=obj.get("aspects"),
            elevation=Elevation.from_dict(obj.get("elevation"))
            if obj.get("elevation")
            else Elevation(),
            validTimePeriod=obj.get("validTimePeriod", "all_day"),
            customData=obj.get("customData"),
            metaData=obj.get("metaData"),
        )


@dataclass
class AvalancheProblem:
    """Defines an avalanche problem, its time, aspect, and elevation constraints. A textual
    detail about the affected terrain can be given in the comment field. Also, details about
    the expected avalanche size, snowpack stability and its frequency can be defined. The
    implied danger rating value is optional.
    """

    customData: Any = None
    problemType: Optional[AvalancheProblemType] = None
    aspects: Optional[List[Aspect]] = None
    avalancheSize: Optional[int] = None
    comment: Optional[str] = None
    dangerRatingValue: Optional[DangerRatingValue] = None
    elevation: Optional[Elevation] = None
    frequency: Optional[ExpectedAvalancheFrequency] = None
    metaData: Optional[MetaData] = None
    snowpackStability: Optional[ExpectedSnowpackStability] = None
    validTimePeriod: Optional[ValidTimePeriod] = None

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
        elif "no_distinct" in problem_type_text:
            problem_type_text = "no_distinct_avalanche_problem"
        self.problemType = problem_type_text
        return self

    def add_aspects(self, aspect_from: str, aspect_to: str):
        """Adds aspects in clockwise mode"""
        aspects_list = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"] * 2
        index_from = aspects_list.index(aspect_from.upper())
        index_to = aspects_list.index(aspect_to.upper(), index_from)
        self.aspects = aspects_list[index_from : index_to + 1]
        return self

    @staticmethod
    def from_dict(obj: Any) -> "AvalancheProblem":
        if not obj:
            return None
        assert isinstance(obj, dict)
        return AvalancheProblem(
            customData=obj.get("customData"),
            problemType=obj.get("problemType"),
            aspects=obj.get("aspects", []),
            avalancheSize=int(obj.get("avalancheSize"))
            if obj.get("avalancheSize")
            else None,
            comment=obj.get("comment"),
            dangerRatingValue=obj.get("dangerRatingValue"),
            elevation=Elevation.from_dict(obj.get("elevation")),
            frequency=obj.get("frequency"),
            metaData=obj.get("metaData"),
            snowpackStability=obj.get("snowpackStability"),
            validTimePeriod=obj.get("validTimePeriod"),
        )


@dataclass
class Tendency:
    """Texts element with highlight and comment for the avalanche activity.

    Texts contains a highlight and a comment string, where highlights could also be described
    as a kind of headline for the longer comment. For text-formatting the HTML-Tags <br/> for
    a new line, (<ul>,<ul/>) and (<li>,<li/>) for lists, (<h1>,<h1/>) to (<h6>,<h6/>) for
    headings and (<b>,</b>) for a bold text are allowed.

    Texts element with highlight and comment for details on the snowpack structure.

    Texts element with highlight and comment for travel advisory.

    Texts element with highlight and comment for weather forecast information.

    Texts element with highlight and comment for weather review information.

    Describes the expected tendency of the development of the avalanche situation for a
    defined time period.
    """

    customData: Any = None
    comment: Optional[str] = None
    highlights: Optional[str] = None
    metaData: Optional[MetaData] = None
    tendencyType: Optional[TendencyType] = None
    validTime: Optional[ValidTime] = None

    @staticmethod
    def from_dict(obj: Any) -> "Tendency":
        if not obj:
            return None
        assert isinstance(obj, dict)
        return Tendency(
            customData=obj.get("customData"),
            comment=obj.get("comment"),
            highlights=obj.get("highlights"),
            metaData=obj.get("metaData"),
            tendencyType=obj.get("tendencyType"),
            validTime=ValidTime.from_dict(obj.get("validTime")),
        )


@dataclass
class Region:
    """Region element describes a (micro) region. The regionID follows the EAWS schema. It is
    recommended to have the region shape's files with the same IDs in
    gitlab.com/eaws/eaws-regions. Additionally, the region name can be added.
    """

    regionID: Optional[str] = None
    name: Optional[str] = None
    metaData: Optional[MetaData] = None
    customData: Any = None

    @staticmethod
    def from_dict(obj: Any) -> "Region":
        if not obj:
            return None
        assert isinstance(obj, dict)
        return Region(
            customData=obj.get("customData"),
            regionID=obj.get("regionID"),
            metaData=obj.get("metaData"),
            name=obj.get("name"),
        )


@dataclass
class Texts:
    """Texts element with highlight and comment for the avalanche activity.

    Texts contains a highlight and a comment string, where highlights could also be described
    as a kind of headline for the longer comment. For text-formatting the HTML-Tags <br/> for
    a new line, (<ul>,<ul/>) and (<li>,<li/>) for lists, (<h1>,<h1/>) to (<h6>,<h6/>) for
    headings and (<b>,</b>) for a bold text are allowed.

    Texts element with highlight and comment for details on the snowpack structure.

    Texts element with highlight and comment for travel advisory.

    Texts element with highlight and comment for weather forecast information.

    Texts element with highlight and comment for weather review information.
    """

    comment: Optional[str] = None
    highlights: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> "Texts":
        if not obj:
            return None
        assert isinstance(obj, dict)
        return Texts(
            comment=obj.get("comment"),
            highlights=obj.get("highlights"),
        )


@dataclass
class AvaBulletin:
    """Avalanche Bulletin valid for a given set of regions."""

    avalancheActivity: Optional[Texts] = None
    """Collection of Avalanche Problem elements for this bulletin."""
    avalancheProblems: Optional[List[AvalancheProblem]] = field(default_factory=list)
    """Unique ID for the bulletin."""
    bulletinID: Optional[str] = None
    """Collection of Danger Rating elements for this bulletin."""
    customData: Any = None
    """Texts element with highlight and comment for the avalanche activity."""
    dangerRatings: Optional[List[DangerRating]] = field(default_factory=list)
    """Contains an optional short text to highlight an exceptionally dangerous situation."""
    highlights: Optional[str] = None
    """Two-letter language code (ISO 639-1)."""
    lang: Optional[str] = None
    metaData: Optional[MetaData] = None
    """Time and date when the next bulletin will be published by the AWS to the Public. ISO 8601
    timestamp in UTC or with time zone information.
    """
    nextUpdate: Optional[datetime] = None
    """Time and date when the bulletin was issued by the AWS to the Public. ISO 8601 timestamp
    in UTC or with time zone information.
    """
    publicationTime: Optional[datetime] = None
    """Collection of region elements for which this bulletin is valid."""
    regions: Optional[List[Region]] = field(default_factory=list)
    """Texts element with highlight and comment for details on the snowpack structure."""
    snowpackStructure: Optional[Texts] = None
    """Details about the issuer/AWS of the bulletin."""
    source: Optional[Source] = field(default_factory=Source)
    """Tendency element for a detailed description of the expected avalanche situation tendency
    after the bulletin's period of validity.
    """
    tendency: Optional[List[Tendency]] = field(default_factory=list)
    """Texts element with highlight and comment for travel advisory."""
    travelAdvisory: Optional[Texts] = None
    """Flag if bulletin is unscheduled or not."""
    unscheduled: Optional[bool] = None
    """Date and Time from and until this bulletin is valid. ISO 8601 Timestamp in UTC or with
    time zone information.
    """
    validTime: Optional[ValidTime] = field(default_factory=ValidTime)
    """Texts element with highlight and comment for weather forecast information."""
    weatherForecast: Optional[Texts] = None
    """Texts element with highlight and comment for weather review information."""
    weatherReview: Optional[Texts] = None

    def get_region_list(self):
        """
        returns valid region IDs as list.
        """
        return [r.regionID for r in self.regions]

    @staticmethod
    def from_dict(obj: Any) -> "AvaBulletin":
        if not obj:
            return None
        assert isinstance(obj, dict)
        return AvaBulletin(
            avalancheActivity=Texts.from_dict(obj.get("avalancheActivity")),
            avalancheProblems=[
                AvalancheProblem.from_dict(p) for p in obj.get("avalancheProblems", [])
            ],
            bulletinID=obj.get("bulletinID"),
            customData=obj.get("customData"),
            dangerRatings=[
                DangerRating.from_dict(r) for r in obj.get("dangerRatings", [])
            ],
            highlights=obj.get("highlights"),
            lang=obj.get("lang"),
            metaData=obj.get("metaData"),
            nextUpdate=datetime.fromisoformat(
                obj.get("nextUpdate").replace("Z", "+00:00")
            )
            if obj.get("nextUpdate")
            else None,
            publicationTime=datetime.fromisoformat(
                obj.get("publicationTime").replace("Z", "+00:00")
            )
            if obj.get("publicationTime")
            else None,
            regions=[Region.from_dict(r) for r in obj.get("regions", [])],
            snowpackStructure=Texts.from_dict(obj.get("snowpackStructure")),
            source=Source.from_dict(obj.get("source"))
            if obj.get("source")
            else Source(),
            tendency=[Tendency.from_dict(t) for t in obj.get("tendency", [])],
            travelAdvisory=Texts.from_dict(obj.get("travelAdvisory")),
            unscheduled=obj.get("unscheduled"),
            validTime=ValidTime.from_dict(obj.get("validTime"))
            if obj.get("validTime")
            else ValidTime(),
            weatherForecast=Texts.from_dict(obj.get("weatherForecast")),
            weatherReview=Texts.from_dict(obj.get("weatherReview")),
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
                if getattr(getattr(self, element), attribute) is not None:
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
            except:
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

        self.print_if_attr_exists("weatherForecast", "highlights")
        self.print_if_attr_exists("weatherForecast", "comment")

        self.print_if_attr_exists("weatherReview", "highlights")
        self.print_if_attr_exists("weatherReview", "comment")

        if hasattr(self.tendency, "tendencyComment"):
            for t in self.tendency:
                self.prettify_out("tendencyComment: " + t.tendencyComment)

        print("╚═══════════════════════════════════════════════════════════\n")
