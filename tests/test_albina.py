from avacore import pyAvaCore
from avacore.avabulletins import Bulletins
import unittest
import xml.etree.ElementTree as ET


# activate to export test json result
'''
import json
from pathlib import Path
from datetime import datetime


class JSONEncoder(json.JSONEncoder):
    """JSON serialization of datetime"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        try:
            return obj.toJSON()
        except: # pylint: disable=bare-except
            return obj.__dict__

'''


class TestAlbina(unittest.TestCase):
    def test_albina(self):
        root = ET.parse(f"{__file__}.xml")
        bulletins = Bulletins()
        bulletins.bulletins = pyAvaCore.parse_xml(root)
        self.assertEqual(bulletins.main_date().isoformat(), "2021-02-10")
        self.assertEqual(len(bulletins.bulletins), 6)

        report = bulletins.bulletins[0]
        self.assertEqual(
            report.publicationTime.isoformat(), "2021-02-09T16:00:00+00:00"
        )
        self.assertEqual(
            report.validTime.startTime.isoformat(), "2021-02-09T23:00:00+00:00"
        )
        self.assertEqual(
            report.validTime.endTime.isoformat(), "2021-02-10T23:00:00+00:00"
        )
        self.assertIn("AT-07-26", report.get_region_list())
        self.assertNotIn("AT-07-01", report.get_region_list())
        self.assertEqual(report.dangerRatings[0].mainValue, "considerable")
        self.assertEqual(report.dangerRatings[0].get_mainValue_int(), 3)
        self.assertEqual(report.dangerRatings[0].elevation.lowerBound, "treeline")
        self.assertEqual(report.avalancheProblems[0].problemType, "wind_drifted_snow")
        self.assertEqual(report.avalancheProblems[1].problemType, "gliding_snow")
        self.assertEqual(
            report.avalancheProblems[2].problemType, "persistent_weak_layers"
        )
        self.assertRaises(AttributeError, getattr, report, "predecessor_id")


"""        
        # activate to export test json result
        
        directory = Path('data')
        directory.mkdir(parents=True, exist_ok=True)
        
        with open(f'{directory}/export-test-albina.json', mode='w', encoding='utf-8') as f:
            json.dump(reports, fp=f, cls=JSONEncoder, indent=2)
"""

if __name__ == "__main__":
    unittest.main()
