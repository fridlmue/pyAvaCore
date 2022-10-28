from avacore import pyAvaCore
import unittest
import xml.etree.ElementTree as ET

from tests import SnowTest


class TestSalzburg(SnowTest):
    def test_salzburg(self):
        root = ET.parse(f"{__file__}.xml")
        bulletins = pyAvaCore.parse_xml(root)
        self.assertEqualBulletinJSON(__file__, bulletins)


if __name__ == "__main__":
    unittest.main()
