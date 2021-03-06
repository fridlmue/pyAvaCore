from avacore import pyAvaCore
import unittest
import datetime
import xml.etree.ElementTree as ET


class TestSlovenia(unittest.TestCase):
    def test_slovenia(self):
        root = ET.parse(f"{__file__}.xml")
        reports = pyAvaCore.parse_xml_bavaria(
            root,
            location="slovenia",
            today=datetime.date(2021, 3, 20),
            fetch_time_dependant=False,
        )
        self.assertEqual(len(reports), 5)
        report = reports[0]
        self.assertEqual(report.bulletinID, "BulletinSiID-SI1")
        self.assertEqual(
            report.publicationTime.isoformat(), "2021-03-19T07:47:19+01:00"
        )
        self.assertEqual(
            report.validTime.startTime.isoformat(), "2021-03-20T00:00:00+01:00"
        )
        self.assertEqual(
            report.validTime.endTime.isoformat(), "2021-03-20T23:59:59.999000+01:00"
        )
        self.assertIn("SI1", report.get_region_list())
        self.assertNotIn("SI2", report.get_region_list())
        self.assertEqual(report.dangerRatings[0].validTimePeriod, "earlier")
        self.assertEqual(report.dangerRatings[0].mainValue, "low")
        self.assertEqual(report.dangerRatings[0].elevation.upperBound, "1700")
        self.assertEqual(report.avalancheProblems[0].problemType, "wind_drifted_snow")
        self.assertIn("E", report.avalancheProblems[0].aspects)
        self.assertIn("SE", report.avalancheProblems[0].aspects)
        self.assertIn("W", report.avalancheProblems[0].aspects)
        self.assertNotIn("N", report.avalancheProblems[0].aspects)
        self.assertRaises(AttributeError, getattr, report, "predecessor_id")

        report = reports[2]
        self.assertEqual(report.bulletinID, "BulletinSiID-SI3")
        self.assertEqual(
            report.publicationTime.isoformat(), "2021-03-19T07:47:19+01:00"
        )
        self.assertEqual(
            report.validTime.startTime.isoformat(), "2021-03-20T00:00:00+01:00"
        )
        self.assertEqual(
            report.validTime.endTime.isoformat(), "2021-03-20T23:59:59.999000+01:00"
        )
        self.assertIn("SI3", report.get_region_list())
        self.assertNotIn("SI1", report.get_region_list())
        self.assertEqual(report.dangerRatings[0].validTimePeriod, "earlier")
        self.assertEqual(report.dangerRatings[2].mainValue, "low")
        self.assertEqual(report.dangerRatings[2].elevation.upperBound, "1700")
        self.assertEqual(report.dangerRatings[2].validTimePeriod, "later")
        self.assertEqual(report.dangerRatings[3].mainValue, "moderate")
        self.assertEqual(report.dangerRatings[3].elevation.lowerBound, "1700")
        self.assertEqual(report.dangerRatings[3].validTimePeriod, "later")
        self.assertRaises(
            AttributeError, getattr, report.dangerRatings[1].elevation, "upperBound"
        )
        self.assertEqual(report.avalancheProblems[0].problemType, "wind_drifted_snow")
        self.assertIn("E", report.avalancheProblems[0].aspects)
        self.assertIn("SE", report.avalancheProblems[0].aspects)
        self.assertIn("W", report.avalancheProblems[0].aspects)
        self.assertNotIn("N", report.avalancheProblems[0].aspects)
        self.assertRaises(AttributeError, getattr, report, "predecessor_id")

        reports = pyAvaCore.parse_xml_bavaria(
            root, location="slovenia", today=datetime.date(2021, 3, 21)
        )
        self.assertEqual(len(reports), 5)
        report = reports[0]
        self.assertEqual(report.bulletinID, "BulletinSiID-SI1")
        self.assertEqual(
            report.publicationTime.isoformat(), "2021-03-19T07:47:19+01:00"
        )
        self.assertEqual(
            report.validTime.startTime.isoformat(), "2021-03-21T00:00:00+01:00"
        )
        self.assertEqual(
            report.validTime.endTime.isoformat(), "2021-03-21T23:59:59.999000+01:00"
        )
        self.assertIn("SI1", report.get_region_list())
        self.assertNotIn("SI2", report.get_region_list())
        self.assertEqual(report.dangerRatings[0].validTimePeriod, "earlier")
        self.assertEqual(report.dangerRatings[0].mainValue, "low")
        self.assertEqual(report.dangerRatings[0].elevation.upperBound, "1700")
        self.assertEqual(report.avalancheProblems[0].problemType, "wind_drifted_snow")
        self.assertIn("E", report.avalancheProblems[0].aspects)
        self.assertIn("SE", report.avalancheProblems[0].aspects)
        self.assertIn("W", report.avalancheProblems[0].aspects)
        self.assertNotIn("N", report.avalancheProblems[0].aspects)
        self.assertRaises(AttributeError, getattr, report, "predecessor_id")

        report = reports[2]
        self.assertEqual(report.bulletinID, "BulletinSiID-SI3")
        self.assertEqual(
            report.publicationTime.isoformat(), "2021-03-19T07:47:19+01:00"
        )
        self.assertEqual(
            report.validTime.startTime.isoformat(), "2021-03-21T00:00:00+01:00"
        )
        self.assertEqual(
            report.validTime.endTime.isoformat(), "2021-03-21T23:59:59.999000+01:00"
        )
        self.assertIn("SI3", report.get_region_list())
        self.assertNotIn("SI1", report.get_region_list())
        self.assertEqual(report.dangerRatings[1].validTimePeriod, "earlier")
        self.assertEqual(report.dangerRatings[2].mainValue, "low")
        self.assertEqual(report.dangerRatings[2].elevation.upperBound, "1700")
        self.assertEqual(report.dangerRatings[2].validTimePeriod, "later")
        self.assertEqual(report.avalancheProblems[0].problemType, "wind_drifted_snow")
        self.assertIn("E", report.avalancheProblems[0].aspects)
        self.assertIn("SE", report.avalancheProblems[0].aspects)
        self.assertIn("W", report.avalancheProblems[0].aspects)
        self.assertNotIn("N", report.avalancheProblems[0].aspects)
        self.assertRaises(AttributeError, getattr, report, "predecessor_id")


if __name__ == "__main__":
    unittest.main()
