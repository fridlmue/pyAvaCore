from avacore import pyAvaCore
import unittest
import xml.etree.ElementTree as ET


class TestAlbinaElevationBand(unittest.TestCase):

    def test_albina_elevation_band(self):
        root = ET.parse(f'{__file__}.xml')
        reports = pyAvaCore.parse_xml(root)
        self.assertEqual(len(reports), 6)

        report = reports[0]
        self.assertEqual(report.bulletinID, '178ed2f5-9e29-4495-b34b-3a355390895b')
        self.assertEqual(report.publicationTime.isoformat(), '2021-12-29T07:00:00+00:00')
        self.assertEqual(report.validTime.startTime.isoformat(), '2021-12-28T23:00:00+00:00')
        self.assertEqual(report.validTime.endTime.isoformat(), '2021-12-29T23:00:00+00:00')
        self.assertIn('AT-07-20', report.get_region_list())
        self.assertNotIn('IT-32-BZ-01', report.get_region_list())
        self.assertEqual(report.dangerRatings[0].mainValue, 'moderate')
        self.assertEqual(report.dangerRatings[0].get_mainValue_int(),  2)
        self.assertEqual(report.dangerRatings[0].elevation.lowerBound, 'treeline')
        self.assertEqual(report.dangerRatings[0].validTimePeriod, 'earlier')
        self.assertRaises(AttributeError, getattr, report.dangerRatings[0].elevation, 'upperBound')
        self.assertEqual(report.dangerRatings[1].mainValue, 'low')
        self.assertEqual(report.dangerRatings[1].get_mainValue_int(),  1)
        self.assertEqual(report.dangerRatings[1].elevation.upperBound, 'treeline')
        self.assertEqual(report.dangerRatings[1].validTimePeriod, 'earlier')
        self.assertRaises(AttributeError, getattr, report.dangerRatings[1].elevation, 'lowerBound')
        self.assertEqual(report.dangerRatings[2].mainValue, 'high')
        self.assertEqual(report.dangerRatings[2].elevation.lowerBound, '1900')
        self.assertEqual(report.dangerRatings[2].validTimePeriod, 'later')
        self.assertRaises(AttributeError, getattr, report.dangerRatings[2].elevation, 'upperBound')
        self.assertEqual(report.dangerRatings[2].get_mainValue_int(),  4)
        self.assertEqual(report.dangerRatings[3].mainValue, 'considerable')
        self.assertEqual(report.dangerRatings[3].elevation.upperBound, '1900')
        self.assertEqual(report.dangerRatings[3].validTimePeriod, 'later')
        self.assertRaises(AttributeError, getattr, report.dangerRatings[3].elevation, 'lowerBound')
        self.assertEqual(report.dangerRatings[3].get_mainValue_int(),  3)
        
        self.assertEqual(report.avalancheProblems[0].problemType, 'wind_drifted_snow')
        self.assertIn('N', report.avalancheProblems[0].aspects)
        self.assertEqual(report.avalancheProblems[0].elevation.lowerBound, 'treeline')
        self.assertEqual(report.avalancheProblems[0].validTimePeriod, 'earlier')
        
        self.assertEqual(report.avalancheProblems[1].problemType, 'wet_snow')
        self.assertIn('S', report.avalancheProblems[1].aspects)
        self.assertEqual(report.avalancheProblems[1].elevation.lowerBound, '1900')
        self.assertEqual(report.avalancheProblems[1].elevation.upperBound, '2400')
        self.assertEqual(report.avalancheProblems[1].validTimePeriod, 'later')
        
        self.assertEqual(report.avalancheProblems[2].problemType, 'new_snow')
        self.assertIn('SW', report.avalancheProblems[2].aspects)
        self.assertEqual(report.avalancheProblems[2].elevation.lowerBound, '2400')
        self.assertEqual(report.avalancheProblems[2].validTimePeriod, 'later')
        
        self.assertEqual(report.avalancheProblems[3].problemType, 'wet_snow')
        self.assertIn('N', report.avalancheProblems[3].aspects)
        self.assertNotIn('S', report.avalancheProblems[3].aspects)
        self.assertEqual(report.avalancheProblems[3].elevation.upperBound, 'treeline')
        self.assertEqual(report.avalancheProblems[3].validTimePeriod, 'later')

if __name__ == '__main__':
    unittest.main()
