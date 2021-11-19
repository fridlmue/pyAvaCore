from avacore import pyAvaCore
import unittest
import xml.etree.ElementTree as ET


class TestAlbinaAmPm(unittest.TestCase):

    def test_albina_ampm(self):
        root = ET.parse(f'{__file__}.xml')
        reports = pyAvaCore.parse_xml(root)
        self.assertEqual(len(reports), 6)

        report = reports[0]
        self.assertEqual(report.bulletinID, '15b7b04b-5f3f-435c-a4f4-33a4eabeb965')
        self.assertEqual(report.publicationTime.isoformat(), '2021-02-21T16:00:00+00:00')
        self.assertEqual(report.validTime.startTime.isoformat(), '2021-02-21T23:00:00+00:00')
        self.assertEqual(report.validTime.endTime.isoformat(), '2021-02-22T11:00:00+00:00')
        self.assertIn('IT-32-TN-15', report.get_region_list())
        self.assertNotIn('IT-32-BZ-01', report.get_region_list())
        self.assertEqual(report.dangerRating[0].mainValue, 'moderate')
        self.assertEqual(report.dangerRating[0].get_mainValue_int(),  2)
        self.assertRaises(AttributeError, getattr, report.dangerRating[0].elevation, 'lowerBound')
        self.assertRaises(AttributeError, getattr, report.dangerRating[0].elevation, 'upperBound')
        self.assertEqual(report.avalancheProblem[0].problemType, 'wet snow')
        self.assertIn('S', report.avalancheProblem[0].dangerRating.aspect)
        self.assertEqual(report.avalancheProblem[1].problemType, 'gliding snow')
        self.assertIn('SW', report.avalancheProblem[1].dangerRating.aspect)
        self.assertNotIn('N', report.avalancheProblem[1].dangerRating.aspect)
        self.assertRaises(AttributeError, getattr, report, "predecessor_id")

        report = reports[5]
        self.assertEqual(report.bulletinID, '56410e01-259b-4b8e-a97b-f4628744b70e_PM')
        self.assertEqual(report.publicationTime.isoformat(), '2021-02-21T16:00:00+00:00')
        self.assertEqual(report.validTime.startTime.isoformat(), '2021-02-22T11:00:00+00:00')
        self.assertEqual(report.validTime.endTime.isoformat(), '2021-02-22T23:00:00+00:00')
        self.assertIn('AT-07-13', report.get_region_list())
        self.assertNotIn('AT-07-24', report.get_region_list())
        self.assertEqual(report.dangerRating[0].mainValue, 'moderate')
        self.assertEqual(report.dangerRating[0].get_mainValue_int(),  2)
        self.assertEqual(report.dangerRating[1].elevation.upperBound, '2600')
        self.assertEqual(report.dangerRating[0].elevation.lowerBound, '2600')
        # self.assertEqual(report.dangerpattern, ['DP10', 'DP6'])
        self.assertEqual(report.avalancheProblem[0].problemType, 'wet snow')
        self.assertIn('W', report.avalancheProblem[0].dangerRating.aspect)
        self.assertEqual(report.avalancheProblem[0].dangerRating.elevation.upperBound, '2600')
        self.assertEqual(report.avalancheProblem[1].problemType, 'drifting snow')
        self.assertIn('NE', report.avalancheProblem[1].dangerRating.aspect)
        self.assertNotIn('S', report.avalancheProblem[1].dangerRating.aspect)
        self.assertEqual(report.avalancheProblem[1].dangerRating.elevation.lowerBound, '2400')
        self.assertEqual(report.predecessor_id, '56410e01-259b-4b8e-a97b-f4628744b70e')


if __name__ == '__main__':
    unittest.main()
