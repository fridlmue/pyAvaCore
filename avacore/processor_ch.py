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
from datetime import timedelta
from typing import Set
import urllib.request
import zipfile
import copy
import dataclasses
import base64
import json
import logging
import re
from zoneinfo import ZoneInfo
from io import BytesIO

from avacore.avabulletins import Bulletins

from avacore.png import png
from avacore.avabulletin import (
    AvaBulletin,
    DangerRating,
    AvalancheProblem,
    Region,
    Texts,
)
from avacore.processor import Processor as AbstractProcessor


class Processor(AbstractProcessor):
    problems = False
    year = ""

    def fetch_files_ch(self):
        """
        Downloads the swiss avalanche zip for the slf app together with the region mapping information
        """
        url = f"https://www.slf.ch/avalanche/mobile/bulletin_{self.local}.zip"
        with urllib.request.urlopen(url) as response:
            logging.info("Fetching %s", url)
            data = response.read()
            self.raw_data = BytesIO(data)
            self.raw_data_format = "zip"

    @staticmethod
    def get_prone_locations(img_text):
        """
        Extract dangerous aspects from png
        """
        imgdata = base64.b64decode(img_text)
        png_data = png.Reader(bytes=imgdata)

        _, _, px, _ = png_data.read()

        px_list = list(px)

        aspects = []

        if px_list[20][129] == 0:
            # aspects.append('NNE')
            aspects = append_to_list(aspects, "N")
            aspects = append_to_list(aspects, "NE")
        if px_list[25][145] == 0:
            # aspects.append('ENE')
            aspects = append_to_list(aspects, "NE")
            aspects = append_to_list(aspects, "E")
        if px_list[31][145] == 0:
            # aspects.append('ESE')
            aspects = append_to_list(aspects, "E")
            aspects = append_to_list(aspects, "SE")
        if px_list[36][129] == 0:
            # aspects.append('SSE')
            aspects = append_to_list(aspects, "SE")
            aspects = append_to_list(aspects, "S")
        if px_list[36][101] == 0:
            # aspects.append('SSW')
            aspects = append_to_list(aspects, "S")
            aspects = append_to_list(aspects, "SW")
        if px_list[31][77] == 0:
            # aspects.append('WSW')
            aspects = append_to_list(aspects, "SW")
            aspects = append_to_list(aspects, "W")
        if px_list[25][77] == 0:
            # aspects.append('WNW')
            aspects = append_to_list(aspects, "W")
            aspects = append_to_list(aspects, "NW")
        if px_list[20][101] == 0:
            # aspects.append('NNW')
            aspects = append_to_list(aspects, "NW")
            aspects = append_to_list(aspects, "N")

        return aspects

    @staticmethod
    def clean_html_string(to_clean):
        """
        Removes or replaces unwanted (HTML control) sequences from String
        """
        to_clean = re.sub(
            r'(\<div class="header-5-weather"\>.*\<\/div\>)', r"§newLine§\1:", to_clean
        )
        to_clean = re.sub(r"(?=\<div)(.|\n)*?(\>)", "", to_clean)
        to_clean = re.sub(r'">', "", to_clean)
        to_clean = re.sub(r"</div>", "", to_clean)
        to_clean = re.sub(" +", " ", to_clean)
        to_clean = re.sub(r"(\n\s*)+\n", "", to_clean)
        to_clean = re.sub(r"\A\s+", "", to_clean)
        to_clean = re.sub(r"\n", "", to_clean)
        to_clean = re.sub(r"<br \/>", "\n", to_clean)
        to_clean = re.sub(r"<br>", "\n", to_clean)
        to_clean = re.sub(r"<\/ul>", "\n", to_clean)
        to_clean = re.sub(r'<ul class=\\"bullet-list-indent', "", to_clean)
        to_clean = re.sub(r'<li class=\\"bullet-list-item', "- ", to_clean)
        to_clean = re.sub(r"\\<\/li>", "\n", to_clean)
        to_clean = re.sub(r"§newLine§", "\n", to_clean)
        return to_clean.strip()

    def process_bulletin(self, region_id) -> Bulletins:
        """
        Download the reports for CH
        """
        # pylint: disable=too-many-locals
        # pylint: disable=too-many-branches
        # pylint: disable=too-many-statements

        reports = []
        final_reports = Bulletins()

        if not isinstance(self.raw_data, BytesIO):
            self.fetch_files_ch()

        zip_path = zipfile.Path(self.raw_data)

        gk_region2pdf = {}
        for p in zip_path.joinpath("1").iterdir():
            if str(p.at).startswith("1/gk1_dst"):
                png_data = png.Reader(bytes=p.read_bytes())
                _, _, px, info = png_data.read()
                planes = info["planes"]
                px_list = list(px)
                for region in regions:
                    b = px_list[region.y][region.x * planes : (region.x + 1) * planes]
                    if sum(b) > 0:
                        bid = str(p.at).removeprefix("1/gk1_dst")[:8]
                        gk_region2pdf[region.id] = bid
        if zip_path.joinpath("2").is_dir():
            for p in zip_path.joinpath("2").iterdir():
                if str(p.at).startswith("2/gk1_dst"):
                    png_data = png.Reader(bytes=p.read_bytes())
                    _, _, px, info = png_data.read()
                    planes = info["planes"]
                    px_list = list(px)
                    for region in regions:
                        b = px_list[region.y][region.x * planes : (region.x + 1) * planes]
                        if sum(b) > 0:
                            bid = str(p.at).removeprefix("1/gk1_dst")[:8]
                            gk_region2pdf[region.id] = bid

        if True:

            # Receives validity information from text.json
            with zip_path.joinpath("text.json").open(encoding="utf8") as fp:
                data = json.load(fp)

            # region_id = region_id[-4:]

            common_report = AvaBulletin()

            begin_end_match = re.compile(
                r"Edition: (?P<begin_date>[0-9.]+), (?P<begin_time>[0-9:]+) "
                r"Next update: (?P<end_date>[0-9.]+), (?P<end_time>[0-9:]+)"
            ).match(data["validity"])

            date_time_now = datetime.now()

            year = self.year or str(date_time_now.year)
            tzinfo = ZoneInfo("Europe/Zurich")

            common_report.publicationTime = datetime.strptime(
                f"{year}-{begin_end_match.group('begin_date')}, {begin_end_match.group('begin_time')}",
                "%Y-%d.%m., %H:%M",
            ).replace(tzinfo=tzinfo)
            common_report.validTime.startTime = common_report.publicationTime
            if common_report.validTime.startTime.hour == 17:
                common_report.validTime.endTime = (
                    common_report.validTime.startTime + timedelta(days=1)
                )
            elif common_report.validTime.startTime.hour == 8:
                common_report.validTime.endTime = (
                    common_report.validTime.startTime + timedelta(hours=9)
                )
            else:  # Shourld not happen
                common_report.validTime.endTime = datetime.strptime(
                    str(date_time_now.year) + "-" + end[end.find(":") + 2 :],
                    "%Y-%d.%m., %H:%M",
                ).replace(tzinfo=tzinfo)

            common_report.avalancheActivity = Texts(highlights=data["flash"])

            text = zip_path.joinpath("sdwetter.html").read_text(encoding="utf-8")
            text = text.split('<div class="footer-meteo-mobile')[0]
            segments = text.split("popover-flag")

            wxSynopsis = Texts()

            for segment in segments[1:]:
                outlook = None
                if "Outlook" in segment or "Tendenz" in segment:
                    outlook = segment.split('<div class="snow-and-weather-block">')[1]
                segment = segment.split('<div class="snow-and-weather-block">')[0]
                segment = self.clean_html_string(segment)

                if "popover-snowpack" in segment:
                    common_report.snowpackStructure = Texts(
                        comment=segment.split("popover-snowpack ")[1]
                    )
                if "popover-actual-weather" in segment:
                    wxSynopsis.comment = segment.split("popover-actual-weather ")[1]
                if "popover-weather-forecast" in segment:
                    wxSynopsis.comment += (
                        "\n" + segment.split("popover-weather-forecast ")[1]
                    )
                # if outlook:
                #     common_report.tendency.tendencyComment = self.clean_html_string(
                #         outlook.split("</span>")[1]
                #     )

            common_report.wxSynopsis = wxSynopsis

            bulletinIDs = []
            bulletin_combinations: Set[AvaBulletin] = set()
            # Receives the ID of the report that matches the selected region_id
            if True:
                for regionID, bulletinID in gk_region2pdf.items():
                    bulletin_combinations.add(bulletinID)
                    bulletinID_pm = None
                    if len(bulletinID) > 8:
                        bulletinID_pm = bulletinID[8:]
                        bulletinID = bulletinID[:8]
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
                        if (
                            not bulletinID
                            in reports[bulletinIDs.index(bulletinID_pm)].predecessor_id
                        ):
                            reports[
                                bulletinIDs.index(bulletinID_pm)
                            ].predecessor_id += ("_" + bulletinID)
                    reports[bulletinIDs.index(bulletinID)].regions.append(
                        Region(regionID)
                    )
                    if not bulletinID_pm is None:
                        reports[bulletinIDs.index(bulletinID_pm)].regions.append(
                            Region(regionID)
                        )

            for report in reports:
                # Opens the matching Report-File
                folder = "1"
                if hasattr(report, "predecessor_id"):
                    folder = "2"

                text = (
                    zip_path.joinpath(folder)
                    .joinpath("dst" + report.bulletinID + ".html")
                    .read_text(encoding="utf-8")
                )

                # Isolates the relevant Danger Information
                text_pos = text.find("data-level=") + len("data-level=") + 1

                danger_rating = DangerRating()
                danger_rating.set_mainValue_int(int(text[text_pos : text_pos + 1]))

                report.dangerRatings.append(danger_rating)

                # Isolates the prone location Image
                text_pos = text.find('src="data:image/png;base64,') + len(
                    'src="data:image/png;base64,'
                )
                subtext = text[text_pos:]
                prone_locations_height = subtext[: subtext.find('"')]
                general_problem_locations = []
                if (
                    len(prone_locations_height) < 1000
                ):  # Sometimes no Picture is attached
                    prone_locations_height = "-"
                else:
                    general_problem_locations = self.get_prone_locations(
                        prone_locations_height
                    )

                # Isolates the prone location Text
                text_pos = subtext.find('alt="') + len('alt="')
                subtext = subtext[text_pos:]
                prone_locations_text = subtext[: subtext.find('"')]
                valid_elevation = ""
                if not prone_locations_text == "Content-Type":
                    valid_elevation = "".join(
                        c for c in prone_locations_text if c.isdigit()
                    )
                    # report.dangerRatings[0].elevation = Elevation(valid_elevation)

                report.customData = {
                    "SLF": {
                        "avalancheProneLocation": {
                            "aspects": general_problem_locations,
                            "elevation": valid_elevation,
                        }
                    }
                }

                texts = []

                if 'div class="seperator"' in text:
                    texts = text.split('div class="seperator"')
                else:
                    texts.append(text)

                # avalancheActivity = Texts(comment="")

                # for element in texts:
                #     if "<h5>Danger description</h5>" in element:
                #         avalancheActivityComment = re.search(
                #             r"(?<=\<\/h5><p>)(.|\n)*?(?=\<\/p>)", element
                #         )
                #         avalancheActivity.comment += (
                #             avalancheActivityComment.group(0) + " "
                #         )
                #     elif "No distinct avalanche problem</h4>" in element:
                #         avalancheActivityComment = re.search(
                #             r"(?<=No distinct avalanche problem<\/h4><p>)(.|\n)*?(?=\<\/p>)",
                #             element,
                #         )
                #         avalancheActivity.comment += (
                #             avalancheActivityComment.group(0) + " "
                #         )
                #     elif "</h4><p>" in element:
                #         avalancheActivityComment = re.search(
                #             r"(?<=\<\/h4><p>)(.|\n)*?(?=\<\/p>)", element
                #         )
                #         comment = avalancheActivityComment.group(0)
                #         comment = re.sub(r"\(see.*map\)", "", comment)
                #         avalancheActivity.comment += comment + " "
                #     else:
                #         logging.warning(
                #             "Error parsing avActComment in: %s", report.bulletinID
                #         )

                # avalancheActivity.comment = self.clean_html_string(
                #     avalancheActivity.comment
                # )
                # report.avalancheActivity = avalancheActivity

                if self.problems:
                    # Optional Feature to parse Problems from the swiss Reports
                    for element in texts:
                        avProblem = re.search(r"(?<=><h4>)(.|\n)*?(?=<\/h4>)", element)
                        for word in avProblem.group(0).lower().split():
                            problem_type_text = ""

                            if "new" in word or "neu" in word:
                                problem_type_text = "new_snow"
                            elif (
                                "drifting" in word or "slabs" in word or "trieb" in word
                            ):
                                problem_type_text = "wind_drifted_snow"
                            elif "old" in word or "alt" in word:
                                problem_type_text = "persistent_weak_layers"
                            elif "wet" in word or "nass" in word:
                                problem_type_text = "wet_snow"
                            elif "gliding" in word or "gleit" in word:
                                problem_type_text = "gliding_snow"
                            elif "favourable" in word:
                                problem_type_text = "favourable_situation"

                            if not problem_type_text == "":
                                problem = AvalancheProblem()
                                problem.problemType = problem_type_text
                                report.avalancheProblems.append(problem)

            for combination in bulletin_combinations:
                am_idx = "-"
                pm_idx = "-"

                for idx, report in enumerate(reports):
                    if not hasattr(report, "predecessor_id"):
                        if report.bulletinID in combination:
                            am_idx = idx
                    else:
                        if report.bulletinID in combination:
                            pm_idx = idx
                if pm_idx == "-":
                    final_reports.append(copy.deepcopy(reports[am_idx]))
                else:
                    matched_regions = set(
                        reports[am_idx].get_region_list()
                    ).intersection(set(reports[pm_idx].get_region_list()))
                    combined_report: AvaBulletin = copy.deepcopy(reports[am_idx])

                    combined_report.bulletinID = combination
                    combined_report.regions = []

                    for region in matched_regions:
                        combined_report.regions.append(Region(region))

                    combined_report.dangerRatings = []
                    for dangerRating in reports[am_idx].dangerRatings:
                        adjusted_danger_rating = DangerRating()
                        adjusted_danger_rating.mainValue = dangerRating.mainValue
                        adjusted_danger_rating.validTimePeriod = "earlier"
                        combined_report.dangerRatings.append(adjusted_danger_rating)

                    for dangerRating in reports[pm_idx].dangerRatings:
                        adjusted_danger_rating = DangerRating()
                        adjusted_danger_rating.mainValue = dangerRating.mainValue
                        adjusted_danger_rating.validTimePeriod = "later"
                        combined_report.dangerRatings.append(adjusted_danger_rating)

                    combined_report.avalancheActivity.comment = (
                        reports[am_idx].avalancheActivity.comment
                        + "\n"
                        + reports[pm_idx].avalancheActivity.comment
                    )
                    combined_report.regions.sort(key=lambda r: r.regionID)
                    final_reports.append(combined_report)

        final_reports.bulletins.sort(key=lambda b: b.bulletinID)
        return final_reports


