from avacore import pyAvaCore
import xml.etree.ElementTree as ET

from tests import SnowTest


class TestAlbinaAmPm(SnowTest):
    def test_albina_ampm(self):
        root = ET.parse(f"{__file__}.xml")
        bulletins = pyAvaCore.parse_xml(root)
        self.assertEqual(bulletins.main_date().isoformat(), "2021-02-22")
        self.assertEqualBulletinJSON(__file__, bulletins)
