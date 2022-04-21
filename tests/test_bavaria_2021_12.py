from avacore import pyAvaCore
from avacore.avabulletins import Bulletins
import unittest
import xml.etree.ElementTree as ET
import datetime


class TestBavaria2021(unittest.TestCase):
    def test_bavaria_2021(self):
        root = ET.parse(f"{__file__}.xml")
        bulletins = Bulletins()
        bulletins.bulletins = pyAvaCore.parse_xml(root)
        self.assertEqual(bulletins.main_date().isoformat(), "2021-12-10")
        self.assertEqual(len(bulletins.bulletins), 3)
        ratings = bulletins.max_danger_ratings(datetime.datetime(2021, 12, 10).date())
        """
        with open(f'tests/test/{bulletins.main_date().isoformat()}-bavaria.ratings.json', mode='w', encoding='utf-8') as f:
            import json
            obj = dict(maxDangerRatings=bulletins.max_danger_ratings())
            json.dump(obj, fp=f, indent=2, sort_keys=True)
        """
        self.assertEqual(
            ratings,
            {
                "DE-BY-11": 3,
                "DE-BY-11:am": 3,
                "DE-BY-11:high": 3,
                "DE-BY-11:high:am": 3,
                "DE-BY-11:high:pm": 3,
                "DE-BY-11:low": 3,
                "DE-BY-11:low:am": 3,
                "DE-BY-11:low:pm": 3,
                "DE-BY-11:pm": 3,
                "DE-BY-12": 3,
                "DE-BY-12:am": 3,
                "DE-BY-12:high": 3,
                "DE-BY-12:high:am": 3,
                "DE-BY-12:high:pm": 3,
                "DE-BY-12:low": 3,
                "DE-BY-12:low:am": 3,
                "DE-BY-12:low:pm": 3,
                "DE-BY-12:pm": 3,
                "DE-BY-20": 3,
                "DE-BY-20:am": 3,
                "DE-BY-20:high": 3,
                "DE-BY-20:high:am": 3,
                "DE-BY-20:high:pm": 3,
                "DE-BY-20:low": 2,
                "DE-BY-20:low:am": 2,
                "DE-BY-20:low:pm": 2,
                "DE-BY-20:pm": 3,
                "DE-BY-30": 3,
                "DE-BY-30:am": 3,
                "DE-BY-30:high": 3,
                "DE-BY-30:high:am": 3,
                "DE-BY-30:high:pm": 3,
                "DE-BY-30:low": 2,
                "DE-BY-30:low:am": 2,
                "DE-BY-30:low:pm": 2,
                "DE-BY-30:pm": 3,
                "DE-BY-41": 2,
                "DE-BY-41:am": 2,
                "DE-BY-41:high": 2,
                "DE-BY-41:high:am": 2,
                "DE-BY-41:high:pm": 2,
                "DE-BY-41:low": 1,
                "DE-BY-41:low:am": 1,
                "DE-BY-41:low:pm": 1,
                "DE-BY-41:pm": 2,
                "DE-BY-42": 2,
                "DE-BY-42:am": 2,
                "DE-BY-42:high": 2,
                "DE-BY-42:high:am": 2,
                "DE-BY-42:high:pm": 2,
                "DE-BY-42:low": 1,
                "DE-BY-42:low:am": 1,
                "DE-BY-42:low:pm": 1,
                "DE-BY-42:pm": 2,
                "DE-BY-43": 2,
                "DE-BY-43:am": 2,
                "DE-BY-43:high": 2,
                "DE-BY-43:high:am": 2,
                "DE-BY-43:high:pm": 2,
                "DE-BY-43:low": 1,
                "DE-BY-43:low:am": 1,
                "DE-BY-43:low:pm": 1,
                "DE-BY-43:pm": 2,
                "DE-BY-51": 2,
                "DE-BY-51:am": 2,
                "DE-BY-51:high": 2,
                "DE-BY-51:high:am": 2,
                "DE-BY-51:high:pm": 2,
                "DE-BY-51:low": 1,
                "DE-BY-51:low:am": 1,
                "DE-BY-51:low:pm": 1,
                "DE-BY-51:pm": 2,
                "DE-BY-52": 2,
                "DE-BY-52:am": 2,
                "DE-BY-52:high": 2,
                "DE-BY-52:high:am": 2,
                "DE-BY-52:high:pm": 2,
                "DE-BY-52:low": 1,
                "DE-BY-52:low:am": 1,
                "DE-BY-52:low:pm": 1,
                "DE-BY-52:pm": 2,
                "DE-BY-60": 2,
                "DE-BY-60:am": 2,
                "DE-BY-60:high": 2,
                "DE-BY-60:high:am": 2,
                "DE-BY-60:high:pm": 2,
                "DE-BY-60:low": 1,
                "DE-BY-60:low:am": 1,
                "DE-BY-60:low:pm": 1,
                "DE-BY-60:pm": 2,
            },
        )


if __name__ == "__main__":
    unittest.main()
