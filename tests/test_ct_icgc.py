import json
from avacore import pyAvaCore
from avacore.processor_catalunya import get_reports_fromjson
import unittest
import xml.etree.ElementTree as ET


class TestCtIcgc(unittest.TestCase):

    def test_ct_icgc(self):
        with open(f'{__file__}.json') as fp:
            data = json.load(fp)
        icgc_report = data
        reports = get_reports_fromjson(icgc_report)
        
        self.assertEqual(len(reports), 7)

        report = reports[0]
        self.assertEqual(report.bulletinID, 'ES-CT-ICGC-1_2022-01-19 00:00:00+01:00')
        self.assertEqual(report.publicationTime.isoformat(), '2022-01-19T00:00:00+01:00')
        self.assertEqual(report.validTime.startTime.isoformat(), '2022-01-20T00:00:00+01:00')
        self.assertEqual(report.validTime.endTime.isoformat(), '2022-01-20T23:59:00+01:00')
        self.assertIn('ES-CT-ICGC-1', report.get_region_list())
        self.assertNotIn('ES-CT-ICGC-2', report.get_region_list())
        self.assertEqual(len(report.dangerRatings), 2)
        self.assertEqual(report.dangerRatings[0].mainValue, 'low')
        self.assertEqual(report.dangerRatings[0].get_mainValue_int(),  1)
        self.assertEqual(report.dangerRatings[1].mainValue, 'moderate')
        self.assertEqual(report.dangerRatings[1].get_mainValue_int(),  2)
        self.assertRaises(AttributeError, getattr, report.dangerRatings[0].elevation, 'lowerBound')
        self.assertRaises(AttributeError, getattr, report.dangerRatings[0].elevation, 'upperBound')
        self.assertEqual(report.avalancheProblems[0].problemType, 'wind_drifted_snow')
        # self.assertEqual(report.avalancheProblems[0].dangerRating.elevation.lowerBound, '300')
        # self.assertRaises(AttributeError, getattr, report.avalancheProblems[0].dangerRating.elevation, 'upperBound')
        # self.assertIn('S', report.avalancheProblems[0].dangerRating.aspect)
        self.assertRaises(AttributeError, getattr, report, "predecessor_id")
