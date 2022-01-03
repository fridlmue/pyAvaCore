from avacore import pyAvaCore
from avacore.avabulletins import Bulletins
import unittest
import xml.etree.ElementTree as ET


class TestBavaria(unittest.TestCase):
    def test_bavaria(self):
        root = ET.parse(f"{__file__}.xml")
        bulletins = Bulletins()
        bulletins.bulletins = pyAvaCore.parse_xml(root)
        self.assertEqual(bulletins.main_date().isoformat(), "2021-12-29")
        # self.assertEqual(len(bulletins.bulletins), 1)
        ratings = bulletins.max_danger_ratings()
        self.assertEqual(
            ratings,
            {
                "AT-08-01:high": 3,
                "AT-08-01:low": 3,
                "AT-08-02:high": 3,
                "AT-08-02:low": 3,
                "AT-08-03-01:high": 3,
                "AT-08-03-01:low": 3,
                "AT-08-03-02:high": 3,
                "AT-08-03-02:low": 3,
                "AT-08-04:high": 3,
                "AT-08-04:low": 3,
                "AT-08-05-01:high": 3,
                "AT-08-05-01:low": 3,
                "AT-08-05-02:high": 3,
                "AT-08-05-02:low": 3,
                "AT-08-06:high": 3,
                "AT-08-06:low": 3,
            },
        )


if __name__ == "__main__":
    unittest.main()
