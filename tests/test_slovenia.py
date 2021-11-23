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
        self.assertEqual(report.bulletinID, 'BulletinSiID-SI1')
        self.assertEqual(report.publicationTime.isoformat(), '2021-03-19T07:47:19+01:00')
        self.assertEqual(report.validTime.startTime.isoformat(), '2021-03-20T00:00:00+01:00')
        self.assertEqual(report.validTime.endTime.isoformat(), '2021-03-20T12:00:00+01:00')
        self.assertIn('SI1', report.get_region_list())
        self.assertNotIn('SI2', report.get_region_list())
        self.assertEqual(report.dangerRating[0].mainValue, 'low')
        #self.assertEqual(report.danger_main[0].valid_elevation, '<1700')
        self.assertEqual(report.dangerRating[0].elevation.upperBound, '1700')
        # self.assertEqual(report.dangerpattern, ['DP4'])
        self.assertEqual(report.avalancheProblem[0].problemType, 'wind_drifted_snow')
        self.assertIn('E', report.avalancheProblem[0].dangerRating.aspect)
        self.assertIn('SE', report.avalancheProblem[0].dangerRating.aspect)
        self.assertIn('W', report.avalancheProblem[0].dangerRating.aspect)
        self.assertNotIn('N', report.avalancheProblem[0].dangerRating.aspect)
        self.assertRaises(AttributeError, getattr, report, 'predecessor_id')

        report = reports[7]
        self.assertEqual(report.bulletinID, 'BulletinSiID-SI3_PM')
        self.assertEqual(report.publicationTime.isoformat(), '2021-03-19T07:47:19+01:00')
        self.assertEqual(report.validTime.startTime.isoformat(), '2021-03-20T12:00:00+01:00')
        self.assertEqual(report.validTime.endTime.isoformat(), '2021-03-20T23:59:59.999000+01:00')
        self.assertIn('SI3', report.get_region_list())
        self.assertNotIn('SI1', report.get_region_list())
        self.assertEqual(report.dangerRating[0].mainValue, 'low')
        # self.assertEqual(report.danger_main[0].valid_elevation, '<1700')
        self.assertEqual(report.dangerRating[0].elevation.upperBound, '1700')
        # self.assertEqual(report.dangerpattern, ['DP4'])
        self.assertEqual(report.avalancheProblem[0].problemType, 'wind_drifted_snow')
        self.assertIn('E', report.avalancheProblem[0].dangerRating.aspect)
        self.assertIn('SE', report.avalancheProblem[0].dangerRating.aspect)
        self.assertIn('W', report.avalancheProblem[0].dangerRating.aspect)
        self.assertNotIn('N', report.avalancheProblem[0].dangerRating.aspect)
        self.assertEqual(report.predecessor_id, 'BulletinSiID-SI3')

        reports = pyAvaCore.parse_xml_bavaria(root, location = 'slovenia', today = datetime.date(2021,3,21))
        self.assertEqual(len(reports), 10)
        report = reports[0]
        self.assertEqual(report.bulletinID, 'BulletinSiID-SI1')
        self.assertEqual(report.publicationTime.isoformat(), '2021-03-19T07:47:19+01:00')
        self.assertEqual(report.validTime.startTime.isoformat(), '2021-03-21T00:00:00+01:00')
        self.assertEqual(report.validTime.endTime.isoformat(), '2021-03-21T12:00:00+01:00')
        self.assertIn('SI1', report.get_region_list())
        self.assertNotIn('SI2', report.get_region_list())
        self.assertEqual(report.dangerRating[0].mainValue, 'low')
        # self.assertEqual(report.danger_main[0].valid_elevation, '<1700')
        self.assertEqual(report.dangerRating[0].elevation.upperBound, '1700')
        # self.assertEqual(report.dangerpattern, ['DP4'])
        self.assertEqual(report.avalancheProblem[0].problemType, 'wind_drifted_snow')
        self.assertIn('E', report.avalancheProblem[0].dangerRating.aspect)
        self.assertIn('SE', report.avalancheProblem[0].dangerRating.aspect)
        self.assertIn('W', report.avalancheProblem[0].dangerRating.aspect)
        self.assertNotIn('N', report.avalancheProblem[0].dangerRating.aspect)
        self.assertRaises(AttributeError, getattr, report, 'predecessor_id')

        report = reports[7]
        self.assertEqual(report.bulletinID, 'BulletinSiID-SI3_PM')
        self.assertEqual(report.publicationTime.isoformat(), '2021-03-19T07:47:19+01:00')
        self.assertEqual(report.validTime.startTime.isoformat(), '2021-03-21T12:00:00+01:00')
        self.assertEqual(report.validTime.endTime.isoformat(), '2021-03-21T23:59:59.999000+01:00')
        self.assertIn('SI3', report.get_region_list())
        self.assertNotIn('SI1', report.get_region_list())
        self.assertEqual(report.dangerRating[0].mainValue, 'low')
        # self.assertEqual(report.danger_main[0].valid_elevation, '<1700')
        self.assertEqual(report.dangerRating[0].elevation.upperBound, '1700')
        # self.assertEqual(report.dangerpattern, ['DP4'])
        self.assertEqual(report.avalancheProblem[0].problemType, 'wind_drifted_snow')
        self.assertIn('E', report.avalancheProblem[0].dangerRating.aspect)
        self.assertIn('SE', report.avalancheProblem[0].dangerRating.aspect)
        self.assertIn('W', report.avalancheProblem[0].dangerRating.aspect)
        self.assertNotIn('N', report.avalancheProblem[0].dangerRating.aspect)
        self.assertEqual(report.predecessor_id, 'BulletinSiID-SI3')

if __name__ == '__main__':
    unittest.main()
