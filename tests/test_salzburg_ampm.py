from avacore import pyAvaCore
import unittest
import json
import xml.etree.ElementTree as ET


class TestSalzburg(unittest.TestCase):

    def test_salzburg(self):
        root = ET.parse(f'{__file__}.xml')
        reports = pyAvaCore.parse_xml(root)
        self.assertEqual(len(reports), 5)
        report = reports[0]
        self.assertEqual(report.reportId, 'RID489RGR1')
        self.assertEqual(report.rep_date.isoformat(), '2021-02-25T17:00:00+00:00')
        self.assertEqual(report.validity_begin.isoformat(), '2021-02-25T23:00:00+00:00')
        self.assertEqual(report.validity_end.isoformat(), '2021-02-26T23:00:00+00:00')
        self.assertEqual([
            'AT-05-19', 'AT-05-20'], report.valid_regions)
        self.assertEqual(report.danger_main[0].main_value, 1)
        self.assertIsNone(report.danger_main[0].valid_elevation)
        self.assertEqual(report.problem_list[0].problem_type, 'wet snow')
        self.assertEqual(report.problem_list[1].problem_type, 'gliding snow')
        self.assertRaises(AttributeError, getattr, report, "predecessor_id")
        
        report = reports[1]
        self.assertEqual(report.reportId, 'RID489RGR2')
        self.assertEqual(report.rep_date.isoformat(), '2021-02-25T17:00:00+00:00')
        self.assertEqual(report.validity_begin.isoformat(), '2021-02-25T23:00:00+00:00')
        self.assertEqual(report.validity_end.isoformat(), '2021-02-26T11:00:00+00:00')
        self.assertEqual([
            'AT-05-18', 'AT-05-14', 'AT-05-15', 'AT-05-17',
            'AT-05-16', 'AT-05-12', 'AT-05-08', 'AT-05-13',
            'AT-05-04', 'AT-05-21', 'AT-05-02', 'AT-05-03', 'AT-05-01'], report.valid_regions)
        self.assertEqual(report.danger_main[0].main_value, 1)
        self.assertIsNone(report.danger_main[0].valid_elevation)
        self.assertEqual(report.problem_list[0].problem_type, 'wet snow')
        self.assertEqual(report.problem_list[1].problem_type, 'gliding snow')
        self.assertRaises(AttributeError, getattr, report, "predecessor_id")
        
        report = reports[2]
        self.assertEqual(report.reportId, 'RID489RGR2_PM')
        self.assertEqual(report.rep_date.isoformat(), '2021-02-25T17:00:00+00:00')
        self.assertEqual(report.validity_begin.isoformat(), '2021-02-26T11:00:00+00:00')
        self.assertEqual(report.validity_end.isoformat(), '2021-02-26T23:00:00+00:00')
        self.assertEqual([
            'AT-05-18', 'AT-05-14', 'AT-05-15', 'AT-05-17',
            'AT-05-16', 'AT-05-12', 'AT-05-08', 'AT-05-13',
            'AT-05-04', 'AT-05-21', 'AT-05-02', 'AT-05-03', 'AT-05-01'], report.valid_regions)
        self.assertEqual(report.danger_main[0].main_value, 2)
        self.assertIsNone(report.danger_main[0].valid_elevation)
        self.assertEqual(report.problem_list[0].problem_type, 'wet snow')
        self.assertEqual(report.problem_list[1].problem_type, 'gliding snow')
        self.assertEqual(report.predecessor_id, 'RID489RGR2')
        
        report = reports[3]
        self.assertEqual(report.reportId, 'RID489RGR3')
        self.assertEqual(report.rep_date.isoformat(), '2021-02-25T17:00:00+00:00')
        self.assertEqual(report.validity_begin.isoformat(), '2021-02-25T23:00:00+00:00')
        self.assertEqual(report.validity_end.isoformat(), '2021-02-26T11:00:00+00:00')
        self.assertEqual([
            'AT-05-10', 'AT-05-06', 'AT-05-09', 'AT-05-05',
            'AT-05-11', 'AT-05-07'], report.valid_regions)
        self.assertEqual(report.danger_main[0].main_value, 1)
        self.assertEqual(report.danger_main[0].valid_elevation, '>2000')
        self.assertEqual(report.danger_main[1].main_value, 1)
        self.assertEqual(report.danger_main[1].valid_elevation, '<2000')
        self.assertEqual(report.problem_list[0].problem_type, 'wet snow')
        self.assertEqual(report.problem_list[1].problem_type, 'gliding snow')
        self.assertRaises(AttributeError, getattr, report, "predecessor_id")
        
        report = reports[4]
        self.assertEqual(report.reportId, 'RID489RGR3_PM')
        self.assertEqual(report.rep_date.isoformat(), '2021-02-25T17:00:00+00:00')
        self.assertEqual(report.validity_begin.isoformat(), '2021-02-26T11:00:00+00:00')
        self.assertEqual(report.validity_end.isoformat(), '2021-02-26T23:00:00+00:00')
        self.assertEqual([
            'AT-05-10', 'AT-05-06', 'AT-05-09', 'AT-05-05',
            'AT-05-11', 'AT-05-07'], report.valid_regions)
        self.assertEqual(report.danger_main[0].main_value, 1)
        self.assertEqual(report.danger_main[0].valid_elevation, '>2600')
        self.assertEqual(report.danger_main[1].main_value, 2)
        self.assertEqual(report.danger_main[1].valid_elevation, '<2600')
        self.assertEqual(report.problem_list[0].problem_type, 'wet snow')
        self.assertEqual(report.problem_list[1].problem_type, 'gliding snow')
        self.assertEqual(report.predecessor_id, 'RID489RGR3')

    def test_salzburg_json(self):
        with open(f'{__file__}.json', 'r') as f:
            expected = f.read()
        root = ET.parse(f'{__file__}.xml')
        reports = pyAvaCore.parse_xml(root)
        actual = json.dumps(reports, indent=2, cls=pyAvaCore.JSONEncoder)
        self.assertEqual(actual, expected)

if __name__ == '__main__':
    unittest.main()
