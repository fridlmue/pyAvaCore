from avacore.processor_uk import Processor

from tests import SnowTest


class TestGbSct(SnowTest):
    def test_gbsct(self):
        processor = Processor()
        bulletins = processor.parse_json_file('', f"{__file__}.json")
        self.assertEqualBulletinJSON(__file__, bulletins)
