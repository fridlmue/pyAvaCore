from avacore.processor_caamlv5 import Processor

from tests import SnowTest


class TestAlbina(SnowTest):
    def test_albina(self):
        processor = Processor()
        bulletins = processor.parse_xml_file("", f"{__file__}.xml")
        self.assertEqual(bulletins.main_date().isoformat(), "2021-02-10")
        self.assertEqualBulletinJSON(__file__, bulletins)
