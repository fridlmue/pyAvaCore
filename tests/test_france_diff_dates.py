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
        self.assertNotIn("FR-04", ratings)

        ratings = bulletins.max_danger_ratings(datetime.datetime(2022, 4, 21).date())
        self.assertIn("FR-04", ratings)
        self.assertNotIn("FR-02", ratings)

        dates = bulletins.main_dates(datetime.datetime(2022, 4, 20, 8, 0, 0))
        self.assertEqual(len(dates), 2)
        self.assertIn(datetime.date(2022, 4, 20), dates)
        self.assertIn(datetime.date(2022, 4, 21), dates)

        dates = bulletins.main_dates(datetime.datetime(2022, 4, 20, 15, 0, 0))
        self.assertEqual(len(dates), 1)
        self.assertIn(datetime.date(2022, 4, 21), dates)

        dates = bulletins.main_dates(datetime.datetime(2022, 4, 21, 1, 0, 0))
        self.assertEqual(len(dates), 1)
        self.assertIn(datetime.date(2022, 4, 21), dates)

        dates = bulletins.main_dates(datetime.datetime(2022, 4, 21, 14, 0, 0))
        self.assertEqual(len(dates), 1)
        self.assertIn(datetime.date(2022, 4, 21), dates)

        dates = bulletins.main_dates(datetime.datetime(2022, 4, 21, 14, 1, 0))
        self.assertEqual(len(dates), 1)
        self.assertIn(datetime.date(2022, 4, 21), dates)


if __name__ == "__main__":
    unittest.main()
