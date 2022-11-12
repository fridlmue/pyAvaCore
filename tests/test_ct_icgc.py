from avacore.processor_catalunya import Processor

from tests import SnowTest


class TestCtIcgc(SnowTest):
    def test_ct_icgc(self):
        processor = Processor()
        bulletins = processor.parse_json_file("", f"{__file__}.json")
        self.assertEqualBulletinJSON(__file__, bulletins)
