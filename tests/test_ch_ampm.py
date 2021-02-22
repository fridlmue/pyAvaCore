from avacore import pyAvaCore
import unittest
import xml.etree.ElementTree as ET
import pathlib


class TestCH(unittest.TestCase):

    def test_ch(self):
        # root = ET.parse(f'{__file__}.xml')
        reports = pyAvaCore.get_reports_ch(str(pathlib.Path(__file__).parent.absolute()), cached=True)
        self.assertEqual(len(reports), 9)
        report = reports[2]
        self.assertEqual(report.report_id, '8947715')
        self.assertEqual(report.rep_date.isoformat(), '2021-02-22T17:00:00')
        self.assertEqual(report.validity_begin.isoformat(), '2021-02-22T17:00:00')
        self.assertEqual(report.validity_end.isoformat(), '2021-02-23T08:00:00')
        self.assertIn('CH-4224', report.valid_regions)
        self.assertNotIn('CH-7111', report.valid_regions)
        self.assertEqual(report.danger_main[0].main_value, 2)
        self.assertEqual(report.danger_main[0].valid_elevation, '-')
        self.assertEqual(report.dangerpattern, [])
        self.assertEqual(report.problem_list[0].problem_type, 'general')
        self.assertEqual(report.problem_list[0].valid_elevation, 'ElevationRange_2400Hi')
        self.assertIn('AspectRange_NNE', report.problem_list[0].aspect)
        self.assertIn('AspectRange_WNW', report.problem_list[0].aspect)
        self.assertNotIn('AspectRange_ESE', report.problem_list[0].aspect)

        report = reports[8]
        self.assertEqual(report.report_id, '8947712')
        self.assertEqual(report.rep_date.isoformat(), '2021-02-22T17:00:00')
        self.assertEqual(report.validity_begin.isoformat(), '2021-02-22T17:00:00')
        self.assertEqual(report.validity_end.isoformat(), '2021-02-23T08:00:00')
        self.assertIn('CH-7231', report.valid_regions)
        self.assertNotIn('CH-4224', report.valid_regions)
        self.assertEqual(report.danger_main[0].main_value, 2)
        self.assertEqual(report.danger_main[0].valid_elevation, '-')
        self.assertEqual(report.dangerpattern, [])
        self.assertEqual(report.problem_list[0].problem_type, 'general')
        self.assertEqual(report.problem_list[0].valid_elevation, 'ElevationRange_2200Hi')
        self.assertIn('AspectRange_NNE', report.problem_list[0].aspect)
        self.assertIn('AspectRange_WNW', report.problem_list[0].aspect)
        self.assertNotIn('AspectRange_SSW', report.problem_list[0].aspect)
        
        report = reports[1]
        self.assertEqual(report.report_id, '8947717')
        self.assertEqual(report.rep_date.isoformat(), '2021-02-22T17:00:00')
        self.assertEqual(report.validity_begin.isoformat(), '2021-02-22T17:00:00')
        self.assertEqual(report.validity_end.isoformat(), '2021-02-23T08:00:00')
        self.assertIn('CH-1233', report.valid_regions)
        self.assertNotIn('CH-4224', report.valid_regions)
        self.assertEqual(report.danger_main[0].main_value, 2)
        self.assertEqual(report.danger_main[0].valid_elevation, '-')
        self.assertEqual(report.dangerpattern, [])
        self.assertEqual(report.problem_list[0].problem_type, 'general')
        self.assertEqual(report.problem_list[0].valid_elevation, '')
        self.assertNotIn('AspectRange_NNE', report.problem_list[0].aspect)
        self.assertNotIn('AspectRange_WNW', report.problem_list[0].aspect)
        self.assertNotIn('AspectRange_SSW', report.problem_list[0].aspect)
if __name__ == '__main__':
    unittest.main()
