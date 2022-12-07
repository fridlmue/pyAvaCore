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

        if zip_path.joinpath("gk_region2pdf.txt").is_file():

            # Receives validity information from text.json
            with zip_path.joinpath("text.json").open(encoding="utf8") as fp:
                data = json.load(fp)

            # region_id = region_id[-4:]

            common_report = AvaBulletin()

            begin, end = data["validity"].split("/")

            date_time_now = datetime.now()

            year = self.year or str(date_time_now.year)
            tzinfo = ZoneInfo("Europe/Zurich")

            common_report.publicationTime = datetime.strptime(
                year + "-" + begin[begin.find(":") + 2 : -1], "%Y-%d.%m., %H:%M"
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
                if outlook:
                    common_report.tendency.tendencyComment = self.clean_html_string(
                        outlook.split("</span>")[1]
                    )

            common_report.wxSynopsis = wxSynopsis

            bulletinIDs = []
            bulletin_combinations: Set[AvaBulletin] = set()
            # Receives the ID of the report that matches the selected region_id
            with zip_path.joinpath("gk_region2pdf.txt").open(encoding="utf8") as fp:
                for line in fp:
                    bulletinID = line.split("_")[5][:-5]
                    bulletin_combinations.add(bulletinID)
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
                        if (
                            not bulletinID
                            in reports[bulletinIDs.index(bulletinID_pm)].predecessor_id
                        ):
                            reports[
                                bulletinIDs.index(bulletinID_pm)
                            ].predecessor_id += ("_" + bulletinID)
                    reports[bulletinIDs.index(bulletinID)].regions.append(
                        Region("CH-" + line[:4])
                    )
                    if not bulletinID_pm is None:
                        reports[bulletinIDs.index(bulletinID_pm)].regions.append(
                            Region("CH-" + line[:4])
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

                avalancheActivity = Texts(comment="")

                for element in texts:
                    if "<h5>Danger description</h5>" in element:
                        avalancheActivityComment = re.search(
                            r"(?<=\<\/h5><p>)(.|\n)*?(?=\<\/p>)", element
                        )
                        avalancheActivity.comment += (
                            avalancheActivityComment.group(0) + " "
                        )
                    elif "No distinct avalanche problem</h4>" in element:
                        avalancheActivityComment = re.search(
                            r"(?<=No distinct avalanche problem<\/h4><p>)(.|\n)*?(?=\<\/p>)",
                            element,
                        )
                        avalancheActivity.comment += (
                            avalancheActivityComment.group(0) + " "
                        )
                    elif "</h4><p>" in element:
                        avalancheActivityComment = re.search(
                            r"(?<=\<\/h4><p>)(.|\n)*?(?=\<\/p>)", element
                        )
                        comment = avalancheActivityComment.group(0)
                        comment = re.sub(r"\(see.*map\)", "", comment)
                        avalancheActivity.comment += comment + " "
                    else:
                        logging.warning(
                            "Error parsing avActComment in: %s", report.bulletinID
                        )

                avalancheActivity.comment = self.clean_html_string(
                    avalancheActivity.comment
                )
                report.avalancheActivity = avalancheActivity

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


regions = [{'X': 145, 'Y': 274, 'id': 'CH-1111'},
    {'X': 173, 'Y': 275, 'id': 'CH-1112'},
    {'X': 154, 'Y': 295, 'id': 'CH-1113'},
    {'X': 168, 'Y': 311, 'id': 'CH-1114'},
    {'X': 181, 'Y': 247, 'id': 'CH-1121'},
    {'X': 170, 'Y': 233, 'id': 'CH-1122'},
    {'X': 217, 'Y': 208, 'id': 'CH-1211'},
    {'X': 256, 'Y': 196, 'id': 'CH-1212'},
    {'X': 266, 'Y': 219, 'id': 'CH-1213'},
    {'X': 217, 'Y': 234, 'id': 'CH-1221'},
    {'X': 195, 'Y': 276, 'id': 'CH-1222'},
    {'X': 195, 'Y': 294, 'id': 'CH-1223'},
    {'X': 212, 'Y': 269, 'id': 'CH-1224'},
    {'X': 217, 'Y': 286, 'id': 'CH-1225'},
    {'X': 234, 'Y': 258, 'id': 'CH-1226'},
    {'X': 229, 'Y': 278, 'id': 'CH-1227'},
    {'X': 219, 'Y': 251, 'id': 'CH-1228'},
    {'X': 249, 'Y': 250, 'id': 'CH-1231'},
    {'X': 251, 'Y': 269, 'id': 'CH-1232'},
    {'X': 272, 'Y': 248, 'id': 'CH-1233'},
    {'X': 270, 'Y': 258, 'id': 'CH-1234'},
    {'X': 286, 'Y': 224, 'id': 'CH-1241'},
    {'X': 285, 'Y': 240, 'id': 'CH-1242'},
    {'X': 299, 'Y': 250, 'id': 'CH-1243'},
    {'X': 309, 'Y': 224, 'id': 'CH-1244'},
    {'X': 315, 'Y': 238, 'id': 'CH-1245'},
    {'X': 332, 'Y': 223, 'id': 'CH-1246'},
    {'X': 323, 'Y': 252, 'id': 'CH-1247'},
    {'X': 139, 'Y': 301, 'id': 'CH-1311'},
    {'X': 145, 'Y': 329, 'id': 'CH-1312'},
    {'X': 313, 'Y': 179, 'id': 'CH-2111'},
    {'X': 310, 'Y': 166, 'id': 'CH-2112'},
    {'X': 302, 'Y': 196, 'id': 'CH-2121'},
    {'X': 341, 'Y': 201, 'id': 'CH-2122'},
    {'X': 317, 'Y': 206, 'id': 'CH-2123'},
    {'X': 347, 'Y': 177, 'id': 'CH-2124'},
    {'X': 365, 'Y': 149, 'id': 'CH-2131'},
    {'X': 393, 'Y': 153, 'id': 'CH-2132'},
    {'X': 373, 'Y': 169, 'id': 'CH-2133'},
    {'X': 392, 'Y': 179, 'id': 'CH-2134'},
    {'X': 378, 'Y': 194, 'id': 'CH-2211'},
    {'X': 360, 'Y': 194, 'id': 'CH-2212'},
    {'X': 357, 'Y': 221, 'id': 'CH-2221'},
    {'X': 385, 'Y': 213, 'id': 'CH-2222'},
    {'X': 356, 'Y': 237, 'id': 'CH-2223'},
    {'X': 359, 'Y': 249, 'id': 'CH-2224'},
    {'X': 418, 'Y': 146, 'id': 'CH-3111'},
    {'X': 411, 'Y': 188, 'id': 'CH-3112'},
    {'X': 435, 'Y': 177, 'id': 'CH-3113'},
    {'X': 414, 'Y': 163, 'id': 'CH-3114'},
    {'X': 472, 'Y': 95, 'id': 'CH-3211'},
    {'X': 420, 'Y': 124, 'id': 'CH-3221'},
    {'X': 462, 'Y': 129, 'id': 'CH-3222'},
    {'X': 446, 'Y': 151, 'id': 'CH-3223'},
    {'X': 465, 'Y': 173, 'id': 'CH-3224'},
    {'X': 485, 'Y': 138, 'id': 'CH-3311'},
    {'X': 152, 'Y': 349, 'id': 'CH-4111'},
    {'X': 164, 'Y': 358, 'id': 'CH-4112'},
    {'X': 176, 'Y': 375, 'id': 'CH-4113'},
    {'X': 186, 'Y': 319, 'id': 'CH-4114'},
    {'X': 189, 'Y': 342, 'id': 'CH-4115'},
    {'X': 201, 'Y': 370, 'id': 'CH-4116'},
    {'X': 216, 'Y': 303, 'id': 'CH-4121'},
    {'X': 215, 'Y': 333, 'id': 'CH-4122'},
    {'X': 220, 'Y': 360, 'id': 'CH-4123'},
    {'X': 234, 'Y': 327, 'id': 'CH-4124'},
    {'X': 239, 'Y': 351, 'id': 'CH-4125'},
    {'X': 257, 'Y': 284, 'id': 'CH-4211'},
    {'X': 247, 'Y': 322, 'id': 'CH-4212'},
    {'X': 288, 'Y': 273, 'id': 'CH-4213'},
    {'X': 283, 'Y': 293, 'id': 'CH-4214'},
    {'X': 244, 'Y': 299, 'id': 'CH-4215'},
    {'X': 267, 'Y': 323, 'id': 'CH-4221'},
    {'X': 254, 'Y': 358, 'id': 'CH-4222'},
    {'X': 278, 'Y': 345, 'id': 'CH-4223'},
    {'X': 261, 'Y': 373, 'id': 'CH-4224'},
    {'X': 283, 'Y': 356, 'id': 'CH-4225'},
    {'X': 294, 'Y': 306, 'id': 'CH-4231'},
    {'X': 296, 'Y': 330, 'id': 'CH-4232'},
    {'X': 311, 'Y': 274, 'id': 'CH-4241'},
    {'X': 312, 'Y': 292, 'id': 'CH-4242'},
    {'X': 328, 'Y': 257, 'id': 'CH-4243'},
    {'X': 331, 'Y': 270, 'id': 'CH-4244'},
    {'X': 510, 'Y': 169, 'id': 'CH-5111'},
    {'X': 506, 'Y': 185, 'id': 'CH-5112'},
    {'X': 545, 'Y': 195, 'id': 'CH-5113'},
    {'X': 479, 'Y': 185, 'id': 'CH-5121'},
    {'X': 497, 'Y': 203, 'id': 'CH-5122'},
    {'X': 528, 'Y': 211, 'id': 'CH-5123'},
    {'X': 437, 'Y': 201, 'id': 'CH-5124'},
    {'X': 393, 'Y': 222, 'id': 'CH-5211'},
    {'X': 390, 'Y': 242, 'id': 'CH-5212'},
    {'X': 441, 'Y': 225, 'id': 'CH-5214'},
    {'X': 412, 'Y': 234, 'id': 'CH-5215'},
    {'X': 431, 'Y': 251, 'id': 'CH-5216'},
    {'X': 478, 'Y': 219, 'id': 'CH-5221'},
    {'X': 469, 'Y': 237, 'id': 'CH-5222'},
    {'X': 458, 'Y': 258, 'id': 'CH-5223'},
    {'X': 511, 'Y': 231, 'id': 'CH-5231'},
    {'X': 492, 'Y': 247, 'id': 'CH-5232'},
    {'X': 485, 'Y': 277, 'id': 'CH-5233'},
    {'X': 500, 'Y': 265, 'id': 'CH-5234'},
    {'X': 354, 'Y': 269, 'id': 'CH-6111'},
    {'X': 374, 'Y': 261, 'id': 'CH-6112'},
    {'X': 411, 'Y': 266, 'id': 'CH-6113'},
    {'X': 363, 'Y': 293, 'id': 'CH-6114'},
    {'X': 399, 'Y': 282, 'id': 'CH-6115'},
    {'X': 382, 'Y': 317, 'id': 'CH-6121'},
    {'X': 418, 'Y': 317, 'id': 'CH-6122'},
    {'X': 408, 'Y': 351, 'id': 'CH-6131'},
    {'X': 418, 'Y': 383, 'id': 'CH-6132'},
    {'X': 440, 'Y': 274, 'id': 'CH-6211'},
    {'X': 440, 'Y': 303, 'id': 'CH-6212'},
    {'X': 521, 'Y': 280, 'id': 'CH-7111'},
    {'X': 542, 'Y': 275, 'id': 'CH-7112'},
    {'X': 537, 'Y': 239, 'id': 'CH-7113'},
    {'X': 524, 'Y': 259, 'id': 'CH-7114'},
    {'X': 549, 'Y': 253, 'id': 'CH-7115'},
    {'X': 588, 'Y': 178, 'id': 'CH-7121'},
    {'X': 564, 'Y': 196, 'id': 'CH-7122'},
    {'X': 558, 'Y': 214, 'id': 'CH-7123'},
    {'X': 594, 'Y': 192, 'id': 'CH-7124'},
    {'X': 571, 'Y': 227, 'id': 'CH-7125'},
    {'X': 591, 'Y': 216, 'id': 'CH-7126'},
    {'X': 499, 'Y': 293, 'id': 'CH-7211'},
    {'X': 555, 'Y': 289, 'id': 'CH-7221'},
    {'X': 562, 'Y': 308, 'id': 'CH-7222'},
    {'X': 595, 'Y': 241, 'id': 'CH-7231'},
    {'X': 51, 'Y': 270, 'id': 'CH-8111'},
    {'X': 67, 'Y': 239, 'id': 'CH-8112'},
    {'X': 108, 'Y': 201, 'id': 'CH-8113'},
    {'X': 102, 'Y': 183, 'id': 'CH-8114'},
    {'X': 138, 'Y': 164, 'id': 'CH-8211'},
    {'X': 165, 'Y': 154, 'id': 'CH-8212'},
    {'X': 178, 'Y': 135, 'id': 'CH-8213'},
    {'X': 204, 'Y': 113, 'id': 'CH-8214'},
    {'X': 238, 'Y': 110, 'id': 'CH-8215'},
    {'X': 276, 'Y': 96, 'id': 'CH-8216'},
    {'X': 130, 'Y': 151, 'id': 'CH-8221'},
    {'X': 159, 'Y': 118, 'id': 'CH-8222'},
    {'X': 166, 'Y': 86, 'id': 'CH-8223'},
    {'X': 186, 'Y': 108, 'id': 'CH-8224'},
    {'X': 220, 'Y': 89, 'id': 'CH-8225'},
    {'X': 236, 'Y': 70, 'id': 'CH-8226'},
    {'X': 261, 'Y': 85, 'id': 'CH-8227'},
    {'X': 270, 'Y': 64, 'id': 'CH-8228'},
    {'X': 121, 'Y': 236, 'id': 'CH-9111'},
    {'X': 280, 'Y': 126, 'id': 'CH-9211'},
    {'X': 404, 'Y': 73, 'id': 'CH-9311'}]