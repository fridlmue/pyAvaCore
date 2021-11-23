from avacore import pyAvaCore
import unittest
import xml.etree.ElementTree as ET


class TestVorarlberg(unittest.TestCase):

    def test_vorarlberg(self):
        root = ET.parse(f'{__file__}.xml')
        reports = pyAvaCore.parse_xml_vorarlberg(root)
        self.assertEqual(len(reports), 12)
        report = reports[2]
        self.assertEqual(report.bulletinID, 'DibosBulletinDeID5946-AT8R3')
        self.assertEqual(report.publicationTime.isoformat(), '2021-02-23T07:30:00+01:00')
        self.assertEqual(report.validTime.startTime.isoformat(), '2021-02-23T07:30:00+01:00')
        self.assertEqual(report.validTime.endTime.isoformat(), '2021-02-23T12:00:00+01:00')
        self.assertIn('AT8R3', report.get_region_list())
        self.assertNotIn('AT8R1', report.get_region_list())
        self.assertEqual(report.dangerRating[0].mainValue, 'moderate')
        self.assertEqual(report.dangerRating[0].elevation.lowerBound, '2200')
        self.assertEqual(report.dangerRating[1].mainValue, 'low')
        self.assertEqual(report.dangerRating[1].elevation.upperBound, '2200')
        self.assertEqual(report.avalancheProblem[0].problemType, 'wind_drifted_snow')
        self.assertEqual(report.avalancheProblem[1].problemType, 'wet_snow')
        self.assertRaises(AttributeError, getattr, report, "predecessor_id")
        
        report = reports[10]

        self.assertEqual(report.bulletinID, 'DibosBulletinDeID5946-AT8R5_PM')
        self.assertEqual(report.publicationTime.isoformat(), '2021-02-23T07:30:00+01:00')
        self.assertEqual(report.validTime.startTime.isoformat(), '2021-02-23T12:00:00+01:00')
        self.assertEqual(report.validTime.endTime.isoformat(), '2021-02-24T07:30:00+01:00')
        self.assertIn('AT8R5', report.get_region_list())
        self.assertNotIn('AT8R1', report.get_region_list())
        self.assertEqual(len(report.dangerRating), 1)
        self.assertEqual(report.dangerRating[0].mainValue, 'moderate')
        self.assertRaises(AttributeError, getattr, report.dangerRating[0].elevation, 'lowerBound')
        self.assertRaises(AttributeError, getattr, report.dangerRating[0].elevation, 'upperBound')
        self.assertEqual(report.avalancheProblem[0].problemType, 'wind_drifted_snow')
        self.assertEqual(report.avalancheProblem[1].problemType, 'wet_snow')
        self.assertEqual(report.predecessor_id, 'DibosBulletinDeID5946-AT8R5')

if __name__ == '__main__':
    unittest.main()
