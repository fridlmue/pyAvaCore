from pyAvaCore import pyAvaCore
import unittest
import xml.etree.ElementTree as ET

class TestAlbina(unittest.TestCase):

    def test_albina(self):
        root = ET.parse(f'{__file__}.xml')
        reports = pyAvaCore.parseXML(root)
        self.assertEqual(len(reports), 6)
        report = reports[0]
        self.assertEqual(report.repDate.isoformat(), '2021-02-09T16:00:00+00:00')
        self.assertEqual(report.timeBegin.isoformat(), '2021-02-09T23:00:00+00:00')
        self.assertEqual(report.timeEnd.isoformat(), '2021-02-10T23:00:00+00:00')
        self.assertIn('AT-07-26', report.validRegions)
        self.assertNotIn('AT-07-01', report.validRegions)
        self.assertEqual(report.dangerMain[0]['mainValue'], 3)
        self.assertEqual(report.dangerMain[0]['validElev'], 'ElevationRange_TreelineHi')
        self.assertEqual(report.dangerPattern, ['DP6', 'DP2'])
        self.assertEqual(report.problemList[0]['type'], 'drifting snow')
        self.assertEqual(report.problemList[1]['type'], 'gliding snow')
        self.assertEqual(report.problemList[2]['type'], 'old snow')

if __name__ == '__main__':
    unittest.main()
