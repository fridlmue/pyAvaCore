from pyAvaCore import pyAvaCore
import unittest
import xml.etree.ElementTree as ET

class TestAlbina(unittest.TestCase):

    def test_albina(self):
        root = ET.parse(f'{__file__}.xml')
        reports = pyAvaCore.parseXML(root)
        self.assertEqual(len(reports), 6)

if __name__ == '__main__':
    unittest.main()
