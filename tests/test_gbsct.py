import json
from avacore import pyAvaCore
from avacore.processor_uk import get_reports_from_json
import unittest
import xml.etree.ElementTree as ET


class TestGbSct(unittest.TestCase):
    def test_gbsct(self):
        with open(f"{__file__}.json") as fp:
            data = json.load(fp)
        sais_report = data
        reports = get_reports_from_json(sais_report)

        self.assertEqual(len(reports), 6)

        report = reports[0]
        self.assertEqual(report.bulletinID, "GB-SCT-9788")
        self.assertEqual(report.publicationTime.isoformat(), "2021-12-22T00:00:00")
        self.assertEqual(report.validTime.startTime.isoformat(), "2021-12-22T18:00:00")
        self.assertEqual(report.validTime.endTime.isoformat(), "2021-12-23T18:00:00")
        self.assertIn("GB-SCT-7", report.get_region_list())
        self.assertNotIn("GB-SCT-6", report.get_region_list())
        self.assertEqual(report.dangerRatings[0].mainValue, "low")
        self.assertEqual(report.dangerRatings[0].get_mainValue_int(), 1)
        self.assertRaises(AttributeError, getattr, report, "predecessor_id")

        report = reports[3]
        self.assertEqual(report.bulletinID, "GB-SCT-9791")
        self.assertEqual(report.publicationTime.isoformat(), "2021-12-22T00:00:00")
        self.assertEqual(report.validTime.startTime.isoformat(), "2021-12-22T18:00:00")
        self.assertEqual(report.validTime.endTime.isoformat(), "2021-12-23T18:00:00")
        self.assertIn("GB-SCT-4", report.get_region_list())
        self.assertNotIn("GB-SCT-6", report.get_region_list())
