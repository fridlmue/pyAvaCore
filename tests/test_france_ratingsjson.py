from avacore import pyAvaCore
from avacore.avabulletins import Bulletins
import unittest
import json
import pathlib
import datetime


class TestFrance_dangerratings(unittest.TestCase):
    def test_france_dangerratings(self):

        with open(f"{__file__}.json") as fp:
            data = json.load(fp)

        bulletins = Bulletins()
        bulletins.from_json(data)

        ratings = bulletins.max_danger_ratings(datetime.datetime(2022, 1, 10).date())

        self.assertEqual(ratings["FR-01"], 4)
        self.assertEqual(ratings["FR-01:am"], 4)
        self.assertEqual(ratings["FR-01:pm"], 3)
        self.assertEqual(ratings["FR-01:low"], 3)
        self.assertEqual(ratings["FR-01:high"], 4)
        self.assertEqual(ratings["FR-01:low:pm"], 3)
        self.assertEqual(ratings["FR-01:low:am"], 3)
        self.assertEqual(ratings["FR-01:high:pm"], 3)
        self.assertEqual(ratings["FR-01:high:am"], 4)
