from avacore.processor_caamlv6 import Processor2022

from tests import SnowTest


class TestAlbina(SnowTest):
    def test_albina_2023_03_14(self):
        processor = Processor2022()
        bulletins = processor.parse_json_file("", f"{__file__}.json")
        self.assertEqualBulletinJSON(__file__, bulletins)
