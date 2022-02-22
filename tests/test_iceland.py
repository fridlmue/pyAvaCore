from avacore import pyAvaCore
import unittest
import xml.etree.ElementTree as ET


class TestIceland(unittest.TestCase):

    def test_iceland(self):
        # root = ET.parse(f'{__file__}.xml')
        reports = pyAvaCore.process_reports_is(path=f'{__file__}.xml', cached=True)
        self.assertEqual(len(reports), 4)
        report = reports[0]
        self.assertEqual(report.bulletinID, 'IS-SV-2022-02-21T16:40:51+00:00')
        self.assertEqual(report.publicationTime.isoformat(), '2022-02-21T16:40:51+00:00')
        self.assertEqual(report.validTime.startTime.isoformat(), '2022-02-21T19:00:00+00:00')
        self.assertEqual(report.validTime.endTime.isoformat(), '2022-02-22T19:00:00+00:00')
        self.assertIn('IS-SV', report.get_region_list())
        self.assertNotIn('BYAMM', report.get_region_list())
        self.assertEqual(report.dangerRatings[0].mainValue, 'high')
        # self.assertRaises(AttributeError, getattr, report.dangerRatings[0].elevation, 'upperBound')
        # self.assertEqual(report.dangerRatings[0].elevation.lowerBound, '1500')
        # self.assertEqual(report.danger_main[0].valid_elevation, '>1500')
        # self.assertEqual(report.dangerpattern, [])
        self.assertEqual(report.avalancheProblems[0].problemType, 'wind_drifted_snow')
        self.assertEqual(report.avalancheProblems[1].problemType, 'persistent_weak_layers')
        self.assertEqual(len(report.avalancheProblems), 2)
        self.assertIn('N', report.avalancheProblems[0].dangerRating.aspect)
        self.assertIn('W', report.avalancheProblems[0].dangerRating.aspect)
        self.assertRaises(AttributeError, getattr, report, "predecessor_id")

if __name__ == '__main__':
    unittest.main()
