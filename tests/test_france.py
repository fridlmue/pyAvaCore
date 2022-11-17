from avacore.processor_fr import Processor

from tests import SnowTest


class TestFrance(SnowTest):
    def test_france(self):
        processor = Processor()
        bulletins = processor.parse_xml_file("", f"{__file__}.xml")
        self.assertEqualBulletinJSON(__file__, bulletins)
