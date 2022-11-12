from avacore import pyAvaCore
import xml.etree.ElementTree as ET

from tests import SnowTest


class TestBavaria2021(SnowTest):
    def test_bavaria_2021(self):
        root = ET.parse(f"{__file__}.xml")
        bulletins = pyAvaCore.parse_xml(root)
        self.assertEqualBulletinJSON(__file__, bulletins)
