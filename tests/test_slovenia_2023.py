from avacore.processor_caamlv5 import SloveniaProcessor
import datetime

from tests import SnowTest


class TestSlovenia2023(SnowTest):
    def test_slovenia_2023(self):
        processor = SloveniaProcessor()
        processor.today = datetime.date(2023, 1, 9)
        bulletins = processor.parse_xml_file("SI", f"{__file__}.xml")
        self.assertEqualBulletinJSON(__file__, bulletins, "SI")
