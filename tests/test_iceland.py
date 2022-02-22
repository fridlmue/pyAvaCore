from avacore import pyAvaCore
import unittest
import xml.etree.ElementTree as ET


class TestIceland(unittest.TestCase):

    def test_iceland(self):
        root = ET.parse(f'{__file__}.xml')
        reports = pyAvaCore.process_reports_is(root)
        self.assertEqual(len(reports), 4)
        report = reports[0]
        self.assertEqual(report.bulletinID, 'IS-SV-2022-01-19T17:35:39+00:00')
        self.assertEqual(report.publicationTime.isoformat(), '2022-01-19T17:35:39+00:00')
        self.assertEqual(report.validTime.startTime.isoformat(), '2022-01-19T19:00:00+00:00')
        self.assertEqual(report.validTime.endTime.isoformat(), '2022-01-20T19:00:00+00:00')
        self.assertIn('IS-SV', report.get_region_list())
        self.assertNotIn('BYAMM', report.get_region_list())
        self.assertEqual(report.dangerRatings[0].mainValue, 'low')
        # self.assertRaises(AttributeError, getattr, report.dangerRatings[0].elevation, 'upperBound')
        # self.assertEqual(report.dangerRatings[0].elevation.lowerBound, '1500')
        # self.assertEqual(report.danger_main[0].valid_elevation, '>1500')
        # self.assertEqual(report.dangerpattern, [])
        self.assertEqual(report.avalancheProblems[0].problemType, 'Wet snow')
        self.assertIn('E', report.avalancheProblems[0].dangerRating.aspect)
        self.assertIn('NW', report.avalancheProblems[0].dangerRating.aspect)
        self.assertRaises(AttributeError, getattr, report, "predecessor_id")

if __name__ == '__main__':
    unittest.main()
