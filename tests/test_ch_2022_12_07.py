from avacore.processor_ch import Processor

from tests import SnowTest


class TestCH(SnowTest):
    def test_ch_2022_json(self):
        processor = Processor()
        bulletins = processor.parse_json_file("", f"{__file__}.json")
        self.assertEqualBulletinJSON(__file__, bulletins)
