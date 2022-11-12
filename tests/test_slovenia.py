from avacore import pyAvaCore
import datetime
import xml.etree.ElementTree as ET

from tests import SnowTest


class TestSlovenia(SnowTest):
    def test_slovenia(self):
        root = ET.parse(f"{__file__}.xml")
        bulletins = pyAvaCore.parse_xml_bavaria(
            root,
            location="slovenia",
            today=datetime.date(2021, 3, 20),
            fetch_time_dependant=False,
        )
        self.assertEqualBulletinJSON(__file__, bulletins)
