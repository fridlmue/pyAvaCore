from avacore import pyAvaCore
import unittest
import xml.etree.ElementTree as ET

from tests import SnowTest


class TestSalzburg(SnowTest):
    def test_salzburg(self):
        root = ET.parse(f"{__file__}.xml")
        json = pyAvaCore.parse_xml(root).to_json()
        self.assertEqualJSON(__file__, json)


if __name__ == "__main__":
    unittest.main()
