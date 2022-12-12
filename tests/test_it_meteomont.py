from avacore.processor_it_meteomont import Processor

from tests import SnowTest


class TestMeteoMont(SnowTest):
    def test_it_meteomont(self):
        processor = Processor()
        bulletins = processor.parse_json_file("", f"{__file__}.json")
        self.assertEqualBulletinJSON(__file__, bulletins, 'IT-MeteoMont')
