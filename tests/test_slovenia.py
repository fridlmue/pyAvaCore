from avacore import pyAvaCore
import unittest
import datetime
import xml.etree.ElementTree as ET


class TestSlovenia(unittest.TestCase):

    def test_slovenia(self):
        root = ET.parse(f'{__file__}.xml')
        reports = pyAvaCore.parse_xml_bavaria(root, location = 'slovenia', today = datetime.date(2021,3,20))
        self.assertEqual(len(reports), 10)
        report = reports[0]
        self.assertEqual(report.report_id, 'BulletinSiID-SI1')
        self.assertEqual(report.rep_date.isoformat(), '2021-03-19T07:47:19')
        self.assertEqual(report.validity_begin.isoformat(), '2021-03-20T00:00:00')
        self.assertEqual(report.validity_end.isoformat(), '2021-03-20T12:00:00')
        self.assertIn('SI1', report.valid_regions)
        self.assertNotIn('SI2', report.valid_regions)
        self.assertEqual(report.danger_main[0].main_value, 1)
        self.assertEqual(report.danger_main[0].valid_elevation, '<1700')
        self.assertEqual(report.dangerpattern, ['DP4'])
        self.assertEqual(report.problem_list[0].problem_type, 'drifting snow')
        self.assertIn('E', report.problem_list[0].aspect)
        self.assertIn('SE', report.problem_list[0].aspect)
        self.assertIn('W', report.problem_list[0].aspect)
        self.assertNotIn('N', report.problem_list[0].aspect)
        self.assertRaises(AttributeError, getattr, report, 'predecessor_id')

        report = reports[7]
        self.assertEqual(report.report_id, 'BulletinSiID-SI3_PM')
        self.assertEqual(report.rep_date.isoformat(), '2021-03-19T07:47:19')
        self.assertEqual(report.validity_begin.isoformat(), '2021-03-20T12:00:00')
        self.assertEqual(report.validity_end.isoformat(), '2021-03-20T23:59:59')
        self.assertIn('SI3', report.valid_regions)
        self.assertNotIn('SI1', report.valid_regions)
        self.assertEqual(report.danger_main[0].main_value, 1)
        self.assertEqual(report.danger_main[0].valid_elevation, '<1700')
        self.assertEqual(report.dangerpattern, ['DP4'])
        self.assertEqual(report.problem_list[0].problem_type, 'drifting snow')
        self.assertIn('E', report.problem_list[0].aspect)
        self.assertIn('SE', report.problem_list[0].aspect)
        self.assertIn('W', report.problem_list[0].aspect)
        self.assertNotIn('N', report.problem_list[0].aspect)
        self.assertEqual(report.predecessor_id, 'BulletinSiID-SI3')

        reports = pyAvaCore.parse_xml_bavaria(root, location = 'slovenia', today = datetime.date(2021,3,21))
        self.assertEqual(len(reports), 10)
        report = reports[0]
        self.assertEqual(report.report_id, 'BulletinSiID-SI1')
        self.assertEqual(report.rep_date.isoformat(), '2021-03-19T07:47:19')
        self.assertEqual(report.validity_begin.isoformat(), '2021-03-21T00:00:00')
        self.assertEqual(report.validity_end.isoformat(), '2021-03-21T12:00:00')
        self.assertIn('SI1', report.valid_regions)
        self.assertNotIn('SI2', report.valid_regions)
        self.assertEqual(report.danger_main[0].main_value, 1)
        self.assertEqual(report.danger_main[0].valid_elevation, '<1700')
        self.assertEqual(report.dangerpattern, ['DP4'])
        self.assertEqual(report.problem_list[0].problem_type, 'drifting snow')
        self.assertIn('E', report.problem_list[0].aspect)
        self.assertIn('SE', report.problem_list[0].aspect)
        self.assertIn('W', report.problem_list[0].aspect)
        self.assertNotIn('N', report.problem_list[0].aspect)
        self.assertRaises(AttributeError, getattr, report, 'predecessor_id')

        report = reports[7]
        self.assertEqual(report.report_id, 'BulletinSiID-SI3_PM')
        self.assertEqual(report.rep_date.isoformat(), '2021-03-19T07:47:19')
        self.assertEqual(report.validity_begin.isoformat(), '2021-03-21T12:00:00')
        self.assertEqual(report.validity_end.isoformat(), '2021-03-21T23:59:59')
        self.assertIn('SI3', report.valid_regions)
        self.assertNotIn('SI1', report.valid_regions)
        self.assertEqual(report.danger_main[0].main_value, 1)
        self.assertEqual(report.danger_main[0].valid_elevation, '<1700')
        self.assertEqual(report.dangerpattern, ['DP4'])
        self.assertEqual(report.problem_list[0].problem_type, 'drifting snow')
        self.assertIn('E', report.problem_list[0].aspect)
        self.assertIn('SE', report.problem_list[0].aspect)
        self.assertIn('W', report.problem_list[0].aspect)
        self.assertNotIn('N', report.problem_list[0].aspect)
        self.assertEqual(report.predecessor_id, 'BulletinSiID-SI3')

if __name__ == '__main__':
    unittest.main()
