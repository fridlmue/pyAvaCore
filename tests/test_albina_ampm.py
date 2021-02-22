from avacore import pyAvaCore
import unittest
import xml.etree.ElementTree as ET


class TestAlbinaAmPm(unittest.TestCase):

    def test_albina_ampm(self):
        root = ET.parse(f'{__file__}.xml')
        reports = pyAvaCore.parse_xml(root)
        self.assertEqual(len(reports), 6)

        report = reports[0]
        self.assertEqual(report.report_id, '15b7b04b-5f3f-435c-a4f4-33a4eabeb965')
        self.assertEqual(report.rep_date.isoformat(), '2021-02-21T16:00:00+00:00')
        self.assertEqual(report.validity_begin.isoformat(), '2021-02-21T23:00:00+00:00')
        self.assertEqual(report.validity_end.isoformat(), '2021-02-22T11:00:00+00:00')
        self.assertIn('IT-32-TN-15', report.valid_regions)
        self.assertNotIn('IT-32-BZ-01', report.valid_regions)
        self.assertEqual(report.danger_main[0].main_value, 2)
        self.assertEqual(report.danger_main[0].valid_elevation, '-')
        self.assertEqual(report.dangerpattern, ['DP10'])
        self.assertEqual(report.problem_list[0].problem_type, 'wet snow')
        self.assertIn('AspectRange_s', report.problem_list[0].aspect)
        self.assertEqual(report.problem_list[1].problem_type, 'gliding snow')
        self.assertIn('AspectRange_sw', report.problem_list[1].aspect)
        self.assertNotIn('AspectRange_n', report.problem_list[1].aspect)
        self.assertRaises(AttributeError, getattr, report, "predecessor_id")

        report = reports[5]
        self.assertEqual(report.report_id, '56410e01-259b-4b8e-a97b-f4628744b70e_PM')
        self.assertEqual(report.rep_date.isoformat(), '2021-02-21T16:00:00+00:00')
        self.assertEqual(report.validity_begin.isoformat(), '2021-02-22T11:00:00+00:00')
        self.assertEqual(report.validity_end.isoformat(), '2021-02-22T23:00:00+00:00')
        self.assertIn('AT-07-13', report.valid_regions)
        self.assertNotIn('AT-07-24', report.valid_regions)
        self.assertEqual(report.danger_main[1].main_value, 2)
        self.assertEqual(report.danger_main[1].valid_elevation, 'ElevationRange_2600Lw')
        self.assertEqual(report.danger_main[0].valid_elevation, 'ElevationRange_2600Hi')
        self.assertEqual(report.dangerpattern, ['DP10', 'DP6'])
        self.assertEqual(report.problem_list[0].problem_type, 'wet snow')
        self.assertIn('AspectRange_w', report.problem_list[0].aspect)
        self.assertEqual(report.problem_list[0].valid_elevation, 'ElevationRange_2600Lw')
        self.assertEqual(report.problem_list[1].problem_type, 'drifting snow')
        self.assertIn('AspectRange_ne', report.problem_list[1].aspect)
        self.assertNotIn('AspectRange_s', report.problem_list[1].aspect)
        self.assertEqual(report.problem_list[1].valid_elevation, 'ElevationRange_2400Hi')
        self.assertEqual(report.predecessor_id, '56410e01-259b-4b8e-a97b-f4628744b70e')


if __name__ == '__main__':
    unittest.main()
