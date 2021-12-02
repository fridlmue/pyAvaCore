from avacore import pyAvaCore
import unittest
import xml.etree.ElementTree as ET


class TestBavaria(unittest.TestCase):

    def test_bavaria(self):
        root = ET.parse(f'{__file__}.xml')
        reports = pyAvaCore.parse_xml_bavaria(root)
        self.assertEqual(len(reports), 6)
        report = reports[0]
        self.assertEqual(report.bulletinID, 'BYCAAMLGenID3577-BYALL')
        self.assertEqual(report.publicationTime.isoformat(), '2021-01-26T17:43:18+01:00')
        self.assertEqual(report.validTime.startTime.isoformat(), '2021-01-27T00:00:00+01:00')
        self.assertEqual(report.validTime.endTime.isoformat(), '2021-01-27T23:59:59+01:00')
        self.assertIn('BYALL', report.get_region_list())
        self.assertNotIn('BYAMM', report.get_region_list())
        self.assertEqual(report.dangerRatings[0].mainValue, 'considerable')
        self.assertRaises(AttributeError, getattr, report.dangerRatings[0].elevation, 'upperBound')
        self.assertEqual(report.dangerRatings[0].elevation.lowerBound, '1500')
        # self.assertEqual(report.danger_main[0].valid_elevation, '>1500')
        # self.assertEqual(report.dangerpattern, [])
        self.assertEqual(report.avalancheProblems[0].problemType, 'wind_drifted_snow')
        self.assertIn('E', report.avalancheProblems[0].dangerRating.aspect)
        self.assertIn('NW', report.avalancheProblems[0].dangerRating.aspect)
        self.assertRaises(AttributeError, getattr, report, "predecessor_id")

if __name__ == '__main__':
    unittest.main()
