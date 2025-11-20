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
from datetime import time
import copy
import xml.etree.ElementTree as ET
from avacore.avabulletin import (
    AvaBulletin,
    DangerRating,
    AvalancheProblem,
    Region,
    Elevation,
    Texts,
    Tendency,
)
from avacore.avabulletins import Bulletins
from avacore.processor import XmlProcessor


CAAML_NS = "{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}"
XLINK_NS = "{http://www.w3.org/1999/xlink}"


def et_add_parent_info(element_tree):
    """Add Parent-Info to structure an ElementTree"""

    for child in element_tree:
        child.attrib["__my_parent__"] = element_tree
        et_add_parent_info(child)


def et_get_parent(element_tree):
    """get Parent-Info from ElementTree, when parent Info was added previously."""

    if "__my_parent__" in element_tree.attrib:
        return element_tree.attrib["__my_parent__"]
    return None


class Processor(XmlProcessor):
    def parse_xml(self, region_id: str, root: ET.Element) -> Bulletins:
        """parses ALBINA-Style CAAML-XML. root is a ElementTree"""

        reports = Bulletins()

        for bulletin in root.iter(CAAML_NS + "Bulletin"):
            report = AvaBulletin()
            report.bulletinID = bulletin.attrib.get("{http://www.opengis.net/gml}id")
            pm_danger_ratings = []

            pm_available = False
            for nDangerRating in bulletin.iter(CAAML_NS + "DangerRating"):
                for validTime in nDangerRating.iter(CAAML_NS + "validTime"):
                    pm_available = True
                    break

            weatherForecast = Texts()
            avalancheActivity = Texts()
            snowpackStructure = Texts()

            for observations in bulletin:
                et_add_parent_info(observations)
                for locRef in observations.iter(CAAML_NS + "locRef"):
                    loc_ref = locRef.attrib.get(XLINK_NS + "href")
                    if loc_ref not in report.regions:
                        report.regions.append(Region(loc_ref))
                for dateTimeReport in observations.iter(CAAML_NS + "dateTimeReport"):
                    report.publicationTime = datetime.fromisoformat(
                        dateTimeReport.text.replace("Z", "+00:00")
                    )
                for validTime in observations.iter(CAAML_NS + "validTime"):
                    if not et_get_parent(validTime):
                        for beginPosition in observations.iter(
                            CAAML_NS + "beginPosition"
                        ):
                            report.validTime.startTime = datetime.fromisoformat(
                                beginPosition.text.replace("Z", "+00:00")
                            )
                        for endPosition in observations.iter(CAAML_NS + "endPosition"):
                            report.validTime.endTime = datetime.fromisoformat(
                                endPosition.text.replace("Z", "+00:00")
                            )
                for nDangerRating in observations.iter(CAAML_NS + "DangerRating"):
                    main_value = 0
                    am_rating = True
                    for mainValue in nDangerRating.iter(CAAML_NS + "mainValue"):
                        main_value = int(mainValue.text)
                    valid_elevation = "-"
                    for validElevation in nDangerRating.iter(
                        CAAML_NS + "validElevation"
                    ):
                        valid_elevation = validElevation.attrib.get(XLINK_NS + "href")
                    for beginPosition in nDangerRating.iter(CAAML_NS + "beginPosition"):
                        validity_begin = datetime.fromisoformat(
                            beginPosition.text.replace("Z", "+00:00")
                        )
                        if validity_begin.time() <= time(
                            15, 0, 0
                        ) and validity_begin.time() >= time(8, 0, 0):
                            am_rating = False
                            # report.validTime.endTime = report.validTime.endTime.replace(hour=validity_begin.hour)
                    danger_rating = DangerRating()
                    danger_rating.set_mainValue_int(main_value)
                    danger_rating.elevation.auto_select(valid_elevation)
                    if am_rating:
                        report.dangerRatings.append(danger_rating)
                    else:
                        pm_danger_ratings.append(danger_rating)

                for DangerPatterns in observations.iter(CAAML_NS + "dangerPatterns"):
                    dp = []
                    for DangerPattern in DangerPatterns.iter(
                        CAAML_NS + "DangerPattern"
                    ):
                        for DangerPatternType in DangerPattern.iter(CAAML_NS + "type"):
                            dp.append(DangerPatternType.text)
                    report.customData = {"LWD_Tyrol": {"dangerPatterns": dp}}

                for AvProblem in observations.iter(CAAML_NS + "AvProblem"):
                    type_r = ""
                    # problem_danger_rating = DangerRating()
                    elevation = Elevation()
                    for avProbType in AvProblem.iter(CAAML_NS + "type"):
                        type_r = avProbType.text
                    aspect = []
                    for validAspect in AvProblem.iter(CAAML_NS + "validAspect"):
                        aspect.append(
                            validAspect.get(XLINK_NS + "href")
                            .upper()
                            .replace("ASPECTRANGE_", "")
                        )
                    valid_elevation = "-"
                    for validElevation in AvProblem.iter(CAAML_NS + "validElevation"):
                        if XLINK_NS + "href" in validElevation.attrib:
                            elevation.auto_select(
                                validElevation.attrib.get(XLINK_NS + "href")
                            )
                        else:
                            for beginPosition in validElevation.iter(
                                CAAML_NS + "beginPosition"
                            ):
                                elevation.auto_select(
                                    "ElevationRange_" + beginPosition.text + "Hi"
                                )
                            for endPosition in validElevation.iter(
                                CAAML_NS + "endPosition"
                            ):
                                elevation.auto_select(
                                    "ElevationRange_" + endPosition.text + "Lw"
                                )

                    comment_r = ""
                    for comment in AvProblem.iter(CAAML_NS + "comment"):
                        comment_r = comment.text
                    # problem_danger_rating.aspects = aspect
                    problem = AvalancheProblem()
                    problem.add_problemType(type_r)
                    problem.elevation = elevation
                    problem.aspects = aspect
                    if comment_r != "":
                        problem.comment = comment_r
                    report.avalancheProblems.append(problem)

                for avActivityHighlights in observations.iter(
                    CAAML_NS + "avActivityHighlights"
                ):
                    if avActivityHighlights.text is not None:
                        avalancheActivity.highlights = (
                            avActivityHighlights.text.replace("&nbsp;", "\n")
                        )
                for wxSynopsisComment in observations.iter(
                    CAAML_NS + "wxSynopsisComment"
                ):
                    weatherForecast.comment = wxSynopsisComment.text.replace(
                        "&nbsp;", "\n"
                    )
                for avActivityComment in observations.iter(
                    CAAML_NS + "avActivityComment"
                ):
                    if avActivityComment.text is not None:
                        avalancheActivity.comment = avActivityComment.text.replace(
                            "&nbsp;", "\n"
                        )
                for snowpackStructureComment in observations.iter(
                    CAAML_NS + "snowpackStructureComment"
                ):
                    if snowpackStructureComment.text is not None:
                        snowpackStructure.comment = (
                            snowpackStructureComment.text.replace("&nbsp;", "\n")
                        )
                for tendencyComment in observations.iter(CAAML_NS + "tendencyComment"):
                    if tendencyComment.text is not None:
                        report.tendency = [
                            Tendency(
                                comment=tendencyComment.text.replace("&nbsp;", "\n")
                            )
                        ]

            report.weatherForecast = weatherForecast
            report.avalancheActivity = avalancheActivity
            report.snowpackStructure = snowpackStructure

            if pm_available:
                for danger_rating in report.dangerRatings:
                    danger_rating.validTimePeriod = "earlier"
                for danger_rating in pm_danger_ratings:
                    danger_rating.validTimePeriod = "later"
                    report.dangerRatings.append(danger_rating)

            if report.bulletinID.endswith("_PM"):
                for pm_bulletin in reports.bulletins:
                    if pm_bulletin.bulletinID == report.bulletinID[:-3]:
                        father_bulletin = pm_bulletin
                        father_bulletin.validTime.endTime = report.validTime.endTime
                        for idx, danger_rating in enumerate(
                            father_bulletin.dangerRatings
                        ):
                            father_bulletin.dangerRatings[
                                idx
                            ].validTimePeriod = "earlier"
                        for danger_rating in report.dangerRatings:
                            danger_rating.validTimePeriod = "later"
                            father_bulletin.dangerRatings.append(danger_rating)
                        for idx, avalanche_problem in enumerate(
                            father_bulletin.avalancheProblems
                        ):
                            father_bulletin.avalancheProblems[
                                idx
                            ].validTimePeriod = "earlier"
                        for avalanche_problem in report.avalancheProblems:
                            avalanche_problem.validTimePeriod = "later"
                            father_bulletin.avalancheProblems.append(avalanche_problem)
            else:
                reports.append(report)

        return reports


