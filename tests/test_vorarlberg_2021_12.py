from avacore import pyAvaCore
import xml.etree.ElementTree as ET

from tests import SnowTest


class TestVorarlberg2021(SnowTest):
    def test_vorarlberg_2021(self):
        root = ET.parse(f"{__file__}.xml")
        bulletins = pyAvaCore.parse_xml(root)
        self.assertEqual(bulletins.main_date().isoformat(), "2021-12-29")
        self.assertEqualBulletinJSON(__name__, bulletins)
