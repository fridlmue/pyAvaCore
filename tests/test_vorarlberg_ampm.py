from avacore import pyAvaCore
import unittest
import xml.etree.ElementTree as ET


class TestVorarlberg(unittest.TestCase):

    def test_vorarlberg(self):
        root = ET.parse(f'{__file__}.xml')
        reports = pyAvaCore.parse_xml_vorarlberg(root)
        self.assertEqual(len(reports), 12)
        report = reports[2]
        self.assertEqual(report.report_id, 'DibosBulletinDeID5946-AT8R3')
        self.assertEqual(report.rep_date.isoformat(), '2021-02-23T07:30:00')
        self.assertEqual(report.validity_begin.isoformat(), '2021-02-23T07:30:00')
        self.assertEqual(report.validity_end.isoformat(), '2021-02-23T12:00:00')
        self.assertIn('AT8R3', report.valid_regions)
        self.assertNotIn('AT8R1', report.valid_regions)
        self.assertEqual(report.danger_main[0].main_value, 2)
        self.assertEqual(report.danger_main[0].valid_elevation, '>2200')
        self.assertEqual(report.danger_main[1].main_value, 1)
        self.assertEqual(report.danger_main[1].valid_elevation, '<2200')
        # self.assertEqual(report.dangerPattern, ['DP6', 'DP2'])
        self.assertEqual(report.problem_list[0].problem_type, 'drifting snow')
        self.assertEqual(report.problem_list[1].problem_type, 'wet snow')
        self.assertRaises(AttributeError, getattr, report, "predecessor_id")
        
        
        report = reports[10]
        self.assertEqual(report.report_id, 'DibosBulletinDeID5946-AT8R5_PM')
        self.assertEqual(report.rep_date.isoformat(), '2021-02-23T07:30:00')
        self.assertEqual(report.validity_begin.isoformat(), '2021-02-23T12:00:00')
        self.assertEqual(report.validity_end.isoformat(), '2021-02-24T07:30:00')
        self.assertIn('AT8R5', report.valid_regions)
        self.assertNotIn('AT8R1', report.valid_regions)
        self.assertEqual(len(report.danger_main), 2)
        self.assertEqual(report.danger_main[0].main_value, 2)
        self.assertEqual(report.danger_main[0].valid_elevation, '>2200')
        self.assertEqual(report.danger_main[1].main_value, 2)
        self.assertEqual(report.danger_main[1].valid_elevation, '>2200')
        # self.assertEqual(report.dangerPattern, ['DP6', 'DP2'])
        self.assertEqual(report.problem_list[0].problem_type, 'drifting snow')
        self.assertEqual(report.problem_list[1].problem_type, 'wet snow')
        self.assertEqual(report.predecessor_id, 'DibosBulletinDeID5946-AT8R5')

if __name__ == '__main__':
    unittest.main()
