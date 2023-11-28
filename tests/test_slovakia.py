from avacore.processor_sk import Processor

from tests import SnowTest


class TestSlovakia(SnowTest):
    def test_slovakia(self):
        processor = Processor()
        bulletins = processor.parse_json_file("", f"{__file__}.json")
        self.assertEqualBulletinJSON(__file__, bulletins)
