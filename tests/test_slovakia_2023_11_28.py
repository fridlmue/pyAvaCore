from avacore.processor_caamlv6 import Processor2022

from tests import SnowTest


class TestSlovakia(SnowTest):
    def test_slovakia_2023_11_28(self):
        processor = Processor2022()
        bulletins = processor.parse_json_file("", f"{__file__}.json")
        self.assertEqualBulletinJSON(__file__, bulletins)
