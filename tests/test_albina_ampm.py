from avacore import pyAvaCore
from avacore.avabulletins import Bulletins
import unittest
import xml.etree.ElementTree as ET


class TestAlbinaAmPm(unittest.TestCase):
    def test_albina_ampm(self):
        root = ET.parse(f"{__file__}.xml")
        bulletins = pyAvaCore.parse_xml(root)
        self.assertEqual(bulletins.main_date().isoformat(), "2021-02-22")
        self.assertEqual(len(bulletins.bulletins), 3)

        report = bulletins.bulletins[0]
        self.assertEqual(report.bulletinID, "15b7b04b-5f3f-435c-a4f4-33a4eabeb965")
        self.assertEqual(
            report.publicationTime.isoformat(), "2021-02-21T16:00:00+00:00"
        )
        self.assertEqual(
            report.validTime.startTime.isoformat(), "2021-02-21T23:00:00+00:00"
        )
        self.assertEqual(
            report.validTime.endTime.isoformat(), "2021-02-22T23:00:00+00:00"
        )
        self.assertIn("IT-32-TN-15", report.get_region_list())
        self.assertNotIn("IT-32-BZ-01", report.get_region_list())
        self.assertEqual(report.dangerRatings[0].mainValue, "moderate")
        self.assertEqual(report.dangerRatings[0].validTimePeriod, "earlier")
        self.assertEqual(report.dangerRatings[0].get_mainValue_int(), 2)
        self.assertEqual(report.dangerRatings[1].mainValue, "considerable")
        self.assertEqual(report.dangerRatings[1].validTimePeriod, "later")
        self.assertEqual(report.dangerRatings[1].get_mainValue_int(), 3)
        self.assertRaises(
            AttributeError, getattr, report.dangerRatings[0].elevation, "lowerBound"
        )
        self.assertRaises(
            AttributeError, getattr, report.dangerRatings[0].elevation, "upperBound"
        )
        self.assertEqual(report.avalancheProblems[0].problemType, "wet_snow")
        self.assertIn("S", report.avalancheProblems[0].aspects)
        self.assertEqual(report.avalancheProblems[1].problemType, "gliding_snow")
        self.assertEqual(report.avalancheProblems[0].validTimePeriod, "earlier")
        self.assertIn("SW", report.avalancheProblems[1].aspects)
        self.assertNotIn("N", report.avalancheProblems[1].aspects)
        # self.assertRaises(AttributeError, getattr, report, "predecessor_id")

        report = bulletins.bulletins[2]
        self.assertEqual(report.bulletinID, "56410e01-259b-4b8e-a97b-f4628744b70e")
        self.assertEqual(
            report.publicationTime.isoformat(), "2021-02-21T16:00:00+00:00"
        )
        self.assertEqual(
            report.validTime.startTime.isoformat(), "2021-02-21T23:00:00+00:00"
        )
        self.assertEqual(
            report.validTime.endTime.isoformat(), "2021-02-22T23:00:00+00:00"
        )
        self.assertIn("AT-07-13", report.get_region_list())
        self.assertNotIn("AT-07-24", report.get_region_list())
        self.assertEqual(report.dangerRatings[0].mainValue, "moderate")
        self.assertEqual(report.dangerRatings[0].get_mainValue_int(), 2)
        self.assertEqual(report.dangerRatings[0].validTimePeriod, "earlier")
        self.assertEqual(report.dangerRatings[3].elevation.upperBound, "2600")
        self.assertEqual(report.dangerRatings[3].validTimePeriod, "later")
        self.assertEqual(report.dangerRatings[2].validTimePeriod, "later")
        self.assertEqual(report.dangerRatings[1].elevation.upperBound, "2400")
        self.assertEqual(report.dangerRatings[1].validTimePeriod, "earlier")
        self.assertEqual(report.dangerRatings[0].elevation.lowerBound, "2400")
        self.assertIn('DP6', report.customData['LWD_Tyrol']['dangerPatterns'])
        self.assertIn('DP10', report.customData['LWD_Tyrol']['dangerPatterns'])
        self.assertEqual(report.avalancheProblems[0].validTimePeriod, "earlier")
        self.assertEqual(report.avalancheProblems[0].problemType, "wind_drifted_snow")
        self.assertEqual(report.avalancheProblems[1].elevation.upperBound, "2600")
        self.assertEqual(report.avalancheProblems[1].validTimePeriod, "later")
        self.assertEqual(report.avalancheProblems[1].problemType, "wet_snow")
        self.assertIn("W", report.avalancheProblems[1].aspects)
        self.assertNotIn("N", report.avalancheProblems[1].aspects)
        self.assertEqual(report.avalancheProblems[2].elevation.lowerBound, "2400")
        self.assertIn("N", report.avalancheProblems[2].aspects)
        self.assertEqual(report.avalancheProblems[2].validTimePeriod, "later")
        self.assertEqual(report.avalancheProblems[2].problemType, "wind_drifted_snow")
        self.assertIn("NE", report.avalancheProblems[2].aspects)
        self.assertNotIn("S", report.avalancheProblems[2].aspects)
        self.assertEqual(report.avalancheProblems[2].elevation.lowerBound, "2400")
        # self.assertEqual(report.predecessor_id, '56410e01-259b-4b8e-a97b-f4628744b70e')


if __name__ == "__main__":
    unittest.main()
