from avacore.processor_cz import Processor

from tests import SnowTest


class TestCZ(SnowTest):
    def test_cz(self):
        processor = Processor()
        bulletins = processor.parse_json_file('', f"{__file__}.json")
        self.assertEqualBulletinJSON(__file__, bulletins)
