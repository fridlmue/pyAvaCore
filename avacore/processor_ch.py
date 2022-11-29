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

        url = f"https://www.slf.ch/avalanche/bulletin/{self.local}/gk_region2pdf.txt"
        try:
            with urllib.request.urlopen(url) as response:
                logging.info("Fetching %s", url)
                data = response.read()
            with zipfile.ZipFile(self.raw_data, "a") as zip_ref:
                zip_ref.writestr("gk_region2pdf.txt", data)
        except:  # pylint: disable=bare-except
            logging.warning("Could not locate gk_regions2pdf.txt")

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

        # in px_list[y][x], y is the line, x is the row with 4 channels each. x in pixel = 1+ x/4

        if px_list[19][81] == 0:
            aspects.append('NW')
        if px_list[19][113] == 0:
            aspects.append('N')
        if px_list[19][145] == 0:
            aspects.append('NE')
        if px_list[28][81] == 0:
            aspects.append('W')
        if px_list[28][145] == 0:
            aspects.append('E')
        if px_list[36][81] == 0:
            aspects.append('SW')
        if px_list[36][113] == 0:
            aspects.append('S')
        if px_list[36][145] == 0:
            aspects.append('SE')

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
