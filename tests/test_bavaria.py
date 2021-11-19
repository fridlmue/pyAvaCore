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
        self.assertEqual(report.publicationTime.isoformat(), '2021-01-26T17:43:18')
        self.assertEqual(report.validTime.startTime.isoformat(), '2021-01-27T00:00:00')
        self.assertEqual(report.validTime.endTime.isoformat(), '2021-01-27T23:59:59')
        self.assertIn('BYALL', report.region)
        self.assertNotIn('BYAMM', report.region)
        self.assertEqual(report.dangerRating[0].mainValue, 'considerable')
        self.assertRaises(AttributeError, getattr, report.dangerRating[0].elevation, 'upperBound')
        self.assertEqual(report.dangerRating[0].elevation.lowerBound, '1500')
        # self.assertEqual(report.danger_main[0].valid_elevation, '>1500')
        # self.assertEqual(report.dangerpattern, [])
        self.assertEqual(report.avalancheProblem[0].problemType, 'drifting snow')
        self.assertIn('E', report.avalancheProblem[0].dangerRating.aspect)
        self.assertIn('NW', report.avalancheProblem[0].dangerRating.aspect)
        self.assertRaises(AttributeError, getattr, report, "predecessor_id")

if __name__ == '__main__':
    unittest.main()
