from avacore import pyAvaCore
from avacore.avabulletins import Bulletins
import unittest
import json
import pathlib


class TestFrance(unittest.TestCase):

    def test_france(self):
        
        with open(f'{__file__}.json') as fp:
            data = json.load(fp)
        bulletins = data
        
        # self.assertEqual(bulletins.main_date().isoformat(), "2022-01-10")


if __name__ == '__main__':
    unittest.main()
