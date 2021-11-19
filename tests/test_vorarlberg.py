from avacore import pyAvaCore
import unittest
import xml.etree.ElementTree as ET


class TestVorarlberg(unittest.TestCase):

    def test_vorarlberg(self):
        root = ET.parse(f'{__file__}.xml')
        reports = pyAvaCore.parse_xml_vorarlberg(root)
        self.assertEqual(len(reports), 6)
        report = reports[2]
        self.assertEqual(report.publicationTime.isoformat(), '2021-02-09T07:30:00')
        self.assertEqual(report.validTime.startTime.isoformat(), '2021-02-09T07:30:00')
        self.assertEqual(report.validTime.endTime.isoformat(), '2021-02-10T07:30:00')
        self.assertIn('AT8R3', report.get_region_list())
        self.assertNotIn('AT8R1', report.get_region_list())
        self.assertEqual(report.dangerRating[0].mainValue, 'considerable')
        self.assertEqual(report.dangerRating[0].elevation.lowerBound, '2200')
        # self.assertEqual(report.dangerPattern, ['DP6', 'DP2'])
        self.assertEqual(report.avalancheProblem[0].problemType, 'drifting snow')
        self.assertEqual(report.avalancheProblem[1].problemType, 'old snow')
        self.assertRaises(AttributeError, getattr, report, "predecessor_id")

if __name__ == '__main__':
    unittest.main()
