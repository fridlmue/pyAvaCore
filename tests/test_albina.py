from avacore import pyAvaCore
import unittest
import xml.etree.ElementTree as ET


class TestAlbina(unittest.TestCase):

    def test_albina(self):
        root = ET.parse(f'{__file__}.xml')
        reports = pyAvaCore.parse_xml(root)
        self.assertEqual(len(reports), 6)
        report = reports[0]
        self.assertEqual(report.rep_date.isoformat(), '2021-02-09T16:00:00+00:00')
        self.assertEqual(report.validity_begin.isoformat(), '2021-02-09T23:00:00+00:00')
        self.assertEqual(report.validity_end.isoformat(), '2021-02-10T23:00:00+00:00')
        self.assertIn('AT-07-26', report.valid_regions)
        self.assertNotIn('AT-07-01', report.valid_regions)
        self.assertEqual(report.danger_main[0].main_value, 3)
        self.assertEqual(report.danger_main[0].valid_elevation, 'ElevationRange_TreelineHi')
        self.assertEqual(report.dangerpattern, ['DP6', 'DP2'])
        self.assertEqual(report.problem_list[0].type, 'drifting snow')
        self.assertEqual(report.problem_list[1].type, 'gliding snow')
        self.assertEqual(report.problem_list[2].type, 'old snow')

if __name__ == '__main__':
    unittest.main()
