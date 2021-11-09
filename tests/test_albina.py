from avacore import pyAvaCore
import unittest
import xml.etree.ElementTree as ET


class TestAlbina(unittest.TestCase):

    def test_albina(self):
        root = ET.parse(f'{__file__}.xml')
        reports = pyAvaCore.parse_xml(root)
        self.assertEqual(len(reports), 6)
        report = reports[0]
        self.assertEqual(report.publicationTime.isoformat(), '2021-02-09T16:00:00+00:00')
        self.assertEqual(report.validTime.startTime.isoformat(), '2021-02-09T23:00:00+00:00')
        self.assertEqual(report.validTime.endTime.isoformat(), '2021-02-10T23:00:00+00:00')
        self.assertIn('AT-07-26', report.region)
        self.assertNotIn('AT-07-01', report.region)
        # self.assertEqual(report.danger_main[0].main_value, 3)
        self.assertEqual(report.dangerRating[0].mainValue, 'considerable')
        self.assertEqual(report.dangerRating[0].get_mainValue_int(), 3)
        # self.assertEqual(report.danger_main[0].valid_elevation, '>Treeline')
        self.assertEqual(report.dangerRating[0].elevation.upperBound, 'Treeline')
        # self.assertEqual(report.dangerpattern, ['DP6', 'DP2'])
        self.assertEqual(report.avalancheProblem[0].problemType, 'drifting snow')
        self.assertEqual(report.avalancheProblem[1].problemType, 'gliding snow')
        self.assertEqual(report.avalancheProblem[2].problemType, 'old snow')
        #self.assertEqual(report.problem_list[0].problem_type, 'drifting snow')
        #self.assertEqual(report.problem_list[1].problem_type, 'gliding snow')
        #self.assertEqual(report.problem_list[2].problem_type, 'old snow')
        self.assertRaises(AttributeError, getattr, report, "predecessor_id")

if __name__ == '__main__':
    unittest.main()
