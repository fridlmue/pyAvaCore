from avacore.processor_caamlv5 import BavariaProcessor

from tests import SnowTest


class TestBavaria(SnowTest):
    def test_bavaria(self):
        processor = BavariaProcessor()
        bulletins = processor.parse_xml_file("DE-BY", f"{__file__}.xml")
        self.assertEqualBulletinJSON(__file__, bulletins, "DE-BY")
