from avacore import pyAvaCore
import xml.etree.ElementTree as ET

from tests import SnowTest


class TestVorarlberg2022(SnowTest):
    def test_vorarlberg_2022(self):
        root = ET.parse(f"{__file__}.xml")
        bulletins = pyAvaCore.parse_xml(root)
        self.assertEqual(bulletins.main_date().isoformat(), "2022-01-31")
        self.assertEqualBulletinJSON(__file__, bulletins)
