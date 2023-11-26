from avacore.processor_norway import Processor

from tests import SnowTest


class TestNorway(SnowTest):
    def test_norway(self):
        processor = Processor()
        processor.fetch_time_dependant = False
        bulletins = processor.parse_json_file("NO-3016", f"{__file__}.json")
        self.assertEqualBulletinJSON(__file__, bulletins)
