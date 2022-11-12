from avacore.processor_caamlv5 import SloveniaProcessor
import datetime

from tests import SnowTest


class TestSlovenia(SnowTest):
    def test_slovenia(self):
        processor = SloveniaProcessor()
        processor.today = datetime.date(2021, 3, 20)
        processor.fetch_time_dependant = False
        bulletins = processor.parse_xml_file("SI", f"{__file__}.xml")
        self.assertEqualBulletinJSON(__file__, bulletins)
