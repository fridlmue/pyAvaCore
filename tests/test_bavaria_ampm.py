from avacore import pyAvaCore
import unittest
import xml.etree.ElementTree as ET


class TestBavariaAmPm(unittest.TestCase):

    def test_bavaria_ampm(self):
        root = ET.parse(f'{__file__}.xml')
        reports = pyAvaCore.parse_xml_bavaria(root)
        self.assertEqual(len(reports), 12)
        report = reports[0]
        self.assertEqual(report.report_id, 'BYCAAMLGenID3631-BYALL')
        self.assertEqual(report.rep_date.isoformat(), '2021-02-19T17:24:15')
        self.assertEqual(report.validity_begin.isoformat(), '2021-02-20T00:00:00')
        self.assertEqual(report.validity_end.isoformat(), '2021-02-20T11:59:59')
        self.assertIn('BYALL', report.valid_regions)
        self.assertNotIn('BYAMM', report.valid_regions)
        self.assertEqual(report.danger_main[0].main_value, 2)
        self.assertEqual(report.danger_main[0].valid_elevation, '>2000')
        self.assertEqual(report.danger_main[1].main_value, 1)
        self.assertEqual(report.danger_main[1].valid_elevation, '<2000')
        self.assertEqual(report.dangerpattern, [])
        self.assertEqual(report.problem_list[0].problem_type, 'drifting snow')
        self.assertIn('E', report.problem_list[0].aspect)
        self.assertIn('NW', report.problem_list[0].aspect)
        self.assertRaises(AttributeError, getattr, report, "predecessor_id")
        
        report = reports[7]
        self.assertEqual(report.report_id, 'BYCAAMLGenID3631-BYAMM_PM')
        self.assertEqual(report.rep_date.isoformat(), '2021-02-19T17:24:15')
        self.assertEqual(report.validity_begin.isoformat(), '2021-02-20T12:00:00')
        self.assertEqual(report.validity_end.isoformat(), '2021-02-20T23:59:59')
        self.assertIn('BYAMM', report.valid_regions)
        self.assertNotIn('BYBGD', report.valid_regions)
        self.assertEqual(report.danger_main[0].main_value, 2)
        self.assertEqual(report.danger_main[0].valid_elevation, None)
        self.assertEqual(report.dangerpattern, [])
        self.assertEqual(report.problem_list[0].problem_type, 'drifting snow')
        self.assertIn('E', report.problem_list[0].aspect)
        self.assertIn('NW', report.problem_list[0].aspect)
        self.assertEqual(report.predecessor_id, 'BYCAAMLGenID3631-BYAMM')
        
        report = reports[11]
        self.assertEqual(report.report_id, 'BYCAAMLGenID3631-BYBGD_PM')
        self.assertEqual(report.rep_date.isoformat(), '2021-02-19T17:24:15')
        self.assertEqual(report.validity_begin.isoformat(), '2021-02-20T12:00:00')
        self.assertEqual(report.validity_end.isoformat(), '2021-02-20T23:59:59')
        self.assertIn('BYBGD', report.valid_regions)
        self.assertNotIn('BYCHG', report.valid_regions)
        self.assertEqual(report.danger_main[0].main_value, 2)
        self.assertEqual(report.danger_main[0].valid_elevation, '>2000')
        self.assertEqual(report.danger_main[1].main_value, 2)
        self.assertEqual(report.danger_main[1].valid_elevation, '<2000')
        self.assertEqual(report.dangerpattern, [])
        self.assertEqual(report.problem_list[0].problem_type, 'drifting snow')
        self.assertIn('E', report.problem_list[0].aspect)
        self.assertIn('NW', report.problem_list[0].aspect)

if __name__ == '__main__':
    unittest.main()
