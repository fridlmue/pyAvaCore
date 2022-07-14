from avacore import pyAvaCore
import unittest
import json
import xml.etree.ElementTree as ET


class TestSalzburg(unittest.TestCase):
    def test_salzburg(self):
        root = ET.parse(f"{__file__}.xml")
        reports = pyAvaCore.parse_xml(root).bulletins
        self.assertEqual(len(reports), 3)
        report = reports[0]
        self.assertEqual(report.bulletinID, "RID489RGR1")
        self.assertEqual(
            report.publicationTime.isoformat(), "2021-02-25T17:00:00+00:00"
        )
        self.assertEqual(
            report.validTime.startTime.isoformat(), "2021-02-25T23:00:00+00:00"
        )
        self.assertEqual(
            report.validTime.endTime.isoformat(), "2021-02-26T23:00:00+00:00"
        )
        self.assertIn("AT-05-19", report.get_region_list())
        self.assertIn("AT-05-20", report.get_region_list())
        self.assertNotIn("AT-05-21", report.get_region_list())
        self.assertEqual(report.dangerRatings[0].mainValue, "low")
        self.assertRaises(
            AttributeError, getattr, report.dangerRatings[0].elevation, "lowerBound"
        )
        self.assertRaises(
            AttributeError, getattr, report.dangerRatings[0].elevation, "upperBound"
        )
        self.assertEqual(report.avalancheProblems[0].problemType, "wet_snow")
        self.assertEqual(
            report.avalancheProblems[0].terrainFeature,
            "daytime cycle of naturally triggered avalanches",
        )
        self.assertEqual(report.avalancheProblems[1].problemType, "gliding_snow")
        self.assertEqual(
            report.avalancheProblems[1].terrainFeature,
            "in extremely steep grass-covered terrain",
        )
        self.assertRaises(AttributeError, getattr, report, "predecessor_id")

        report = reports[1]

        self.assertEqual(report.bulletinID, "RID489RGR2")
        self.assertEqual(
            report.publicationTime.isoformat(), "2021-02-25T17:00:00+00:00"
        )
        self.assertEqual(
            report.validTime.startTime.isoformat(), "2021-02-25T23:00:00+00:00"
        )
        self.assertEqual(
            report.validTime.endTime.isoformat(), "2021-02-26T23:00:00+00:00"
        )

        self.assertIn("AT-05-18", report.get_region_list())
        self.assertIn("AT-05-14", report.get_region_list())
        self.assertIn("AT-05-08", report.get_region_list())
        self.assertIn("AT-05-18", report.get_region_list())
        self.assertIn("AT-05-03", report.get_region_list())
        self.assertIn("AT-05-01", report.get_region_list())
        self.assertNotIn("AT-05-20", report.get_region_list())
        self.assertEqual(report.dangerRatings[0].mainValue, "low")
        self.assertEqual(report.dangerRatings[0].validTimePeriod, "earlier")
        self.assertRaises(
            AttributeError, getattr, report.dangerRatings[0].elevation, "lowerBound"
        )
        self.assertRaises(
            AttributeError, getattr, report.dangerRatings[0].elevation, "upperBound"
        )
        self.assertEqual(report.dangerRatings[1].mainValue, "moderate")
        self.assertEqual(report.dangerRatings[1].validTimePeriod, "later")
        self.assertRaises(
            AttributeError, getattr, report.dangerRatings[1].elevation, "lowerBound"
        )
        self.assertRaises(
            AttributeError, getattr, report.dangerRatings[1].elevation, "upperBound"
        )
        self.assertEqual(report.avalancheProblems[0].problemType, "wet_snow")
        self.assertEqual(report.avalancheProblems[1].problemType, "gliding_snow")
        self.assertRaises(AttributeError, getattr, report, "predecessor_id")

        self.assertEqual(
            [
                "AT-05-18",
                "AT-05-14",
                "AT-05-15",
                "AT-05-17",
                "AT-05-16",
                "AT-05-12",
                "AT-05-08",
                "AT-05-13",
                "AT-05-04",
                "AT-05-21",
                "AT-05-02",
                "AT-05-03",
                "AT-05-01",
            ],
            report.get_region_list(),
        )

        report = reports[2]
        self.assertEqual(report.bulletinID, "RID489RGR3")
        self.assertEqual(
            report.publicationTime.isoformat(), "2021-02-25T17:00:00+00:00"
        )
        self.assertEqual(
            report.validTime.startTime.isoformat(), "2021-02-25T23:00:00+00:00"
        )
        self.assertEqual(
            report.validTime.endTime.isoformat(), "2021-02-26T23:00:00+00:00"
        )

        self.assertIn("AT-05-10", report.get_region_list())
        self.assertIn("AT-05-06", report.get_region_list())
        self.assertIn("AT-05-09", report.get_region_list())
        self.assertIn("AT-05-05", report.get_region_list())
        self.assertIn("AT-05-11", report.get_region_list())
        self.assertIn("AT-05-07", report.get_region_list())
        self.assertNotIn("AT-05-18", report.get_region_list())
        self.assertEqual(report.dangerRatings[0].mainValue, "low")
        # self.assertEqual(report.dangerRatings[0].valid_elevation, '>2000')
        self.assertEqual(report.dangerRatings[0].elevation.lowerBound, "2000")
        self.assertEqual(report.dangerRatings[0].validTimePeriod, "earlier")
        self.assertEqual(report.dangerRatings[1].mainValue, "low")
        # self.assertEqual(report.dangerRatings[1].valid_elevation, '<2000')
        self.assertEqual(report.dangerRatings[1].elevation.upperBound, "2000")
        self.assertEqual(report.dangerRatings[1].validTimePeriod, "earlier")
        self.assertEqual(report.avalancheProblems[0].problemType, "wet_snow")
        self.assertEqual(report.avalancheProblems[1].problemType, "gliding_snow")

        self.assertEqual(report.dangerRatings[2].mainValue, "low")
        # self.assertEqual(report.dangerRatings[0].valid_elevation, '>2600')
        self.assertEqual(report.dangerRatings[2].elevation.lowerBound, "2600")
        self.assertEqual(report.dangerRatings[2].validTimePeriod, "later")
        self.assertEqual(report.dangerRatings[3].mainValue, "moderate")
        # self.assertEqual(report.dangerRatings[1].valid_elevation, '<2600')
        self.assertEqual(report.dangerRatings[3].elevation.upperBound, "2600")
        self.assertEqual(report.dangerRatings[3].validTimePeriod, "later")

        self.assertRaises(AttributeError, getattr, report, "predecessor_id")


if __name__ == "__main__":
    unittest.main()
