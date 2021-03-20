from avacore import pyAvaCore
import unittest
import xml.etree.ElementTree as ET
import pathlib


class TestFrance(unittest.TestCase):

    def test_france(self):
        # root = ET.parse(f'{__file__}.xml')
        reports = pyAvaCore.get_reports_fr('FR-22', path=f'{__file__}.xml', cached=True)
        self.assertEqual(len(reports), 2)
        report = reports[0]
        self.assertEqual(report.report_id, 'FR-22_2021-03-18T16:00:00_PM')
        self.assertEqual(report.rep_date.isoformat(), '2021-03-18T16:00:00')
        self.assertEqual(report.validity_begin.isoformat(), '2021-03-19T12:00:00')
        self.assertEqual(report.validity_end.isoformat(), '2021-03-19T18:00:00')
        self.assertIn('FR-22', report.valid_regions)
        self.assertNotIn('FR-10', report.valid_regions)
        self.assertEqual(report.danger_main[0].main_value, 2)
        self.assertEqual(report.danger_main[0].valid_elevation, '<2200')
        self.assertEqual(report.danger_main[1].main_value, 3)
        self.assertEqual(report.danger_main[1].valid_elevation, '>2200')
        self.assertEqual(report.dangerpattern, [])
        self.assertEqual(report.problem_list[0].problem_type, 'general')
        self.assertIn('E', report.problem_list[0].aspect)
        self.assertIn('SE', report.problem_list[0].aspect)

        self.assertEqual(report.predecessor_id, 'FR-22_2021-03-18T16:00:00')

        report = reports[1]
        self.assertEqual(report.report_id, 'FR-22_2021-03-18T16:00:00')
        self.assertEqual(report.rep_date.isoformat(), '2021-03-18T16:00:00')
        self.assertEqual(report.validity_begin.isoformat(), '2021-03-18T16:00:00')
        self.assertEqual(report.validity_end.isoformat(), '2021-03-19T12:00:00')
        self.assertIn('FR-22', report.valid_regions)
        self.assertNotIn('FR-10', report.valid_regions)
        self.assertEqual(report.danger_main[0].main_value, 1)
        self.assertEqual(report.danger_main[0].valid_elevation, '<2200')
        self.assertEqual(report.danger_main[1].main_value, 2)
        self.assertEqual(report.danger_main[1].valid_elevation, '>2200')
        self.assertEqual(report.dangerpattern, [])
        self.assertEqual(report.problem_list[0].problem_type, 'general')
        self.assertIn('E', report.problem_list[0].aspect)
        self.assertIn('SE', report.problem_list[0].aspect)

        self.assertRaises(AttributeError, getattr, report, "predecessor_id")

if __name__ == '__main__':
    unittest.main()
