from avacore.processor_fi import Processor

import datetime
import io
import pathlib

from tests import SnowTest


class TestFI(SnowTest):
    def test(self):
        processor = Processor()
        processor.raw_data = io.BytesIO(pathlib.Path(f"{__file__}.png").read_bytes())
        processor.today = datetime.date.fromisoformat("2023-02-03")
        bulletins = processor.process_bulletin("")
        self.assertEqualBulletinJSON(__file__, bulletins)
