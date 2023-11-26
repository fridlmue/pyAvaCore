from avacore.processor_is import Processor

from tests import SnowTest


class TestIceland(SnowTest):
    def test_iceland(self):
        processor = Processor()
        bulletins = processor.parse_xml_file("", f"{__file__}.xml")
        self.assertEqualBulletinJSON(__file__, bulletins)
