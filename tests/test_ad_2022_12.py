from avacore.processor_ad import Processor

from tests import SnowTest


class TestAD2022(SnowTest):
    def test_AD_2022_12(self):
        processor = Processor()
        bulletins = processor.parse_xml_file("", f"{__file__}.xml")
        self.assertEqualBulletinJSON(__file__, bulletins)
