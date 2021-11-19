from avacore import pyAvaCore
import unittest
import xml.etree.ElementTree as ET
import pathlib


class TestCH(unittest.TestCase):

    def test_ch(self):
        # root = ET.parse(f'{__file__}.xml')
        reports = pyAvaCore.process_reports_ch(str(pathlib.Path(__file__).parent.absolute()), cached=True)
        self.assertEqual(len(reports), 9)
        report = reports[2]
        self.assertEqual(report.bulletinID, '8947715')
        self.assertEqual(report.publicationTime.isoformat(), '2021-02-22T17:00:00')
        self.assertEqual(report.validTime.startTime.isoformat(), '2021-02-22T17:00:00')
        self.assertEqual(report.validTime.endTime.isoformat(), '2021-02-23T17:00:00')
        self.assertIn('CH-4224', report.region)
        self.assertNotIn('CH-7111', report.region)
        self.assertEqual(report.dangerRating[0].mainValue, 'moderate')
        # self.assertEqual(report.dangerRating[0].elevation, None)
        self.assertEqual(report.dangerRating[0].elevation.lowerBound, '2400')
        self.assertRaises(AttributeError, getattr, report.dangerRating[0].elevation, 'upperBound')
        # self.assertEqual(report.dangerpattern, [])
        # self.assertEqual(report.problem_list[0].problem_type, 'general')
        # self.assertEqual(report.problem_list[0].valid_elevation, '>2400')
        self.assertIn('NNE', report.dangerRating[0].aspect)
        self.assertIn('WNW', report.dangerRating[0].aspect)
        self.assertNotIn('ESE', report.dangerRating[0].aspect)
        self.assertRaises(AttributeError, getattr, report, "predecessor_id")

        report = reports[8]
        self.assertEqual(report.bulletinID, '8947712')
        self.assertEqual(report.publicationTime.isoformat(), '2021-02-22T17:00:00')
        self.assertEqual(report.validTime.startTime.isoformat(), '2021-02-22T17:00:00')
        self.assertEqual(report.validTime.endTime.isoformat(), '2021-02-23T17:00:00')
        self.assertIn('CH-7231', report.region)
        self.assertNotIn('CH-4224', report.region)
        self.assertEqual(report.dangerRating[0].mainValue, 'moderate')
        #self.assertEqual(report.danger_main[0].valid_elevation, None)
        self.assertEqual(report.dangerRating[0].elevation.lowerBound, '2200')
        self.assertRaises(AttributeError, getattr, report.dangerRating[0].elevation, 'upperBound')
        # self.assertEqual(report.dangerpattern, [])
        # self.assertEqual(report.problem_list[0].problem_type, 'general')
        # self.assertEqual(report.problem_list[0].valid_elevation, '>2200')
        self.assertIn('NNE', report.dangerRating[0].aspect)
        self.assertIn('WNW', report.dangerRating[0].aspect)
        self.assertNotIn('SSW', report.dangerRating[0].aspect)
        self.assertRaises(AttributeError, getattr, report, "predecessor_id")
        
        report = reports[1]
        self.assertEqual(report.bulletinID, '8947717')
        self.assertEqual(report.publicationTime.isoformat(), '2021-02-22T17:00:00')
        self.assertEqual(report.validTime.startTime.isoformat(), '2021-02-22T17:00:00')
        self.assertEqual(report.validTime.endTime.isoformat(), '2021-02-23T17:00:00')
        self.assertIn('CH-1233', report.region)
        self.assertNotIn('CH-4224', report.region)
        self.assertEqual(report.dangerRating[0].mainValue, 'moderate')
        #self.assertEqual(report.danger_main[0].valid_elevation, None)
        self.assertRaises(AttributeError, getattr, report.dangerRating[0].elevation, 'lowerBound')
        self.assertRaises(AttributeError, getattr, report.dangerRating[0].elevation, 'upperBound')
        self.assertEqual(report.dangerpattern, [])
        # self.assertEqual(report.problem_list[0].problem_type, 'general')
        # self.assertEqual(report.problem_list[0].valid_elevation, None)
        self.assertNotIn('NNE', report.dangerRating[0].aspect)
        self.assertNotIn('WNW', report.dangerRating[0].aspect)
        self.assertNotIn('SSW', report.dangerRating[0].aspect)
        self.assertEqual(report.predecessor_id, '8947716_8947711_8947714')
if __name__ == '__main__':
    unittest.main()
