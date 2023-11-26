from avacore.processor_pl_12 import Processor

from tests import SnowTest


class TestPl12(SnowTest):
    def test_pl_12_2022_12_01(self):
        processor = Processor()
        processor.fetch_time_dependant = False
        bulletins = processor.parse_json_file("PL-12", f"{__file__}.json")
        self.assertEqualBulletinJSON(__file__, bulletins)