def append_to_list(list_r, element):
    """
    Append Element to List, if element is not yet there
    """
    if not element in list_r:
        list_r.append(element)
        return list_r
    return list_r


@dataclasses.dataclass
class PixelRegion:
    id: str
    x: int
    y: int


regions = [
    PixelRegion(id="CH-1111", x=145, y=274),
    PixelRegion(id="CH-1112", x=173, y=275),
    PixelRegion(id="CH-1113", x=154, y=295),
    PixelRegion(id="CH-1114", x=168, y=311),
    PixelRegion(id="CH-1121", x=181, y=247),
    PixelRegion(id="CH-1122", x=170, y=233),
    PixelRegion(id="CH-1211", x=217, y=208),
    PixelRegion(id="CH-1212", x=256, y=196),
    PixelRegion(id="CH-1213", x=266, y=219),
    PixelRegion(id="CH-1221", x=217, y=234),
    PixelRegion(id="CH-1222", x=195, y=276),
    PixelRegion(id="CH-1223", x=195, y=294),
    PixelRegion(id="CH-1224", x=212, y=269),
    PixelRegion(id="CH-1225", x=217, y=286),
    PixelRegion(id="CH-1226", x=234, y=258),
    PixelRegion(id="CH-1227", x=229, y=278),
    PixelRegion(id="CH-1228", x=219, y=251),
    PixelRegion(id="CH-1231", x=249, y=250),
    PixelRegion(id="CH-1232", x=251, y=269),
    PixelRegion(id="CH-1233", x=272, y=248),
    PixelRegion(id="CH-1234", x=270, y=258),
    PixelRegion(id="CH-1241", x=286, y=224),
    PixelRegion(id="CH-1242", x=285, y=240),
    PixelRegion(id="CH-1243", x=299, y=250),
    PixelRegion(id="CH-1244", x=309, y=224),
    PixelRegion(id="CH-1245", x=315, y=238),
    PixelRegion(id="CH-1246", x=332, y=223),
    PixelRegion(id="CH-1247", x=323, y=252),
    PixelRegion(id="CH-1311", x=139, y=301),
    PixelRegion(id="CH-1312", x=145, y=329),
    PixelRegion(id="CH-2111", x=313, y=179),
    PixelRegion(id="CH-2112", x=310, y=166),
    PixelRegion(id="CH-2121", x=302, y=196),
    PixelRegion(id="CH-2122", x=341, y=201),
    PixelRegion(id="CH-2123", x=317, y=206),
    PixelRegion(id="CH-2124", x=347, y=177),
    PixelRegion(id="CH-2131", x=365, y=149),
    PixelRegion(id="CH-2132", x=393, y=153),
    PixelRegion(id="CH-2133", x=373, y=169),
    PixelRegion(id="CH-2134", x=392, y=179),
    PixelRegion(id="CH-2211", x=378, y=194),
    PixelRegion(id="CH-2212", x=360, y=194),
    PixelRegion(id="CH-2221", x=357, y=221),
    PixelRegion(id="CH-2222", x=385, y=213),
    PixelRegion(id="CH-2223", x=356, y=237),
    PixelRegion(id="CH-2224", x=359, y=249),
    PixelRegion(id="CH-3111", x=418, y=146),
    PixelRegion(id="CH-3112", x=411, y=188),
    PixelRegion(id="CH-3113", x=435, y=177),
    PixelRegion(id="CH-3114", x=414, y=163),
    PixelRegion(id="CH-3211", x=472, y=95),
    PixelRegion(id="CH-3221", x=420, y=124),
    PixelRegion(id="CH-3222", x=462, y=129),
    PixelRegion(id="CH-3223", x=446, y=151),
    PixelRegion(id="CH-3224", x=465, y=173),
    PixelRegion(id="CH-3311", x=485, y=138),
    PixelRegion(id="CH-4111", x=152, y=349),
    PixelRegion(id="CH-4112", x=164, y=358),
    PixelRegion(id="CH-4113", x=176, y=375),
    PixelRegion(id="CH-4114", x=186, y=319),
    PixelRegion(id="CH-4115", x=189, y=342),
    PixelRegion(id="CH-4116", x=201, y=370),
    PixelRegion(id="CH-4121", x=216, y=303),
    PixelRegion(id="CH-4122", x=215, y=333),
    PixelRegion(id="CH-4123", x=220, y=360),
    PixelRegion(id="CH-4124", x=234, y=327),
    PixelRegion(id="CH-4125", x=239, y=351),
    PixelRegion(id="CH-4211", x=257, y=284),
    PixelRegion(id="CH-4212", x=247, y=322),
    PixelRegion(id="CH-4213", x=288, y=273),
    PixelRegion(id="CH-4214", x=283, y=293),
    PixelRegion(id="CH-4215", x=244, y=299),
    PixelRegion(id="CH-4221", x=267, y=323),
    PixelRegion(id="CH-4222", x=254, y=358),
    PixelRegion(id="CH-4223", x=278, y=345),
    PixelRegion(id="CH-4224", x=261, y=373),
    PixelRegion(id="CH-4225", x=283, y=356),
    PixelRegion(id="CH-4231", x=294, y=306),
    PixelRegion(id="CH-4232", x=296, y=330),
    PixelRegion(id="CH-4241", x=311, y=274),
    PixelRegion(id="CH-4242", x=312, y=292),
    PixelRegion(id="CH-4243", x=328, y=257),
    PixelRegion(id="CH-4244", x=331, y=270),
    PixelRegion(id="CH-5111", x=510, y=169),
    PixelRegion(id="CH-5112", x=506, y=185),
    PixelRegion(id="CH-5113", x=545, y=195),
    PixelRegion(id="CH-5121", x=479, y=185),
    PixelRegion(id="CH-5122", x=497, y=203),
    PixelRegion(id="CH-5123", x=528, y=211),
    PixelRegion(id="CH-5124", x=437, y=201),
    PixelRegion(id="CH-5211", x=393, y=222),
    PixelRegion(id="CH-5212", x=390, y=242),
    PixelRegion(id="CH-5214", x=441, y=225),
    PixelRegion(id="CH-5215", x=412, y=234),
    PixelRegion(id="CH-5216", x=431, y=251),
    PixelRegion(id="CH-5221", x=478, y=219),
    PixelRegion(id="CH-5222", x=469, y=237),
    PixelRegion(id="CH-5223", x=458, y=258),
    PixelRegion(id="CH-5231", x=511, y=231),
    PixelRegion(id="CH-5232", x=492, y=247),
    PixelRegion(id="CH-5233", x=485, y=277),
    PixelRegion(id="CH-5234", x=500, y=265),
    PixelRegion(id="CH-6111", x=354, y=269),
    PixelRegion(id="CH-6112", x=374, y=261),
    PixelRegion(id="CH-6113", x=411, y=266),
    PixelRegion(id="CH-6114", x=363, y=293),
    PixelRegion(id="CH-6115", x=399, y=282),
    PixelRegion(id="CH-6121", x=382, y=317),
    PixelRegion(id="CH-6122", x=418, y=317),
    PixelRegion(id="CH-6131", x=408, y=351),
    PixelRegion(id="CH-6132", x=418, y=383),
    PixelRegion(id="CH-6211", x=440, y=274),
    PixelRegion(id="CH-6212", x=440, y=303),
    PixelRegion(id="CH-7111", x=521, y=280),
    PixelRegion(id="CH-7112", x=542, y=275),
    PixelRegion(id="CH-7113", x=537, y=239),
    PixelRegion(id="CH-7114", x=524, y=259),
    PixelRegion(id="CH-7115", x=549, y=253),
    PixelRegion(id="CH-7121", x=588, y=178),
    PixelRegion(id="CH-7122", x=564, y=196),
    PixelRegion(id="CH-7123", x=558, y=214),
    PixelRegion(id="CH-7124", x=594, y=192),
    PixelRegion(id="CH-7125", x=571, y=227),
    PixelRegion(id="CH-7126", x=591, y=216),
    PixelRegion(id="CH-7211", x=499, y=293),
    PixelRegion(id="CH-7221", x=555, y=289),
    PixelRegion(id="CH-7222", x=562, y=308),
    PixelRegion(id="CH-7231", x=595, y=241),
    PixelRegion(id="CH-8111", x=51, y=270),
    PixelRegion(id="CH-8112", x=67, y=239),
    PixelRegion(id="CH-8113", x=108, y=201),
    PixelRegion(id="CH-8114", x=102, y=183),
    PixelRegion(id="CH-8211", x=138, y=164),
    PixelRegion(id="CH-8212", x=165, y=154),
    PixelRegion(id="CH-8213", x=178, y=135),
    PixelRegion(id="CH-8214", x=204, y=113),
    PixelRegion(id="CH-8215", x=238, y=110),
    PixelRegion(id="CH-8216", x=276, y=96),
    PixelRegion(id="CH-8221", x=130, y=151),
    PixelRegion(id="CH-8222", x=159, y=118),
    PixelRegion(id="CH-8223", x=166, y=86),
    PixelRegion(id="CH-8224", x=186, y=108),
    PixelRegion(id="CH-8225", x=220, y=89),
    PixelRegion(id="CH-8226", x=236, y=70),
    PixelRegion(id="CH-8227", x=261, y=85),
    PixelRegion(id="CH-8228", x=270, y=64),
    PixelRegion(id="CH-9111", x=121, y=236),
    PixelRegion(id="CH-9211", x=280, y=126),
    PixelRegion(id="CH-9311", x=404, y=73),
]
