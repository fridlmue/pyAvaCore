from avacore.processor_caamlv5 import Processor

from tests import SnowTest


class TestBavaria2021(SnowTest):
    def test_bavaria_2021(self):
        processor = Processor()
        bulletins = processor.parse_xml_file("", f"{__file__}.xml")
        self.assertEqualBulletinJSON(__file__, bulletins)
