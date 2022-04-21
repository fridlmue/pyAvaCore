from avacore import pyAvaCore
from avacore.avabulletins import Bulletins
import unittest
import xml.etree.ElementTree as ET
import json
import datetime


class TestAlbinaRatings(unittest.TestCase):
    def test_albina_ratings(self):
        root = ET.parse(f"{__file__}.xml")
        bulletins = Bulletins()
        bulletins.bulletins = pyAvaCore.parse_xml(root)

        self.assertEqual(bulletins.main_date().isoformat(), "2022-03-22")
        self.assertEqual(len(bulletins.bulletins), 2)
        ratings = bulletins.max_danger_ratings(datetime.datetime(2022, 3, 22).date())

        relevant_ratings = {}
        for key in ratings:
            if key.startswith("AT-07"):
                relevant_ratings[key] = ratings[key]

        maxDangerRatings = {"maxDangerRatings": relevant_ratings}

        with open(f"{__file__}.ratings.json", "r") as f:
            ratings_file = json.load(f)

        with open(f"test.ratings.json", mode="w", encoding="utf-8") as f:
            json.dump(maxDangerRatings, fp=f, indent=2, sort_keys=True)

        self.assertDictEqual(maxDangerRatings, ratings_file)


if __name__ == "__main__":
    unittest.main()
