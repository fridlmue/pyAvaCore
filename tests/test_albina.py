from avacore import pyAvaCore
import xml.etree.ElementTree as ET

from tests import SnowTest


class TestAlbina(SnowTest):
    def test_albina(self):
        root = ET.parse(f"{__file__}.xml")
        bulletins = pyAvaCore.parse_xml(root)
        self.assertEqual(bulletins.main_date().isoformat(), "2021-02-10")
        self.assertEqualBulletinJSON(__file__, bulletins)
