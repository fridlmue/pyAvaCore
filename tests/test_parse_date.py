from unittest import TestCase
from avacore.pyAvaCore import parse_dates


class TestDates(TestCase):
    def test_parse_date(self):
        self.assertEqual([None], parse_dates(""))
        self.assertEqual(
            ["2022-12-01"],
            parse_dates("2022-12-01"),
        )
        self.assertEqual(
            ["2022-12-01", "2022-12-04"],
            parse_dates("2022-12-01 2022-12-04"),
        )
        self.assertEqual(
            ["2022-12-01", "2022-12-02", "2022-12-03", "2022-12-04"],
            parse_dates("2022-12-01/2022-12-04"),
        )
