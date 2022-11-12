from avacore.processor_ch import Processor

import io
import pathlib

from tests import SnowTest


class TestCH(SnowTest):
    def test_ch(self):
        processor = Processor()
        processor.raw_data = io.BytesIO(pathlib.Path(f"{__file__}.zip").read_bytes())
        processor.year = "2021"
        bulletins = processor.process_bulletin("")
        self.assertEqualBulletinJSON(__file__, bulletins)
