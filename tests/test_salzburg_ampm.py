from avacore import pyAvaCore
import unittest
import xml.etree.ElementTree as ET


class TestSalzburg(unittest.TestCase):

    def test_salzburg(self):
        root = ET.parse(f'{__file__}.xml')
        reports = pyAvaCore.parse_xml(root)
        self.assertEqual(len(reports), 3)
        report = reports[1]
        self.assertEqual(report.report_id, 'RID489RGR2')
        self.assertEqual(report.rep_date.isoformat(), '2021-02-25T17:00:00+00:00')
        self.assertEqual(report.validity_begin.isoformat(), '2021-02-25T23:00:00+00:00')
        self.assertEqual(report.validity_end.isoformat(), '2021-02-26T23:00:00+00:00')
        self.assertEqual([
            'AT-05-18', 'AT-05-14', 'AT-05-15', 'AT-05-17',
            'AT-05-16', 'AT-05-12', 'AT-05-08', 'AT-05-13',
            'AT-05-04', 'AT-05-21', 'AT-05-02', 'AT-05-03', 'AT-05-01'], report.valid_regions)
        self.assertEqual(report.danger_main[0].main_value, 1)
        self.assertIsNone(report.danger_main[0].valid_elevation)
        self.assertEqual(report.danger_main[1].main_value, 2)
        self.assertIsNone(report.danger_main[1].valid_elevation)
        self.assertEqual(report.problem_list[0].problem_type, 'wet snow')
        self.assertEqual(report.problem_list[1].problem_type, 'gliding snow')
        self.assertRaises(AttributeError, getattr, report, "predecessor_id")

if __name__ == '__main__':
    unittest.main()
