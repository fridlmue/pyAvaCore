from avacore.processor_caamlv6 import Processor

from tests import SnowTest


class TestAlbina(SnowTest):
    def test_albina_2023_11_27(self):
        processor = Processor()
        bulletins = processor.parse_json_file("", f"{__file__}.json")
        self.assertEqualBulletinJSON(__file__, bulletins)
