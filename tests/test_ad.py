from avacore.processor_ad import Processor

from tests import SnowTest


class TestAD(SnowTest):
    def test_AD(self):
        processor = Processor()
        bulletins = processor.parse_xml_file("", f"{__file__}.xml")
        self.assertEqualBulletinJSON(__file__, bulletins)
