import datetime
import io
from tests import SnowTest
import avacore.processor
import avacore.processor_ad
import avacore.processor_caamlv5
import avacore.processor_caamlv6
import avacore.processor_catalunya
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
import avacore.processor_ro
import avacore.processor_se
import avacore.processor_ua
import avacore.processor_uk


class TestAll(SnowTest):
    def test_ad(self):
        processor = avacore.processor_ad.Processor()
        self._test_processor(processor, "AD")

    def test_ad_2022_12(self):
        processor = avacore.processor_ad.Processor()
        self._test_processor(processor, "AD")

    def test_albina_2023_03_14(self):
        processor = avacore.processor_caamlv6.Processor2022()
        self._test_processor(processor, "AT-07")

    def test_aineva(self):
        processor = avacore.processor_caamlv5.Processor()
        self._test_processor(processor, "IT-21")

    def test_albina_2023_11_27(self):
        processor = avacore.processor_caamlv6.Processor()
        self._test_processor(processor, "IT-21")

    def test_albina_ampm(self):
        processor = avacore.processor_caamlv5.Processor()
        bulletins = self._test_processor(processor, "IT-32-TN")
        self.assertEqual(bulletins.main_date().isoformat(), "2021-02-22")

    def test_albina_elevation_band(self):
        processor = avacore.processor_caamlv5.Processor()
        self._test_processor(processor, "AT-07")

    def test_albina_ratings(self):
        processor = avacore.processor_caamlv5.Processor()
        bulletins = self._test_processor(processor, "IT-32-BZ")
        self.assertEqual(bulletins.main_date().isoformat(), "2022-03-22")

    def test_albina(self):
        processor = avacore.processor_caamlv5.Processor()
        bulletins = self._test_processor(processor, "AT-07")
        self.assertEqual(bulletins.main_date().isoformat(), "2021-02-10")

    def test_ch_2023_11_27(self):
        processor = avacore.processor_caamlv6.Processor()
        self._test_processor(processor, "CH")

    def test_ch_2023_12_19(self):
        processor = avacore.processor_caamlv6.Processor()
        self._test_processor(processor, "CH")

    def test_ct_icgc(self):
        processor = avacore.processor_catalunya.Processor()
        self._test_processor(processor, "ES-CT-L")

    def test_cz(self):
        processor = avacore.processor_cz.Processor()
        self._test_processor(processor, "CZ")

    def test_es_am_pm(self):
        processor = avacore.processor_es.Processor()
        self._test_processor(processor, "ES")

    def test_es(self):
        processor = avacore.processor_es.Processor()
        self._test_processor(processor, "ES")

    def test_fi(self):
        processor = avacore.processor_fi.Processor()
        processor.raw_data = io.BytesIO(self._fixture("png").read_bytes())
        processor.today = datetime.datetime.fromisoformat("2023-02-03T14:08:00")
        self._test_processor(processor, "FI")

    def test_france(self):
        processor = avacore.processor_fr.Processor()
        self._test_processor(processor, "FR")

    def test_gbsct(self):
        processor = avacore.processor_uk.Processor()
        self._test_processor(processor, "GB")

    def test_iceland(self):
        processor = avacore.processor_is.Processor()
        self._test_processor(processor, "IS")

    def test_it_livigno(self):
        processor = avacore.processor_it_livigno.Processor()
        bulletins = self._test_processor(processor, "IT-Livigno")
        self.assertEqual("2022-12-18", bulletins.main_date().isoformat())

    def test_it_livigno_2024(self):
        processor = avacore.processor_it_livigno.Processor()
        bulletins = self._test_processor(processor, "IT-Livigno")
        self.assertEqual("2024-12-01", bulletins.main_date().isoformat())

    def test_it_meteomont(self):
        processor = avacore.processor_it_meteomont.Processor()
        processor.add_eaws_id = True
        bulletins = self._test_processor(processor, "IT-MeteoMont")
        self.assertEqual("2022-12-12", bulletins.main_date().isoformat())
        self.assertEqual(
            ["2022-12-12", "2022-12-13", "2022-12-14", "2022-12-15"],
            sorted([d.isoformat() for d in bulletins.main_dates()]),
        )

    def test_norway(self):
        processor = avacore.processor_norway.Processor()
        processor.fetch_time_dependant = False
        self._test_processor(processor, "NO-3016")

    def test_pl_12_2022_12_01(self):
        processor = avacore.processor_pl_12.Processor()
        processor.fetch_time_dependant = False
        self._test_processor(processor, "PL-12")

    def test_pl_2018_02_09(self):
        processor = avacore.processor_pl.Processor()
        processor.fetch_time_dependant = False
        self._test_processor(processor, "PL-01")

    def test_pl_2019_01_09(self):
        processor = avacore.processor_pl.Processor()
        processor.fetch_time_dependant = False
        self._test_processor(processor, "PL-01")

    def test_slovakia_2023_11_28(self):
        processor = avacore.processor_caamlv6.Processor2022()
        self._test_processor(processor, "SK")

    def test_slovenia(self):
        processor = avacore.processor_caamlv6.Processor()
        self._test_processor(processor, "SI")

    def test_sweden_2022_12(self):
        processor = avacore.processor_se.Processor()
        with self.assertRaises(Exception) as context:
            self._test_processor(processor, "SE")
        self.assertRegex(str(context.exception), "'bulletins' is a required property")

    def test_sweden(self):
        processor = avacore.processor_se.Processor()
        self._test_processor(processor, "SE")

    def test_ua_2024_01_17(self):
        processor = avacore.processor_ua.Processor()
        self._test_processor(processor, "UA")

    def test_ua_2024_01_24(self):
        processor = avacore.processor_ua.Processor()
        self._test_processor(processor, "UA")

    def test_ro_2025_03_14(self):
        processor = avacore.processor_ro.Processor()
        self._test_processor(processor, "RO")

    def test_ro_2025_12_08(self):
        processor = avacore.processor_ro.Processor()
        self._test_processor(processor, "RO")
