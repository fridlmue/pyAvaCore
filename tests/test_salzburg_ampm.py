from avacore import pyAvaCore
import unittest
import json
import xml.etree.ElementTree as ET


class TestSalzburg(unittest.TestCase):

    def test_salzburg(self):
        root = ET.parse(f'{__file__}.xml')
        reports = pyAvaCore.parse_xml(root)
        self.assertEqual(len(reports), 5)
        report = reports[0]
        self.assertEqual(report.bulletinID, 'RID489RGR1')
        self.assertEqual(report.publicationTime.isoformat(), '2021-02-25T17:00:00+00:00')
        self.assertEqual(report.validTime.startTime.isoformat(), '2021-02-25T23:00:00+00:00')
        self.assertEqual(report.validTime.endTime.isoformat(), '2021-02-26T23:00:00+00:00')
        self.assertIn('AT-05-19', report.get_region_list())
        self.assertIn('AT-05-20', report.get_region_list())
        self.assertNotIn('AT-05-21', report.get_region_list())
        self.assertEqual(report.dangerRating[0].mainValue, 'low')
        self.assertRaises(AttributeError, getattr, report.dangerRating[0].elevation, 'lowerBound')
        self.assertRaises(AttributeError, getattr, report.dangerRating[0].elevation, 'upperBound')
        self.assertEqual(report.avalancheProblem[0].problemType, 'wet_snow')
        self.assertEqual(report.avalancheProblem[0].comment, 'daytime cycle of naturally triggered avalanches')
        self.assertEqual(report.avalancheProblem[1].problemType, 'gliding_snow')
        self.assertEqual(report.avalancheProblem[1].comment, 'in extremely steep grass-covered terrain')
        self.assertRaises(AttributeError, getattr, report, "predecessor_id")
        
        report = reports[1]
        self.assertEqual(report.bulletinID, 'RID489RGR2')
        self.assertEqual(report.publicationTime.isoformat(), '2021-02-25T17:00:00+00:00')
        self.assertEqual(report.validTime.startTime.isoformat(), '2021-02-25T23:00:00+00:00')
        self.assertEqual(report.validTime.endTime.isoformat(), '2021-02-26T11:00:00+00:00')
        '''
        self.assertEqual([
            'AT-05-18', 'AT-05-14', 'AT-05-15', 'AT-05-17',
            'AT-05-16', 'AT-05-12', 'AT-05-08', 'AT-05-13',
            'AT-05-04', 'AT-05-21', 'AT-05-02', 'AT-05-03', 'AT-05-01'], report.get_region_list())
        '''
        self.assertIn('AT-05-18', report.get_region_list())
        self.assertIn('AT-05-14', report.get_region_list())
        self.assertIn('AT-05-08', report.get_region_list())
        self.assertIn('AT-05-18', report.get_region_list())
        self.assertIn('AT-05-03', report.get_region_list())
        self.assertIn('AT-05-01', report.get_region_list())
        self.assertNotIn('AT-05-20', report.get_region_list())
        self.assertEqual(report.dangerRating[0].mainValue, 'low')
        self.assertRaises(AttributeError, getattr, report.dangerRating[0].elevation, 'lowerBound')
        self.assertRaises(AttributeError, getattr, report.dangerRating[0].elevation, 'upperBound')
        self.assertEqual(report.avalancheProblem[0].problemType, 'wet_snow')
        self.assertEqual(report.avalancheProblem[1].problemType, 'gliding_snow')
        self.assertRaises(AttributeError, getattr, report, "predecessor_id")
        
        report = reports[2]
        self.assertEqual(report.bulletinID, 'RID489RGR2_PM')
        self.assertEqual(report.publicationTime.isoformat(), '2021-02-25T17:00:00+00:00')
        self.assertEqual(report.validTime.startTime.isoformat(), '2021-02-26T11:00:00+00:00')
        self.assertEqual(report.validTime.endTime.isoformat(), '2021-02-26T23:00:00+00:00')
        '''
        self.assertEqual([
            'AT-05-18', 'AT-05-14', 'AT-05-15', 'AT-05-17',
            'AT-05-16', 'AT-05-12', 'AT-05-08', 'AT-05-13',
            'AT-05-04', 'AT-05-21', 'AT-05-02', 'AT-05-03', 'AT-05-01'], report.get_region_list())
        '''
        self.assertIn('AT-05-18', report.get_region_list())
        self.assertIn('AT-05-14', report.get_region_list())
        self.assertIn('AT-05-08', report.get_region_list())
        self.assertIn('AT-05-18', report.get_region_list())
        self.assertIn('AT-05-03', report.get_region_list())
        self.assertIn('AT-05-01', report.get_region_list())
        self.assertNotIn('AT-05-20', report.get_region_list())
        self.assertEqual(report.dangerRating[0].mainValue, 'moderate')
        self.assertRaises(AttributeError, getattr, report.dangerRating[0].elevation, 'lowerBound')
        self.assertRaises(AttributeError, getattr, report.dangerRating[0].elevation, 'upperBound')
        self.assertEqual(report.avalancheProblem[0].problemType, 'wet_snow')
        self.assertEqual(report.avalancheProblem[1].problemType, 'gliding_snow')
        self.assertEqual(report.predecessor_id, 'RID489RGR2')
        
        report = reports[3]
        self.assertEqual(report.bulletinID, 'RID489RGR3')
        self.assertEqual(report.publicationTime.isoformat(), '2021-02-25T17:00:00+00:00')
        self.assertEqual(report.validTime.startTime.isoformat(), '2021-02-25T23:00:00+00:00')
        self.assertEqual(report.validTime.endTime.isoformat(), '2021-02-26T11:00:00+00:00')
        '''
        self.assertEqual([
            'AT-05-10', 'AT-05-06', 'AT-05-09', 'AT-05-05',
            'AT-05-11', 'AT-05-07'], report.get_region_list())
        '''
        self.assertIn('AT-05-10', report.get_region_list())
        self.assertIn('AT-05-06', report.get_region_list())
        self.assertIn('AT-05-09', report.get_region_list())
        self.assertIn('AT-05-05', report.get_region_list())
        self.assertIn('AT-05-11', report.get_region_list())
        self.assertIn('AT-05-07', report.get_region_list())
        self.assertNotIn('AT-05-18', report.get_region_list())
        self.assertEqual(report.dangerRating[0].mainValue, 'low')
        # self.assertEqual(report.dangerRating[0].valid_elevation, '>2000')
        self.assertEqual(report.dangerRating[0].elevation.lowerBound, '2000')
        self.assertEqual(report.dangerRating[1].mainValue, 'low')
        # self.assertEqual(report.dangerRating[1].valid_elevation, '<2000')
        self.assertEqual(report.dangerRating[1].elevation.upperBound, '2000')
        self.assertEqual(report.avalancheProblem[0].problemType, 'wet_snow')
        self.assertEqual(report.avalancheProblem[1].problemType, 'gliding_snow')
        self.assertRaises(AttributeError, getattr, report, "predecessor_id")
        
        report = reports[4]
        self.assertEqual(report.bulletinID, 'RID489RGR3_PM')
        self.assertEqual(report.publicationTime.isoformat(), '2021-02-25T17:00:00+00:00')
        self.assertEqual(report.validTime.startTime.isoformat(), '2021-02-26T11:00:00+00:00')
        self.assertEqual(report.validTime.endTime.isoformat(), '2021-02-26T23:00:00+00:00')
        '''
        self.assertEqual([
            'AT-05-10', 'AT-05-06', 'AT-05-09', 'AT-05-05',
            'AT-05-11', 'AT-05-07'], report.get_region_list())
        '''
        self.assertIn('AT-05-10', report.get_region_list())
        self.assertIn('AT-05-06', report.get_region_list())
        self.assertIn('AT-05-09', report.get_region_list())
        self.assertIn('AT-05-05', report.get_region_list())
        self.assertIn('AT-05-11', report.get_region_list())
        self.assertIn('AT-05-07', report.get_region_list())
        self.assertNotIn('AT-05-18', report.get_region_list())
        self.assertEqual(report.dangerRating[0].mainValue, 'low')
        # self.assertEqual(report.dangerRating[0].valid_elevation, '>2600')
        self.assertEqual(report.dangerRating[0].elevation.lowerBound, '2600')
        self.assertEqual(report.dangerRating[1].mainValue, 'moderate')
        # self.assertEqual(report.dangerRating[1].valid_elevation, '<2600')
        self.assertEqual(report.dangerRating[1].elevation.upperBound, '2600')
        self.assertEqual(report.avalancheProblem[0].problemType, 'wet_snow')
        self.assertEqual(report.avalancheProblem[1].problemType, 'gliding_snow')
        self.assertEqual(report.predecessor_id, 'RID489RGR3')

    '''
    def test_salzburg_json(self):
        with open(f'{__file__}.json', 'r') as f:
            expected = f.read()
        root = ET.parse(f'{__file__}.xml')
        reports = pyAvaCore.parse_xml(root)
        actual = json.dumps(reports, indent=2, cls=pyAvaCore.JSONEncoder)
        self.assertEqual(actual, expected)
    '''

if __name__ == '__main__':
    unittest.main()
