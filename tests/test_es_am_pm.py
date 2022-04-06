from avacore import pyAvaCore
from avacore.processor_es import get_reports_from_file
import unittest
import xml.etree.ElementTree as ET


class TestES(unittest.TestCase):
    def test_ES(self):
        with open(f"{__file__}.xml", encoding="ISO-8859-1") as f:
            text = f.read()
        reports = get_reports_from_file(text)
        self.assertEqual(len(reports), 10)
        report = reports[0]
        self.assertEqual(report.bulletinID, "ES-NA_2022-02-22 15:57:00+01:00_PM")
        self.assertEqual(
            report.publicationTime.isoformat(), "2022-02-22T15:57:00+01:00"
        )
        self.assertEqual(
            report.validTime.startTime.isoformat(), "2022-02-23T12:00:00+01:00"
        )
        self.assertEqual(
            report.validTime.endTime.isoformat(), "2022-02-23T15:57:00+01:00"
        )
        self.assertIn("ES-NA", report.get_region_list())
        self.assertNotIn("ES-GA", report.get_region_list())
        self.assertEqual(report.dangerRatings[0].mainValue, "moderate")
        self.assertRaises(
            AttributeError, getattr, report.dangerRatings[0].elevation, "upperBound"
        )
        self.assertRaises(
            AttributeError, getattr, report.dangerRatings[0].elevation, "lowerBound"
        )

        report = reports[1]
        self.assertEqual(
            report.validTime.startTime.isoformat(), "2022-02-22T15:57:00+01:00"
        )
        self.assertEqual(
            report.validTime.endTime.isoformat(), "2022-02-23T12:00:00+01:00"
        )
        self.assertEqual(report.dangerRatings[0].mainValue, "low")
        self.assertIn("ES-NA", report.get_region_list())
        self.assertNotIn("ES-GA", report.get_region_list())
        self.assertRaises(
            AttributeError, getattr, report.dangerRatings[0].elevation, "lowerBound"
        )
        self.assertRaises(
            AttributeError, getattr, report.dangerRatings[0].elevation, "upperBound"
        )
        self.assertRaises(AttributeError, getattr, report, "predecessor_id")

        report = reports[2]
        self.assertEqual(report.bulletinID, "ES-JA_2022-02-22 15:57:00+01:00_PM")
        self.assertEqual(
            report.publicationTime.isoformat(), "2022-02-22T15:57:00+01:00"
        )
        self.assertEqual(
            report.validTime.startTime.isoformat(), "2022-02-23T12:00:00+01:00"
        )
        self.assertEqual(
            report.validTime.endTime.isoformat(), "2022-02-23T15:57:00+01:00"
        )
        self.assertIn("ES-JA", report.get_region_list())
        self.assertNotIn("ES-GA", report.get_region_list())
        self.assertEqual(report.dangerRatings[0].mainValue, "moderate")
        self.assertEqual(report.dangerRatings[0].elevation.upperBound, "2400")
        self.assertRaises(
            AttributeError, getattr, report.dangerRatings[0].elevation, "lowerBound"
        )
        self.assertEqual(report.dangerRatings[1].mainValue, "moderate")
        self.assertEqual(report.dangerRatings[1].elevation.lowerBound, "2400")
        self.assertRaises(
            AttributeError, getattr, report.dangerRatings[1].elevation, "upperBound"
        )

        report = reports[3]
        self.assertEqual(
            report.validTime.startTime.isoformat(), "2022-02-22T15:57:00+01:00"
        )
        self.assertEqual(
            report.validTime.endTime.isoformat(), "2022-02-23T12:00:00+01:00"
        )
        self.assertIn("ES-JA", report.get_region_list())
        self.assertNotIn("ES-GA", report.get_region_list())
        self.assertEqual(report.dangerRatings[0].mainValue, "low")
        self.assertRaises(
            AttributeError, getattr, report.dangerRatings[0].elevation, "lowerBound"
        )
        self.assertEqual(report.dangerRatings[0].elevation.upperBound, "2400")
        self.assertRaises(AttributeError, getattr, report, "predecessor_id")
        self.assertEqual(report.dangerRatings[1].mainValue, "moderate")
        self.assertEqual(report.dangerRatings[1].elevation.lowerBound, "2400")
        self.assertRaises(
            AttributeError, getattr, report.dangerRatings[1].elevation, "upperBound"
        )


if __name__ == "__main__":
    unittest.main()
