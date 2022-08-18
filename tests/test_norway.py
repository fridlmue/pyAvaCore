import json
from avacore.processor_norway import Processor
import unittest
import xml.etree.ElementTree as ET


class TestNorway(unittest.TestCase):
    def test_norway(self):
        with open(f"{__file__}.json") as fp:
            data = json.load(fp)
        varsom_report = data
        processor = Processor()
        reports = processor.parse_json_no(
            "NO-3016", varsom_report, fetch_time_dependant=False
        ).bulletins

        self.assertEqual(len(reports), 1)

        report = reports[0]
        self.assertEqual(report.bulletinID, "NO-3016_2021-12-01 15:42:45")
        self.assertEqual(report.publicationTime.isoformat(), "2021-12-01T15:42:45")
        self.assertEqual(report.validTime.startTime.isoformat(), "2021-12-02T00:00:00")
        self.assertEqual(report.validTime.endTime.isoformat(), "2021-12-02T23:59:59")
        self.assertIn("NO-3016", report.get_region_list())
        self.assertNotIn("NO-3017", report.get_region_list())
        self.assertEqual(report.dangerRatings[0].mainValue, "considerable")
        self.assertEqual(report.dangerRatings[0].get_mainValue_int(), 3)
        self.assertRaises(
            AttributeError, getattr, report.dangerRatings[0].elevation, "lowerBound"
        )
        self.assertRaises(
            AttributeError, getattr, report.dangerRatings[0].elevation, "upperBound"
        )
        self.assertEqual(
            report.avalancheProblems[0].problemType, "persistent_weak_layers"
        )
        self.assertEqual(report.avalancheProblems[0].elevation.lowerBound, "300")
        self.assertRaises(
            AttributeError, getattr, report.avalancheProblems[0].elevation, "upperBound"
        )
        self.assertIn("S", report.avalancheProblems[0].aspects)
        self.assertRaises(AttributeError, getattr, report, "predecessor_id")
