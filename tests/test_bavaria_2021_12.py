from avacore import pyAvaCore
from avacore.avabulletins import Bulletins
import unittest
import xml.etree.ElementTree as ET


class TestBavaria(unittest.TestCase):
    def test_bavaria(self):
        root = ET.parse(f"{__file__}.xml")
        bulletins = Bulletins()
        bulletins.bulletins = pyAvaCore.parse_xml(root)
        ratings = bulletins.max_danger_ratings()
        self.assertEqual(
            ratings,
            {
                "DE-BY-11:high": 3,
                "DE-BY-11:low": 3,
                "DE-BY-12:high": 3,
                "DE-BY-12:low": 3,
                "DE-BY-20:high": 3,
                "DE-BY-20:low": 2,
                "DE-BY-30:high": 3,
                "DE-BY-30:low": 2,
                "DE-BY-41:high": 2,
                "DE-BY-41:low": 1,
                "DE-BY-42:high": 2,
                "DE-BY-42:low": 1,
                "DE-BY-43:high": 2,
                "DE-BY-43:low": 1,
                "DE-BY-51:high": 2,
                "DE-BY-51:low": 1,
                "DE-BY-52:high": 2,
                "DE-BY-52:low": 1,
                "DE-BY-60:high": 2,
                "DE-BY-60:low": 1,
            },
        )


if __name__ == "__main__":
    unittest.main()