class VorarlbergProcessor(XmlProcessor):
    def parse_xml(self, region_id: str, root: ET.Element) -> Bulletins:
        """parses Vorarlberg-Style CAAML-XML. root is a ElementTree"""

        reports = Bulletins()
        report = AvaBulletin()
        comment_empty = 1

        # Common for every Report:

        report_id = ""
        for bulletin in root.iter(CAAML_NS + "Bulletin"):
            report_id = bulletin.attrib.get("{http://www.opengis.net/gml}id")

        activity_com = ""
        for bulletin in root.iter(CAAML_NS + "Bulletin"):
            for detail in bulletin:
                for metaDataProperty in detail.iter(CAAML_NS + "metaDataProperty"):
                    for dateTimeReport in metaDataProperty.iter(
                        CAAML_NS + "dateTimeReport"
                    ):
                        report.publicationTime = datetime.fromisoformat(
                            dateTimeReport.text
                        )
                for bulletinResultsOf in detail.iter(CAAML_NS + "bulletinResultsOf"):
                    for travelAdvisoryComment in bulletinResultsOf.iter(
                        CAAML_NS + "travelAdvisoryComment"
                    ):
                        activity_com = travelAdvisoryComment.text
                    for highlights in bulletinResultsOf.iter(CAAML_NS + "highlights"):
                        report.avalancheActivityHighlights = highlights.text
                    for comment in bulletinResultsOf.iter(CAAML_NS + "comment"):
                        if comment_empty:
                            report.tendency = [Tendency(comment=comment.text)]
                            comment_empty = 0
                    for wxSynopsisComment in bulletinResultsOf.iter(
                        CAAML_NS + "wxSynopsisComment"
                    ):
                        report.wxSynopsisComment = wxSynopsisComment.text
                    for snowpackStructureComment in bulletinResultsOf.iter(
                        CAAML_NS + "snowpackStructureComment"
                    ):
                        report.snowpackStructureComment = snowpackStructureComment.text
                    for AvProblem in detail.iter(CAAML_NS + "AvProblem"):
                        type_r = ""
                        for ac_problemt_type in AvProblem.iter(CAAML_NS + "type"):
                            type_r = ac_problemt_type.text
                        aspect = []
                        for validAspect in AvProblem.iter(CAAML_NS + "validAspect"):
                            aspect.append(
                                validAspect.get(XLINK_NS + "href")
                                .upper()
                                .replace("ASPECTRANGE_", "")
                                .replace("O", "E")
                            )
                        valid_elevation = "-"
                        for validElevation in AvProblem.iter(
                            CAAML_NS + "validElevation"
                        ):
                            if XLINK_NS + "href" in validElevation.attrib:
                                if "Treeline" in validElevation.attrib.get(
                                    XLINK_NS + "href"
                                ):
                                    if "Hi" in validElevation.attrib.get(
                                        XLINK_NS + "href"
                                    ):
                                        valid_elevation = ">Treeline"
                                    if "Lo" in validElevation.attrib.get(
                                        XLINK_NS + "href"
                                    ):
                                        valid_elevation = "<Treeline"
                            else:
                                for beginPosition in validElevation.iter(
                                    CAAML_NS + "beginPosition"
                                ):
                                    valid_elevation = (
                                        "ElevationRange_" + beginPosition.text + "Hi"
                                    )
                                for endPosition in validElevation.iter(
                                    CAAML_NS + "endPosition"
                                ):
                                    valid_elevation = (
                                        "ElevationRange_" + endPosition.text + "Lw"
                                    )
                        # problem_danger_rating = DangerRating()
                        # problem_danger_rating.aspects = aspect
                        # problem_danger_rating.elevation.auto_select(valid_elevation)
                        problem = AvalancheProblem()
                        problem.aspects = aspect
                        problem.elevation = Elevation().auto_select(valid_elevation)
                        problem.add_problemType(type_r)
                        # problem.dangerRating = problem_danger_rating
                        report.avalancheProblems.append(problem)

        report.avalancheActivityComment = activity_com

        for bulletinResultOf in root.iter(CAAML_NS + "bulletinResultsOf"):
            et_add_parent_info(bulletinResultOf)

            loc_list = []

            for locRef in bulletinResultOf.iter(CAAML_NS + "locRef"):
                current_loc_ref = locRef.attrib.get(XLINK_NS + "href")

                nDangerRating = et_get_parent(locRef)
                validity_begin = ""
                validity_end = ""
                main_value = 0
                valid_elevation = "-"

                for validTime in nDangerRating.iter(CAAML_NS + "validTime"):
                    for beginPosition in validTime.iter(CAAML_NS + "beginPosition"):
                        validity_begin = datetime.fromisoformat(beginPosition.text)
                    for endPosition in validTime.iter(CAAML_NS + "endPosition"):
                        validity_end = datetime.fromisoformat(endPosition.text)
                main_value = 0
                for main_value in nDangerRating.iter(CAAML_NS + "mainValue"):
                    main_value = int(main_value.text)
                for validElevation in nDangerRating.iter(CAAML_NS + "validElevation"):
                    if XLINK_NS + "href" in validElevation.attrib:
                        valid_elevation = validElevation.attrib.get(XLINK_NS + "href")
                    else:
                        for beginPosition in validElevation.iter(
                            CAAML_NS + "beginPosition"
                        ):
                            if "Keine" not in beginPosition.text:
                                valid_elevation = (
                                    "ElevationRange_" + beginPosition.text + "Hi"
                                )
                        for endPosition in validElevation.iter(
                            CAAML_NS + "endPosition"
                        ):
                            if "Keine" not in endPosition.text:
                                valid_elevation = (
                                    "ElevationRange_" + endPosition.text + "Lw"
                                )

                danger_rating = DangerRating()
                danger_rating.set_mainValue_int(main_value)
                danger_rating.elevation.auto_select(valid_elevation)

                loc_list.append(
                    [current_loc_ref, validity_begin, validity_end, danger_rating]
                )

        loc_ref_list = []
        del_index = []

        for index, loc_elem in enumerate(loc_list):
            if loc_elem[1].time() < time(11, 0, 0):
                if not any(loc_elem[0] in loc_ref for loc_ref in loc_ref_list):
                    c_report = copy.deepcopy(report)
                    c_report.regions.append(Region(loc_elem[0]))
                    c_report.bulletinID = report_id + "-" + loc_elem[0]
                    c_report.validTime.startTime = loc_elem[1]
                    c_report.validTime.endTime = loc_elem[2]
                    c_report.dangerRatings.append(loc_elem[3])
                    loc_ref_list.append(loc_elem[0])
                    reports.append(c_report)
                    del_index.append(index)

        loc_list = [i for j, i in enumerate(loc_list) if j not in del_index]
        del_index = []

        for index, loc_elem in enumerate(loc_list):
            if loc_elem[1].time() < time(11, 0, 0):
                report_elem_number = loc_ref_list.index(loc_elem[0])
                if reports[report_elem_number].validTime.startTime > loc_elem[2]:
                    reports[report_elem_number].validTime.endTime = loc_elem[2]
                if not (
                    reports[report_elem_number].dangerRatings[0].mainValue
                    == loc_elem[3].mainValue
                    and reports[report_elem_number]
                    .dangerRatings[0]
                    .elevation.toString()
                    == loc_elem[3].elevation.toString()
                ):
                    reports[report_elem_number].dangerRatings.append(loc_elem[3])
                del_index.append(index)

        loc_list = [i for j, i in enumerate(loc_list) if j not in del_index]
        del_index = []

        for index, loc_elem in enumerate(loc_list):
            if not any((loc_elem[0] + "_PM") in loc_ref for loc_ref in loc_ref_list):
                report_elem_number = loc_ref_list.index(loc_elem[0])
                c_report = copy.deepcopy(reports[report_elem_number])
                loc_ref_list.append(loc_elem[0] + "_PM")

                c_report.bulletinID = report_id + "-" + loc_elem[0] + "_PM"
                c_report.validTime.startTime = loc_elem[1]
                c_report.validTime.endTime = loc_elem[2]
                c_report.predecessor_id = report_id + "-" + loc_elem[0]

                c_report.dangerRatings = []
                c_report.dangerRatings.append(loc_elem[3])

                reports.append(c_report)
                del_index.append(index)

        loc_list = [i for j, i in enumerate(loc_list) if j not in del_index]
        del_index = []

        for index, loc_elem in enumerate(loc_list):
            report_elem_number = loc_ref_list.index(loc_elem[0] + "_PM")
            for danger_main in reports[report_elem_number].dangerRating:
                if danger_main.elevation.toString() == loc_elem[3].elevation.toString():
                    danger_main.mainValue = loc_elem[3].mainValue

        return reports
