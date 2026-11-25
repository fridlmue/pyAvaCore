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
import html as html_lib
import re
from zoneinfo import ZoneInfo

from avacore.avabulletin import (
    AvaBulletin,
    AvalancheProblem,
    DangerRating,
    Elevation,
    Region,
    Tendency,
    Texts,
    ValidTime,
)
from avacore.avabulletins import Bulletins
from avacore.processor import HtmlProcessor

ASPECTS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]

PERIODS = {
    "allday": "all_day",
}


class Processor(HtmlProcessor):
    fetch_time_dependant = True

    def process_bulletin(self, region_id) -> Bulletins:
        html = self._fetch_url(self.url, {})
        self.raw_data = html
        self.raw_data_format = "html"
        return self.parse_html(region_id, html)

    def parse_html(self, region_id, html: str) -> Bulletins:
        article = re.search(
            r"<article class='topr-bulletin'.*?</article>", html, flags=re.DOTALL
        )
        if article is None:
            raise ValueError(f"Could not find TOPR bulletin in {self.url}")
        article = article.group()

        def find(pattern: str) -> str:
            match = re.search(pattern, article, flags=re.DOTALL)
            if match is None:
                raise ValueError(f"Could not find {pattern!r} in TOPR bulletin")
            return html_lib.unescape(match.group(1).strip())

        def parse_time(value: str) -> datetime:
            return datetime.fromisoformat(value).replace(
                tzinfo=ZoneInfo("Europe/Warsaw")
            )

        bulletin = AvaBulletin()
        bulletin.regions = [Region(regionID=region_id)]
        bulletin.validTime = ValidTime(
            startTime=parse_time(find(r"Obowiązuje od:</span>\s*<strong>([^<]+)")),
            endTime=parse_time(find(r"<strong>Obowiązuje do:</strong>([^<]+)")),
        )
        bulletin.publicationTime = parse_time(
            find(r"<strong>Data publikacji:</strong>([^<]+)")
        )
        bulletin.bulletinID = f"{region_id}_{bulletin.validTime.endTime.isoformat()}"

        definitions = [
            html_lib.unescape(text.strip())
            for text in re.findall(
                r"<span class='topr-mobile-def-label'>[^<]*</span>([^<]*)</p>",
                article,
            )
        ]
        if len(definitions) == 3:
            bulletin.snowpackStructure = Texts(comment=" ".join(definitions[:2]))
            bulletin.travelAdvisory = Texts(comment=definitions[2])

        bulletin.avalancheActivity = Texts(
            comment=find(r"<div class='avalanche-comment'><h4>[^<]*</h4><p>(.*?)</p>")
        )

        tendency = find(r"<span class='tendency-meta'>.*?</svg><span>([^<]+)</span>")
        bulletin.tendency = [
            Tendency(
                comment=tendency,
                tendencyType="steady" if "bez zmian" in tendency else None,
            )
        ]

        problem_list = article[article.index("<div class='problem-list'>") :]
        periods = list(re.finditer(r"<div class='(\w+)-problems'>", problem_list))
        for period, next_period in zip(periods, periods[1:] + [None]):
            if period.group(1) not in PERIODS:
                raise ValueError(f"Unknown TOPR period {period.group(1)!r}")
            valid_time_period = PERIODS[period.group(1)]
            section = problem_list[
                period.end() : next_period.start() if next_period else None
            ]

            danger_icon = re.search(
                r"<div class='period-danger-icon'>(.*?)</svg>", section, re.DOTALL
            ).group(1)
            values = [
                int(v)
                for v in re.findall(r'class="rating-text"[^>]*>(\d)<', danger_icon)
            ]
            if len(set(values)) == 1:
                rating = DangerRating(validTimePeriod=valid_time_period)
                rating.set_mainValue_int(values[0])
                bulletin.dangerRatings.append(rating)
            else:
                bound = re.search(r'class="elevation-text"[^>]*>(\d+)<', danger_icon)
                for value, elevation in zip(
                    values,
                    [
                        Elevation(lowerBound=bound.group(1)),
                        Elevation(upperBound=bound.group(1)),
                    ],
                ):
                    rating = DangerRating(
                        validTimePeriod=valid_time_period, elevation=elevation
                    )
                    rating.set_mainValue_int(value)
                    bulletin.dangerRatings.append(rating)

            for row in section.split("<div class='problem-row'>")[1:]:
                problem_type = re.search(r"data-problem='prb_(\w+?)_topr", row)
                if problem_type is None:
                    continue
                problem = AvalancheProblem(validTimePeriod=valid_time_period)
                problem.add_problemType(problem_type.group(1))

                elevation_svg, compass_svg = row.split(
                    "<div class='problem-svg compass'"
                )[:2]
                upper, lower = re.findall(
                    r'<path d="M [^"]*" class="(elevation-\w+)"', elevation_svg
                )[:2]
                if upper != lower:
                    bound = re.search(
                        r'class="elevation-text"[^>]*>(\d+)<', elevation_svg
                    )
                    bound = bound.group(1) if bound else "treeline"
                    problem.elevation = (
                        Elevation(lowerBound=bound)
                        if upper == "elevation-active"
                        else Elevation(upperBound=bound)
                    )

                sectors = re.findall(r'<path d="m[^"]*" class="([^"]+)"', compass_svg)
                problem.aspects = [
                    aspect
                    for aspect, sector in zip(ASPECTS, sectors)
                    if sector == "exposure-active"
                ]
                bulletin.avalancheProblems.append(problem)

        return Bulletins(bulletins=[bulletin])
