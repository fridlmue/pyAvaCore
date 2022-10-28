from avacore import pyAvaCore
import xml.etree.ElementTree as ET

from tests import SnowTest


class TestBavariaAmPm(SnowTest):
    def test_bavaria_ampm(self):
        root = ET.parse(f"{__file__}.xml")
        bulletins = pyAvaCore.parse_xml_bavaria(root)
        self.assertEqualBulletinJSON(__file__, bulletins)
