from avacore.processor_caamlv5 import Processor
import xml.etree.ElementTree as ET

from tests import SnowTest


class TestAlbinaAmPm(SnowTest):
    def test_albina_ampm(self):
        processor = Processor()
        bulletins = processor.parse_xml_file("", f"{__file__}.xml")
        self.assertEqual(bulletins.main_date().isoformat(), "2021-02-22")
        self.assertEqualBulletinJSON(__file__, bulletins)
