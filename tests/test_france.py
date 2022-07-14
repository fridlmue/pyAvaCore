from avacore.processor_fr import parse_reports_fr
import unittest
import xml.etree.ElementTree as ET


class TestFrance(unittest.TestCase):
    def test_france(self):
        root = ET.ElementTree()
        root.parse(f"{__file__}.xml")
        bulletins = parse_reports_fr(root)
        self.assertEqual(bulletins.main_date().isoformat(), "2021-03-19")
        self.assertEqual(len(bulletins.bulletins), 1)
        report = bulletins.bulletins[0]
        self.assertEqual(report.bulletinID, "FR-22_2021-03-18T16:00:00+01:00")
        self.assertEqual(
            report.publicationTime.isoformat(), "2021-03-18T16:00:00+01:00"
        )
        self.assertEqual(
            report.validTime.startTime.isoformat(), "2021-03-18T16:00:00+01:00"
        )
        self.assertEqual(
            report.validTime.endTime.isoformat(), "2021-03-19T18:00:00+01:00"
        )
        self.assertIn("FR-22", report.get_region_list())
        self.assertNotIn("FR-10", report.get_region_list())
        self.assertEqual(report.dangerRatings[2].mainValue, "moderate")
        self.assertEqual(report.dangerRatings[2].validTimePeriod, "later")
        self.assertEqual(report.dangerRatings[2].elevation.upperBound, "2200")
        self.assertEqual(report.dangerRatings[3].mainValue, "considerable")
        self.assertEqual(report.dangerRatings[3].validTimePeriod, "later")
        self.assertEqual(report.dangerRatings[3].elevation.lowerBound, "2200")
        self.assertEqual(report.dangerRatings[0].mainValue, "low")
        self.assertEqual(report.dangerRatings[0].elevation.upperBound, "2200")
        self.assertEqual(report.dangerRatings[0].validTimePeriod, "earlier")
        self.assertEqual(report.dangerRatings[1].mainValue, "moderate")
        self.assertEqual(report.dangerRatings[1].elevation.lowerBound, "2200")
        self.assertEqual(report.dangerRatings[1].validTimePeriod, "earlier")
        self.assertIn(
            "E", report.customData["MeteoFrance"]["avalancheProneLocation"]["aspects"]
        )
        self.assertIn(
            "SE", report.customData["MeteoFrance"]["avalancheProneLocation"]["aspects"]
        )

        self.assertRaises(AttributeError, getattr, report, "predecessor_id")

        # self.assertEqual(report.predecessor_id, 'FR-22_2021-03-18T16:00:00+01:00')
        """
        report = bulletins.bulletins[1]
        self.assertEqual(report.bulletinID, 'FR-22_2021-03-18T16:00:00+01:00')
        self.assertEqual(report.publicationTime.isoformat(), '2021-03-18T16:00:00+01:00')
        self.assertEqual(report.validTime.startTime.isoformat(), '2021-03-18T16:00:00+01:00')
        self.assertEqual(report.validTime.endTime.isoformat(), '2021-03-19T12:00:00+01:00')
        self.assertIn('FR-22', report.get_region_list())
        self.assertNotIn('FR-10', report.get_region_list())
        self.assertEqual(report.dangerRatings[0].mainValue, 'low')
        self.assertEqual(report.dangerRatings[0].elevation.upperBound, '2200')
        self.assertEqual(report.dangerRatings[1].mainValue, 'moderate')
        self.assertEqual(report.dangerRatings[1].elevation.lowerBound, '2200')
        self.assertIn('E', report.dangerRatings[0].aspects)
        self.assertIn('SE', report.dangerRatings[0].aspects)

        self.assertRaises(AttributeError, getattr, report, "predecessor_id")
        """


if __name__ == "__main__":
    unittest.main()
