from avacore.processor_se import Processor

from tests import SnowTest


class TestSweden(SnowTest):
    def test_sweden(self):
        processor = Processor()
        bulletins = processor.parse_json_file("", f"{__file__}.json")
        self.assertEqualBulletinJSON(__file__, bulletins, 'SE')
