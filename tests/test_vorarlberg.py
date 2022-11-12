from avacore.processor_caamlv5 import VorarlbergProcessor

from tests import SnowTest


class TestVorarlberg(SnowTest):
    def test_vorarlberg(self):
        processor = VorarlbergProcessor()
        bulletins = processor.parse_xml_file("", f"{__file__}.xml")
        self.assertEqualBulletinJSON(__file__, bulletins)
