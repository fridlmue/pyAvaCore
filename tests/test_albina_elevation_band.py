from avacore.processor_caamlv5 import Processor

from tests import SnowTest


class TestAlbinaElevationBand(SnowTest):
    def test_albina_elevation_band(self):
        processor = Processor()
        bulletins = processor.parse_xml_file("", f"{__file__}.xml")
        self.assertEqualBulletinJSON(__file__, bulletins)
