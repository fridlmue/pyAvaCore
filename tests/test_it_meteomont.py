from avacore.processor_it_meteomont import Processor

from tests import SnowTest


class TestMeteoMont(SnowTest):
    def test_it_meteomont(self):
        processor = Processor()
        processor.add_eaws_id = True
        bulletins = processor.parse_json_file("", f"{__file__}.json")
        self.assertEqual("2022-12-12", bulletins.main_date().isoformat())
        self.assertEqual(
            ["2022-12-12", "2022-12-13", "2022-12-14", "2022-12-15"],
            sorted([d.isoformat() for d in bulletins.main_dates()]),
        )
        self.assertEqualBulletinJSON(
            __file__,
            bulletins,
            region_id="IT-MeteoMont",
            date="2022-12-12",
        )
