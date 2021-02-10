from pyAvaCore import pyAvaCore
import unittest
import xml.etree.ElementTree as ET

class TestVorarlberg(unittest.TestCase):

    def test_albina(self):
        root = ET.parse(f'{__file__}.xml')
        reports = pyAvaCore.parse_xml_vorarlberg(root)
        self.assertEqual(len(reports), 7)
        report = reports[2]
        self.assertEqual(report.repDate.isoformat(), '2021-02-09T07:30:00')
        self.assertEqual(report.timeBegin.isoformat(), '2021-02-09T07:30:00')
        self.assertEqual(report.timeEnd.isoformat(), '2021-02-10T07:30:00')
        self.assertIn('AT8R3', report.validRegions)
        self.assertNotIn('AT8R1', report.validRegions)
        self.assertEqual(report.dangerMain[0].mainValue, 3)
        self.assertEqual(report.dangerMain[0].validElev, 'ElevationRange_2200Hi')
        # self.assertEqual(report.dangerPattern, ['DP6', 'DP2'])
        self.assertEqual(report.problemList[0].type, 'drifting snow')
        self.assertEqual(report.problemList[1].type, 'old snow')

if __name__ == '__main__':
    unittest.main()
