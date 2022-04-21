from avacore import pyAvaCore
from avacore.avabulletins import Bulletins
import unittest
import json
import pathlib
import datetime


class TestFrance_diff_dates(unittest.TestCase):
    def test_france_diff_dates(self):

        with open(f"{__file__}.json") as fp:
            data = json.load(fp)

        bulletins = Bulletins()
        bulletins.from_json(data)

        ratings = bulletins.max_danger_ratings(datetime.datetime(2022, 4, 20).date())

        self.assertIn("FR-01", ratings)

        ratings = bulletins.max_danger_ratings(datetime.datetime(2022, 4, 21).date())
        self.assertIn("FR-04", ratings)

if __name__ == "__main__":
    unittest.main()
