from avacore.processor_fr import parse_reports_fr
import xml.etree.ElementTree as ET

from tests import SnowTest


class TestFrance(SnowTest):
    def test_france(self):
        root = ET.ElementTree()
        root.parse(f"{__file__}.xml")
        bulletins = parse_reports_fr(root)
        self.assertEqualBulletinJSON(__file__, bulletins)
