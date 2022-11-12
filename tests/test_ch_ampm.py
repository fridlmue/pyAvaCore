from avacore.processor_ch import Processor

from avacore import pyAvaCore
import pathlib

from tests import SnowTest


class TestCH(SnowTest):
    def test_ch(self):
        processor = Processor()
        processor.cache_path = str(pathlib.Path(__file__).parent.absolute())
        processor.from_cache = True
        processor.year = "2021"
        bulletins = processor.process_bulletin("")
        self.assertEqualBulletinJSON(__file__, bulletins)
