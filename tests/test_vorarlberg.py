from avacore import pyAvaCore
from avacore.processor_caamlv5 import parse_xml_vorarlberg
import unittest
import xml.etree.ElementTree as ET

from tests import SnowTest


class TestVorarlberg(SnowTest):
    def test_vorarlberg(self):
        root = ET.parse(f"{__file__}.xml")
        bulletins = parse_xml_vorarlberg(root)
        self.assertEqualBulletinJSON(__file__, bulletins)


if __name__ == "__main__":
    unittest.main()
