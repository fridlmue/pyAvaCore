from avacore import pyAvaCore
import unittest
import xml.etree.ElementTree as ET


class TestBavaria(unittest.TestCase):

    def test_bavaria(self):
        root = ET.parse(f'{__file__}.xml')
        reports = pyAvaCore.parse_xml_bavaria(root)
        self.assertEqual(len(reports), 6)
        report = reports[0]
        self.assertEqual(report.report_id, 'BYCAAMLGenID3577-BYALL')
        self.assertEqual(report.rep_date.isoformat(), '2021-01-26T17:43:18')
        self.assertEqual(report.validity_begin.isoformat(), '2021-01-27T00:00:00')
        self.assertEqual(report.validity_end.isoformat(), '2021-01-27T23:59:59')
        self.assertIn('BYALL', report.valid_regions)
        self.assertNotIn('BYAMM', report.valid_regions)
        self.assertEqual(report.danger_main[0].main_value, 3)
        self.assertEqual(report.danger_main[0].valid_elevation, 'ElevationRange_1500Hi')
        self.assertEqual(report.dangerpattern, [])
        self.assertEqual(report.problem_list[0].problem_type, 'drifting snow')
        self.assertIn('aspectrange_e', report.problem_list[0].aspect)
        self.assertIn('aspectrange_nw', report.problem_list[0].aspect)
        self.assertRaises(AttributeError, getattr, report, "predecessor_id")

if __name__ == '__main__':
    unittest.main()
