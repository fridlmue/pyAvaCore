from avacore import pyAvaCore
import unittest
import xml.etree.ElementTree as ET
import pathlib


class TestCH(unittest.TestCase):

    def test_ch(self):
        # root = ET.parse(f'{__file__}.xml')
        reports = pyAvaCore.process_reports_ch(str(pathlib.Path(__file__).parent.absolute()), cached=True, year = '2021')
        self.assertEqual(len(reports), 7)
        for idx, report in enumerate(reports):
            if report.bulletinID == '89477158947719':
                report_idx = idx
        report = reports[report_idx]
        self.assertEqual(report.bulletinID, '89477158947719')
        self.assertEqual(report.publicationTime.isoformat(), '2021-02-22T17:00:00+01:00')
        self.assertEqual(report.validTime.startTime.isoformat(), '2021-02-22T17:00:00+01:00')
        self.assertEqual(report.validTime.endTime.isoformat(), '2021-02-23T17:00:00+01:00')
        self.assertIn('CH-4224', report.get_region_list())
        self.assertNotIn('CH-7111', report.get_region_list())
        self.assertEqual(report.dangerRatings[0].mainValue, 'moderate')
        # self.assertEqual(report.dangerRatings[0].elevation, None)
        self.assertEqual(report.customData['SLF']['avalancheProneLocation']['elevation'], '2400')
        self.assertRaises(AttributeError, getattr, report.dangerRatings[0].elevation, 'upperBound')
        self.assertRaises(AttributeError, getattr, report.dangerRatings[0].elevation, 'lowerBound')
        # self.assertEqual(report.dangerpattern, [])
        # self.assertEqual(report.problem_list[0].problem_type, 'general')
        # self.assertEqual(report.problem_list[0].valid_elevation, '>2400')
        self.assertIn('N', report.customData['SLF']['avalancheProneLocation']['aspects'])
        self.assertIn('NE', report.customData['SLF']['avalancheProneLocation']['aspects'])
        self.assertIn('W', report.customData['SLF']['avalancheProneLocation']['aspects'])
        self.assertIn('NW', report.customData['SLF']['avalancheProneLocation']['aspects'])
        self.assertIn('E', report.customData['SLF']['avalancheProneLocation']['aspects'])
        self.assertNotIn('SE', report.customData['SLF']['avalancheProneLocation']['aspects'])
        self.assertNotIn('S', report.customData['SLF']['avalancheProneLocation']['aspects'])
        self.assertNotIn('SW', report.customData['SLF']['avalancheProneLocation']['aspects'])
        self.assertRaises(AttributeError, getattr, report, "predecessor_id")

        for idx, report in enumerate(reports):
            if report.bulletinID == '89477128947719':
                report_idx = idx
        report = reports[report_idx]
        self.assertEqual(report.bulletinID, '89477128947719')
        self.assertEqual(report.publicationTime.isoformat(), '2021-02-22T17:00:00+01:00')
        self.assertEqual(report.validTime.startTime.isoformat(), '2021-02-22T17:00:00+01:00')
        self.assertEqual(report.validTime.endTime.isoformat(), '2021-02-23T17:00:00+01:00')
        self.assertIn('CH-7231', report.get_region_list())
        self.assertNotIn('CH-4224', report.get_region_list())
        self.assertEqual(report.dangerRatings[0].mainValue, 'moderate')
        self.assertEqual(report.customData['SLF']['avalancheProneLocation']['elevation'], '2200')
        self.assertRaises(AttributeError, getattr, report.dangerRatings[0].elevation, 'upperBound')
        self.assertIn('N', report.customData['SLF']['avalancheProneLocation']['aspects'])
        self.assertIn('NE', report.customData['SLF']['avalancheProneLocation']['aspects'])
        self.assertIn('W', report.customData['SLF']['avalancheProneLocation']['aspects'])
        self.assertIn('NW', report.customData['SLF']['avalancheProneLocation']['aspects'])
        self.assertIn('E', report.customData['SLF']['avalancheProneLocation']['aspects'])
        self.assertNotIn('SE', report.customData['SLF']['avalancheProneLocation']['aspects'])
        self.assertNotIn('S', report.customData['SLF']['avalancheProneLocation']['aspects'])
        self.assertNotIn('SW', report.customData['SLF']['avalancheProneLocation']['aspects'])
        self.assertRaises(AttributeError, getattr, report, "predecessor_id")
        
        for idx, report in enumerate(reports):
            if report.bulletinID == '89477148947717':
                report_idx = idx
        report = reports[report_idx]
        self.assertEqual(report.bulletinID, '89477148947717')
        self.assertEqual(report.publicationTime.isoformat(), '2021-02-22T17:00:00+01:00')
        self.assertEqual(report.validTime.startTime.isoformat(), '2021-02-22T17:00:00+01:00')
        self.assertEqual(report.validTime.endTime.isoformat(), '2021-02-23T17:00:00+01:00')
        self.assertIn('CH-1233', report.get_region_list())
        self.assertNotIn('CH-4224', report.get_region_list())
        self.assertEqual(report.dangerRatings[0].mainValue, 'low')
        self.assertEqual(report.dangerRatings[1].mainValue, 'moderate')
        self.assertRaises(AttributeError, getattr, report.dangerRatings[0].elevation, 'lowerBound')
        self.assertRaises(AttributeError, getattr, report.dangerRatings[0].elevation, 'upperBound')
        self.assertNotIn('E', report.customData['SLF']['avalancheProneLocation']['aspects'])
        self.assertNotIn('SE', report.customData['SLF']['avalancheProneLocation']['aspects'])
        # self.assertEqual(report.predecessor_id, '89477148947717')

if __name__ == '__main__':
    unittest.main()
