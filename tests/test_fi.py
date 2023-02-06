from avacore.processor_fi import Processor

import datetime
import io
import pathlib

from tests import SnowTest


class TestFI(SnowTest):
    def test(self):
        processor = Processor()
        processor.raw_data = io.BytesIO(pathlib.Path(f"{__file__}.png").read_bytes())
        processor.today = datetime.datetime.fromisoformat("2023-02-03T14:08:00")
        bulletins = processor.process_bulletin("")
        self.assertEqualBulletinJSON(__file__, bulletins)
