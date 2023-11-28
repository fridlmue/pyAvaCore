import datetime
import io
import unittest
from tests import SnowTest
import avacore.processor
import avacore.processor_ad
import avacore.processor_caamlv5
import avacore.processor_caamlv6
import avacore.processor_catalunya
import avacore.processor_ch
import avacore.processor_ch_zip
import avacore.processor_cz
import avacore.processor_es
import avacore.processor_fi
import avacore.processor_fr
import avacore.processor_is
import avacore.processor_it_livigno
import avacore.processor_it_meteomont
import avacore.processor_norway
import avacore.processor_pl
import avacore.processor_pl_12
import avacore.processor_se
import avacore.processor_sk
import avacore.processor_uk


class TestAll(SnowTest):
    def test_ad(self):
        processor = avacore.processor_ad.Processor()
        bulletins = processor.parse_xml_file("", self._xml)
        self.assertEqualBulletinJSON(bulletins)

    def test_ad_2022_12(self):
        processor = avacore.processor_ad.Processor()
        bulletins = processor.parse_xml_file("", self._xml)
        self.assertEqualBulletinJSON(bulletins)

    def test_albina_2023_03_14(self):
        processor = avacore.processor_caamlv6.Processor2022()
        bulletins = processor.parse_json_file("", self._json)
        self.assertEqualBulletinJSON(bulletins)

    def test_aineva(self):
        processor = avacore.processor_caamlv5.Processor()
        bulletins = processor.parse_xml_file("", self._xml)
        self.assertEqualBulletinJSON(bulletins)

    def test_albina_2023_11_27(self):
        processor = avacore.processor_caamlv6.Processor()
        bulletins = processor.parse_json_file("", self._json)
        self.assertEqualBulletinJSON(bulletins)

    def test_albina_ampm(self):
        processor = avacore.processor_caamlv5.Processor()
        bulletins = processor.parse_xml_file("", self._xml)
        self.assertEqual(bulletins.main_date().isoformat(), "2021-02-22")
        self.assertEqualBulletinJSON(bulletins)

    def test_albina_elevation_band(self):
        processor = avacore.processor_caamlv5.Processor()
        bulletins = processor.parse_xml_file("", self._xml)
        self.assertEqualBulletinJSON(bulletins)

    def test_albina_ratings(self):
        processor = avacore.processor_caamlv5.Processor()
        bulletins = processor.parse_xml_file("", self._xml)
        self.assertEqual(bulletins.main_date().isoformat(), "2022-03-22")
        self.assertEqualBulletinJSON(bulletins)

    def test_albina(self):
        processor = avacore.processor_caamlv5.Processor()
        bulletins = processor.parse_xml_file("", self._xml)
        self.assertEqual(bulletins.main_date().isoformat(), "2021-02-10")
        self.assertEqualBulletinJSON(bulletins)

    def test_bavaria_2021_12(self):
        processor = avacore.processor_caamlv5.Processor()
        bulletins = processor.parse_xml_file("", self._xml)
        self.assertEqualBulletinJSON(bulletins)

    def test_bavaria_ampm(self):
        processor = avacore.processor_caamlv5.BavariaProcessor()
        bulletins = processor.parse_xml_file("DE-BY", self._xml)
        self.assertEqualBulletinJSON(bulletins, "DE-BY")

    def test_bavaria(self):
        processor = avacore.processor_caamlv5.BavariaProcessor()
        bulletins = processor.parse_xml_file("DE-BY", self._xml)
        self.assertEqualBulletinJSON(bulletins, "DE-BY")

    def test_ch_2022_12_07(self):
        processor = avacore.processor_ch.Processor()
        bulletins = processor.parse_json_file("", self._json)
        self.assertEqualBulletinJSON(bulletins)

    def test_ch_2022_12(self):
        processor = avacore.processor_ch_zip.Processor()
        processor.raw_data = io.BytesIO(self._fixture("zip").read_bytes())
        processor.year = 2022
        bulletins = processor.process_bulletin("")
        self.assertEqualBulletinJSON(bulletins)

    def test_ch_2023_02_14(self):
        processor = avacore.processor_ch.Processor()
        bulletins = processor.parse_json_file("", self._json)
        self.assertEqualBulletinJSON(bulletins)

    def test_ch_2023_11_27(self):
        processor = avacore.processor_caamlv6.Processor()
        bulletins = processor.parse_json_file("", self._json)
        self.assertEqualBulletinJSON(bulletins)

    @unittest.skip("2021 format unsupported")
    def test_ch_ampm(self):
        processor = avacore.processor_ch_zip.Processor()
        processor.raw_data = io.BytesIO(self._fixture("zip").read_bytes())
        processor.year = 2021
        bulletins = processor.process_bulletin("")
        self.assertEqualBulletinJSON(bulletins)

    def test_ct_icgc(self):
        processor = avacore.processor_catalunya.Processor()
        bulletins = processor.parse_json_file("", self._json)
        self.assertEqualBulletinJSON(bulletins)

    def test_cz(self):
        processor = avacore.processor_cz.Processor()
        bulletins = processor.parse_json_file("", self._json)
        self.assertEqualBulletinJSON(bulletins)

    def test_es_am_pm(self):
        processor = avacore.processor_es.Processor()
        bulletins = processor.parse_xml_file("", self._xml)
        self.assertEqualBulletinJSON(bulletins)

    def test_es(self):
        processor = avacore.processor_es.Processor()
        bulletins = processor.parse_xml_file("", self._xml)
        self.assertEqualBulletinJSON(bulletins)

    def test_fi(self):
        processor = avacore.processor_fi.Processor()
        processor.raw_data = io.BytesIO(self._fixture("png").read_bytes())
        processor.today = datetime.datetime.fromisoformat("2023-02-03T14:08:00")
        bulletins = processor.process_bulletin("")
        self.assertEqualBulletinJSON(bulletins)

    def test_france(self):
        processor = avacore.processor_fr.Processor()
        bulletins = processor.parse_xml_file("", self._xml)
        self.assertEqualBulletinJSON(bulletins)

    def test_gbsct(self):
        processor = avacore.processor_uk.Processor()
        bulletins = processor.parse_json_file("", self._json)
        self.assertEqualBulletinJSON(bulletins)

    def test_iceland(self):
        processor = avacore.processor_is.Processor()
        bulletins = processor.parse_xml_file("", self._xml)
        self.assertEqualBulletinJSON(bulletins)

    def test_it_livigno(self):
        processor = avacore.processor_it_livigno.Processor()
        html = self._fixture("html").read_text("utf-8")
        bulletins = processor.parse_html("IT-Livigno", html)
        self.assertEqual("2022-12-18", bulletins.main_date().isoformat())
        self.assertEqualBulletinJSON(bulletins)

    def test_it_meteomont(self):
        processor = avacore.processor_it_meteomont.Processor()
        processor.add_eaws_id = True
        bulletins = processor.parse_json_file("", self._json)
        self.assertEqual("2022-12-12", bulletins.main_date().isoformat())
        self.assertEqual(
            ["2022-12-12", "2022-12-13", "2022-12-14", "2022-12-15"],
            sorted([d.isoformat() for d in bulletins.main_dates()]),
        )
        self.assertEqualBulletinJSON(
            bulletins, region_id="IT-MeteoMont", date="2022-12-12"
        )

    def test_norway(self):
        processor = avacore.processor_norway.Processor()
        processor.fetch_time_dependant = False
        bulletins = processor.parse_json_file("NO-3016", self._json)
        self.assertEqualBulletinJSON(bulletins)

    def test_pl_12_2022_12_01(self):
        processor = avacore.processor_pl_12.Processor()
        processor.fetch_time_dependant = False
        bulletins = processor.parse_json_file("PL-12", self._json)
        self.assertEqualBulletinJSON(bulletins)

    def test_pl_2018_02_09(self):
        processor = avacore.processor_pl.Processor()
        processor.fetch_time_dependant = False
        html = self._fixture("html").read_text("utf-8")
        bulletins = processor.parse_html("PL-01", html)
        self.assertEqualBulletinJSON(bulletins)

    def test_pl_2019_01_09(self):
        processor = avacore.processor_pl.Processor()
        processor.fetch_time_dependant = False
        html = self._fixture("html").read_text("utf-8")
        bulletins = processor.parse_html("PL-01", html)
        self.assertEqualBulletinJSON(bulletins)

    def test_salzburg_ampm(self):
        processor = avacore.processor_caamlv5.Processor()
        bulletins = processor.parse_xml_file("", self._xml)
        self.assertEqualBulletinJSON(bulletins)

    def test_slovakia_2023_11_28(self):
        processor = avacore.processor_caamlv6.Processor2022()
        bulletins = processor.parse_json_file("", self._json)
        self.assertEqualBulletinJSON(bulletins)

    def test_slovakia(self):
        processor = avacore.processor_sk.Processor()
        bulletins = processor.parse_json_file("", self._json)
        self.assertEqualBulletinJSON(bulletins)

    def test_slovenia_2023(self):
        processor = avacore.processor_caamlv5.SloveniaProcessor()
        processor.today = datetime.date(2023, 1, 9)
        bulletins = processor.parse_xml_file("SI", self._xml)
        self.assertEqualBulletinJSON(bulletins, "SI")

    def test_slovenia(self):
        processor = avacore.processor_caamlv5.SloveniaProcessor()
        processor.today = datetime.date(2021, 3, 20)
        bulletins = processor.parse_xml_file("SI", self._xml)
        self.assertEqualBulletinJSON(bulletins, "SI")

    def test_sweden_2022_12(self):
        processor = avacore.processor_se.Processor()
        bulletins = processor.parse_json_file("", self._json)
        self.assertEqual([], bulletins.bulletins)

    def test_sweden(self):
        processor = avacore.processor_se.Processor()
        bulletins = processor.parse_json_file("", self._json)
        self.assertEqualBulletinJSON(bulletins, "SE")

    def test_vorarlberg_2021_12(self):
        processor = avacore.processor_caamlv5.Processor()
        bulletins = processor.parse_xml_file("", self._xml)
        self.assertEqual(bulletins.main_date().isoformat(), "2021-12-29")
        self.assertEqualBulletinJSON(bulletins)

    def test_vorarlberg_2022_01(self):
        processor = avacore.processor_caamlv5.Processor()
        bulletins = processor.parse_xml_file("", self._xml)
        self.assertEqual(bulletins.main_date().isoformat(), "2022-01-31")
        self.assertEqualBulletinJSON(bulletins)

    @unittest.skip("wxSynopsisComment")
    def test_vorarlberg_ampm(self):
        processor = avacore.processor_caamlv5.VorarlbergProcessor()
        bulletins = processor.parse_xml_file("", self._xml)
        self.assertEqualBulletinJSON(bulletins)

    @unittest.skip("wxSynopsisComment")
    def test_vorarlberg(self):
        processor = avacore.processor_caamlv5.VorarlbergProcessor()
        bulletins = processor.parse_xml_file("", self._xml)
        self.assertEqualBulletinJSON(bulletins)
