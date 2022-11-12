from avacore import pyAvaCore
import pathlib

from tests import SnowTest


class TestCH(SnowTest):
    def test_ch(self):
        bulletins = pyAvaCore.process_reports_ch(
            str(pathlib.Path(__file__).parent.absolute()), cached=True, year="2021"
        )
        self.assertEqualBulletinJSON(__file__, bulletins)
