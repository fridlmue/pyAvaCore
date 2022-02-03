from avacore import pyAvaCore
from avacore.avabulletins import Bulletins
import unittest
import xml.etree.ElementTree as ET


class TestVorarlberg2022(unittest.TestCase):
    def test_vorarlberg_2022(self):
        root = ET.parse(f"{__file__}.xml")
        bulletins = Bulletins()
        bulletins.bulletins = pyAvaCore.parse_xml(root)
        self.assertEqual(bulletins.main_date().isoformat(), "2022-01-31")
        # self.assertEqual(len(bulletins.bulletins), 1)
        ratings = bulletins.max_danger_ratings()
        
        '''
        with open(f'tests/test/{bulletins.main_date().isoformat()}-vorarlberg_comp.ratings.json', mode='w', encoding='utf-8') as f:
            import json
            obj = dict(maxDangerRatings=bulletins.max_danger_ratings())
            json.dump(obj, fp=f, indent=2, sort_keys=True)
        '''

        self.assertEqual(
            ratings,
            {
                "AT-08-01": 3,
                "AT-08-01:am": 2,
                "AT-08-01:high": 3,
                "AT-08-01:high:am": 2,
                "AT-08-01:high:pm": 3,
                "AT-08-01:low": 2,
                "AT-08-01:low:am": 1,
                "AT-08-01:low:pm": 2,
                "AT-08-01:pm": 3,
                "AT-08-02": 3,
                "AT-08-02:am": 2,
                "AT-08-02:high": 3,
                "AT-08-02:high:am": 2,
                "AT-08-02:high:pm": 3,
                "AT-08-02:low": 2,
                "AT-08-02:low:am": 1,
                "AT-08-02:low:pm": 2,
                "AT-08-02:pm": 3,
                "AT-08-03-01": 3,
                "AT-08-03-01:am": 2,
                "AT-08-03-01:high": 3,
                "AT-08-03-01:high:am": 2,
                "AT-08-03-01:high:pm": 3,
                "AT-08-03-01:low": 2,
                "AT-08-03-01:low:am": 1,
                "AT-08-03-01:low:pm": 2,
                "AT-08-03-01:pm": 3,
                "AT-08-03-02": 3,
                "AT-08-03-02:am": 2,
                "AT-08-03-02:high": 3,
                "AT-08-03-02:high:am": 2,
                "AT-08-03-02:high:pm": 3,
                "AT-08-03-02:low": 2,
                "AT-08-03-02:low:am": 1,
                "AT-08-03-02:low:pm": 2,
                "AT-08-03-02:pm": 3,
                "AT-08-04": 3,
                "AT-08-04:am": 2,
                "AT-08-04:high": 3,
                "AT-08-04:high:am": 2,
                "AT-08-04:high:pm": 3,
                "AT-08-04:low": 2,
                "AT-08-04:low:am": 1,
                "AT-08-04:low:pm": 2,
                "AT-08-04:pm": 3,
                "AT-08-05-01": 3,
                "AT-08-05-01:am": 2,
                "AT-08-05-01:high": 3,
                "AT-08-05-01:high:am": 2,
                "AT-08-05-01:high:pm": 3,
                "AT-08-05-01:low": 2,
                "AT-08-05-01:low:am": 1,
                "AT-08-05-01:low:pm": 2,
                "AT-08-05-01:pm": 3,
                "AT-08-05-02": 3,
                "AT-08-05-02:am": 2,
                "AT-08-05-02:high": 3,
                "AT-08-05-02:high:am": 2,
                "AT-08-05-02:high:pm": 3,
                "AT-08-05-02:low": 2,
                "AT-08-05-02:low:am": 1,
                "AT-08-05-02:low:pm": 2,
                "AT-08-05-02:pm": 3,
                "AT-08-06": 3,
                "AT-08-06:am": 2,
                "AT-08-06:high": 3,
                "AT-08-06:high:am": 2,
                "AT-08-06:high:pm": 3,
                "AT-08-06:low": 2,
                "AT-08-06:low:am": 1,
                "AT-08-06:low:pm": 2,
                "AT-08-06:pm": 3
            },
        )


if __name__ == "__main__":
    unittest.main()
