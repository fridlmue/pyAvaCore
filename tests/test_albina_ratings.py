from avacore.processor_caamlv5 import Processor

from tests import SnowTest


class TestAlbinaRatings(SnowTest):
    def test_albina_ratings(self):
        processor = Processor()
        bulletins = processor.parse_xml_file("", f"{__file__}.xml")
        self.assertEqual(bulletins.main_date().isoformat(), "2022-03-22")
        self.assertEqualBulletinJSON(__file__, bulletins)
