from avacore.processor_es import Processor

from tests import SnowTest


class TestES(SnowTest):
    def test_ES(self):
        processor = Processor()
        bulletins = processor.parse_xml_file("", f"{__file__}.xml")
        self.assertEqualBulletinJSON(__file__, bulletins)
