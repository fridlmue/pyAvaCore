from avacore.processor_caamlv5 import Processor

from tests import SnowTest


class TestVorarlberg(SnowTest):
    def test_vorarlberg(self):
        processor = Processor()
        bulletins = processor.parse_xml_file("", f"{__file__}.xml")
        self.assertEqual(bulletins.main_date().isoformat(), "2022-01-31")
        self.assertEqualBulletinJSON(__file__, bulletins)
