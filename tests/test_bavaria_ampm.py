from avacore import pyAvaCore
import unittest
import xml.etree.ElementTree as ET


class TestBavariaAmPm(unittest.TestCase):

    def test_bavaria_ampm(self):
        root = ET.parse(f'{__file__}.xml')
        reports = pyAvaCore.parse_xml_bavaria(root)
        self.assertEqual(len(reports), 12)
        report = reports[0]
        self.assertEqual(report.bulletinID, 'BYCAAMLGenID3631-BYALL')
        self.assertEqual(report.publicationTime.isoformat(), '2021-02-19T17:24:15+01:00')
        self.assertEqual(report.validTime.startTime.isoformat(), '2021-02-20T00:00:00+01:00')
        self.assertEqual(report.validTime.endTime.isoformat(), '2021-02-20T11:59:59+01:00')
        self.assertIn('BYALL', report.get_region_list())
        self.assertNotIn('BYAMM', report.get_region_list())
        self.assertEqual(report.dangerRatings[0].mainValue, 'moderate')
        # self.assertEqual(report.dangerRatings[0].valid_elevation, '>2000')
        self.assertEqual(report.dangerRatings[0].elevation.lowerBound, '2000')
        self.assertEqual(report.dangerRatings[1].mainValue, 'low')
        #self.assertEqual(report.dangerRatings[1].valid_elevation, '<2000')
        self.assertEqual(report.dangerRatings[1].elevation.upperBound, '2000')
        #self.assertEqual(report.dangerpattern, [])
        self.assertEqual(report.avalancheProblems[0].problemType, 'wind_drifted_snow')
        self.assertIn('E', report.avalancheProblems[0].dangerRating.aspect)
        self.assertIn('NW', report.avalancheProblems[0].dangerRating.aspect)
        self.assertRaises(AttributeError, getattr, report, "predecessor_id")
        
        report = reports[7]
        self.assertEqual(report.bulletinID, 'BYCAAMLGenID3631-BYAMM_PM')
        self.assertEqual(report.publicationTime.isoformat(), '2021-02-19T17:24:15+01:00')
        self.assertEqual(report.validTime.startTime.isoformat(), '2021-02-20T12:00:00+01:00')
        self.assertEqual(report.validTime.endTime.isoformat(), '2021-02-20T23:59:59+01:00')
        self.assertIn('BYAMM', report.get_region_list())
        self.assertNotIn('BYBGD', report.get_region_list())
        self.assertEqual(report.dangerRatings[0].mainValue, 'moderate')
        # self.assertEqual(report.dangerRatings[0].valid_elevation, None)
        self.assertRaises(AttributeError, getattr, report.dangerRatings[0].elevation, 'lowerBound')
        self.assertRaises(AttributeError, getattr, report.dangerRatings[0].elevation, 'upperBound')
        # self.assertEqual(report.dangerpattern, [])
        self.assertEqual(report.avalancheProblems[0].problemType, 'wind_drifted_snow')
        self.assertIn('E', report.avalancheProblems[0].dangerRating.aspect)
        self.assertIn('NW', report.avalancheProblems[0].dangerRating.aspect)
        self.assertEqual(report.predecessor_id, 'BYCAAMLGenID3631-BYAMM')
        
        report = reports[11]
        self.assertEqual(report.bulletinID, 'BYCAAMLGenID3631-BYBGD_PM')
        self.assertEqual(report.publicationTime.isoformat(), '2021-02-19T17:24:15+01:00')
        self.assertEqual(report.validTime.startTime.isoformat(), '2021-02-20T12:00:00+01:00')
        self.assertEqual(report.validTime.endTime.isoformat(), '2021-02-20T23:59:59+01:00')
        self.assertIn('BYBGD', report.get_region_list())
        self.assertNotIn('BYCHG', report.get_region_list())
        self.assertEqual(report.dangerRatings[0].mainValue, 'moderate')
        #self.assertEqual(report.dangerRatings[0].valid_elevation, '>2000')
        self.assertEqual(report.dangerRatings[0].elevation.lowerBound, '2000')
        self.assertEqual(report.dangerRatings[1].mainValue, 'moderate')
        # self.assertEqual(report.dangerRatings[1].valid_elevation, '<2000')
        self.assertEqual(report.dangerRatings[1].elevation.upperBound, '2000')
        # self.assertEqual(report.dangerpattern, [])
        self.assertEqual(report.avalancheProblems[0].problemType, 'wind_drifted_snow')
        self.assertIn('E', report.avalancheProblems[0].dangerRating.aspect)
        self.assertIn('NW', report.avalancheProblems[0].dangerRating.aspect)

if __name__ == '__main__':
    unittest.main()
