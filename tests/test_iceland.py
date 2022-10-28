from avacore.processor_is import parse_reports_is
import xml.etree.ElementTree as ET

from tests import SnowTest


class TestIceland(SnowTest):
    def test_iceland(self):
        root = ET.ElementTree()
        root.parse(f"{__file__}.xml")
        bulletins = parse_reports_is(root)
        self.assertEqualBulletinJSON(__file__, bulletins)
