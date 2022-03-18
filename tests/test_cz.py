import json
from avacore import pyAvaCore
from avacore.processor_cz import get_reports_fromjson
import unittest

class TestCZ(unittest.TestCase):

    def test_cz(self):
        with open(f'{__file__}.json') as fp:
            data = json.load(fp)
        cz_report = data
        reports = get_reports_fromjson(cz_report, fetch_time_dependant=False)
        
        self.assertEqual(len(reports), 2)

        report = reports[0]
        self.assertEqual(report.bulletinID, '2825')
        self.assertEqual(report.publicationTime.isoformat(), '2022-03-15T07:48:00+01:00')
        self.assertEqual(report.validTime.startTime.isoformat(), '2022-03-15T07:48:00+01:00')
        self.assertEqual(report.validTime.endTime.isoformat(), '2022-03-16T07:48:00+01:00')
        self.assertIn('CZ-04', report.get_region_list())
        self.assertNotIn('CZ-06', report.get_region_list())
        self.assertEqual(report.dangerRatings[0].mainValue, 'moderate')
        self.assertEqual(report.dangerRatings[0].get_mainValue_int(),  2)
        self.assertRaises(AttributeError, getattr, report.dangerRatings[0].elevation, 'lowerBound')
        self.assertRaises(AttributeError, getattr, report.dangerRatings[0].elevation, 'upperBound')
        self.assertEqual(report.avalancheProblems[0].problemType, 'wet_snow')
        self.assertRaises(AttributeError, getattr, report.avalancheProblems[0].elevation, 'upperBound')
        self.assertIn('E', report.avalancheProblems[0].aspects)
        self.assertRaises(AttributeError, getattr, report, "predecessor_id")
        
        report = reports[1]
        self.assertEqual(report.bulletinID, '2826')
        self.assertEqual(report.publicationTime.isoformat(), '2022-03-15T08:36:01+01:00')
        self.assertEqual(report.validTime.startTime.isoformat(), '2022-03-15T08:36:01+01:00')
        self.assertEqual(report.validTime.endTime.isoformat(), '2022-03-16T08:36:01+01:00')
        self.assertIn('CZ-06', report.get_region_list())
        self.assertNotIn('CZ-04', report.get_region_list())
        self.assertEqual(report.dangerRatings[0].mainValue, 'moderate')
        self.assertEqual(report.dangerRatings[0].get_mainValue_int(),  2)
        self.assertEqual(report.avalancheProblems[0].problemType, 'wind_drifted_snow')
        self.assertRaises(AttributeError, getattr, report.avalancheProblems[0].elevation, 'upperBound')
        self.assertIn('N', report.avalancheProblems[0].aspects)
        self.assertRaises(AttributeError, getattr, report, "predecessor_id")

