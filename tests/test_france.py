from avacore import pyAvaCore
from avacore.avabulletins import Bulletins
import unittest
import xml.etree.ElementTree as ET
import pathlib


class TestFrance(unittest.TestCase):

    def test_france(self):
        bulletins = Bulletins()
        bulletins.bulletins = pyAvaCore.process_reports_fr('FR-22', path=f'{__file__}.xml', cached=True)
        self.assertEqual(bulletins.main_date().isoformat(), "2021-03-19")
        self.assertEqual(len(bulletins.bulletins), 2)
        report = bulletins.bulletins[0]
        self.assertEqual(report.bulletinID, 'FR-22_2021-03-18T16:00:00+01:00_PM')
        self.assertEqual(report.publicationTime.isoformat(), '2021-03-18T16:00:00+01:00')
        self.assertEqual(report.validTime.startTime.isoformat(), '2021-03-19T12:00:00+01:00')
        self.assertEqual(report.validTime.endTime.isoformat(), '2021-03-19T18:00:00+01:00')
        self.assertIn('FR-22', report.get_region_list())
        self.assertNotIn('FR-10', report.get_region_list())
        self.assertEqual(report.dangerRatings[0].mainValue, 'moderate')
        #self.assertEqual(report.dangerRatings[0].valid_elevation, '<2200')
        self.assertEqual(report.dangerRatings[0].elevation.upperBound, '2200')
        self.assertEqual(report.dangerRatings[1].mainValue, 'considerable')
        #self.assertEqual(report.dangerRatings[1].valid_elevation, '>2200')
        self.assertEqual(report.dangerRatings[1].elevation.lowerBound, '2200')
        # self.assertEqual(report.dangerpattern, [])
        # self.assertEqual(report.avalancheProblem[0].problem_type, 'general')
        self.assertIn('E', report.dangerRatings[0].aspect)
        self.assertIn('SE', report.dangerRatings[0].aspect)

        self.assertEqual(report.predecessor_id, 'FR-22_2021-03-18T16:00:00+01:00')

        report = bulletins.bulletins[1]
        self.assertEqual(report.bulletinID, 'FR-22_2021-03-18T16:00:00+01:00')
        self.assertEqual(report.publicationTime.isoformat(), '2021-03-18T16:00:00+01:00')
        self.assertEqual(report.validTime.startTime.isoformat(), '2021-03-18T16:00:00+01:00')
        self.assertEqual(report.validTime.endTime.isoformat(), '2021-03-19T12:00:00+01:00')
        self.assertIn('FR-22', report.get_region_list())
        self.assertNotIn('FR-10', report.get_region_list())
        self.assertEqual(report.dangerRatings[0].mainValue, 'low')
        #self.assertEqual(report.dangerRatings[0].valid_elevation, '<2200')
        self.assertEqual(report.dangerRatings[0].elevation.upperBound, '2200')
        self.assertEqual(report.dangerRatings[1].mainValue, 'moderate')
        #self.assertEqual(report.dangerRatings[1].valid_elevation, '>2200')
        self.assertEqual(report.dangerRatings[1].elevation.lowerBound, '2200')
        # self.assertEqual(report.dangerpattern, [])
        # self.assertEqual(report.avalancheProblem[0].problem_type, 'general')
        self.assertIn('E', report.dangerRatings[0].aspect)
        self.assertIn('SE', report.dangerRatings[0].aspect)

        self.assertRaises(AttributeError, getattr, report, "predecessor_id")

if __name__ == '__main__':
    unittest.main()
