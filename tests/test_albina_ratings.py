from avacore import pyAvaCore
import xml.etree.ElementTree as ET

from tests import SnowTest


class TestAlbinaRatings(SnowTest):
    def test_albina_ratings(self):
        root = ET.parse(f"{__file__}.xml")
        bulletins = pyAvaCore.parse_xml(root)
        self.assertEqual(bulletins.main_date().isoformat(), "2022-03-22")
        self.assertEqualBulletinJSON(__file__, bulletins)
