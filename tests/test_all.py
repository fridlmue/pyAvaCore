import datetime
import io
from tests import SnowTest
import avacore.processor_AD
import avacore.processor_caamlv5
import avacore.processor_caamlv6
import avacore.processor_ES_CT
import avacore.processor_CZ
import avacore.processor_ES
import avacore.processor_FI
import avacore.processor_FR
import avacore.processor_IS
import avacore.processor_IT_Livigno
import avacore.processor_IT_MeteoMont
import avacore.processor_NO
import avacore.processor_PL
import avacore.processor_PL_12
import avacore.processor_RO
import avacore.processor_SE
import avacore.processor_UA
import avacore.processor_GB


class TestAll(SnowTest):
    def test_AD(self):
        processor = avacore.processor_AD.Processor()
        self._test_processor(processor, "AD")

    def test_AD_2022_12(self):
        processor = avacore.processor_AD.Processor()
        self._test_processor(processor, "AD")

    def test_albina_2023_03_14(self):
        processor = avacore.processor_caamlv6.Processor2022()
        self._test_processor(processor, "AT-07")

    def test_IT_AINEVA(self):
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

    def test_CH_2023_11_27(self):
        processor = avacore.processor_caamlv6.Processor()
        self._test_processor(processor, "CH")

    def test_CH_2023_12_19(self):
        processor = avacore.processor_caamlv6.Processor()
        self._test_processor(processor, "CH")

    def test_ES_CT(self):
        processor = avacore.processor_ES_CT.Processor()
        self._test_processor(processor, "ES-CT-L")

    def test_ES_CT_2026_02_28(self):
        processor = avacore.processor_ES_CT.Processor()
        self._test_processor(processor, "ES-CT-L")

    def test_CZ(self):
        processor = avacore.processor_CZ.Processor()
        self._test_processor(processor, "CZ")

    def test_ES_am_pm(self):
        processor = avacore.processor_ES.Processor()
        self._test_processor(processor, "ES")

    def test_ES(self):
        processor = avacore.processor_ES.Processor()
        self._test_processor(processor, "ES")

    def test_FI(self):
        processor = avacore.processor_FI.Processor()
        processor.raw_data = io.BytesIO(self._fixture("png").read_bytes())
        processor.today = datetime.datetime.fromisoformat("2023-02-03T14:08:00")
        self._test_processor(processor, "FI")

    def test_FR(self):
        processor = avacore.processor_FR.Processor()
        self._test_processor(processor, "FR")

    def test_GB(self):
        processor = avacore.processor_GB.Processor()
        self._test_processor(processor, "GB")

    def test_IS(self):
        processor = avacore.processor_IS.Processor()
        self._test_processor(processor, "IS")

    def test_IT_Livigno(self):
        processor = avacore.processor_IT_Livigno.Processor()
        bulletins = self._test_processor(processor, "IT-25-SO-LI")
        self.assertEqual("2022-12-18", bulletins.main_date().isoformat())

    def test_IT_Livigno_2024(self):
        processor = avacore.processor_IT_Livigno.Processor()
        bulletins = self._test_processor(processor, "IT-25-SO-LI")
        self.assertEqual("2024-12-01", bulletins.main_date().isoformat())

    def test_IT_MeteoMont(self):
        processor = avacore.processor_IT_MeteoMont.Processor()
        processor.add_eaws_id = True
        bulletins = self._test_processor(processor, "IT-MeteoMont")
        self.assertEqual("2022-12-12", bulletins.main_date().isoformat())
        self.assertEqual(
            ["2022-12-12", "2022-12-13", "2022-12-14", "2022-12-15"],
            sorted([d.isoformat() for d in bulletins.main_dates()]),
        )

    def test_NO(self):
        processor = avacore.processor_NO.Processor()
        processor.fetch_time_dependant = False
        self._test_processor(processor, "NO-3016")

    def test_PL_12_2022_12_01(self):
        processor = avacore.processor_PL_12.Processor()
        processor.fetch_time_dependant = False
        self._test_processor(processor, "PL-12")

    def test_PL_2018_02_09(self):
        processor = avacore.processor_PL.Processor()
        processor.fetch_time_dependant = False
        self._test_processor(processor, "PL-01")

    def test_PL_2019_01_09(self):
        processor = avacore.processor_PL.Processor()
        processor.fetch_time_dependant = False
        self._test_processor(processor, "PL-01")

    def test_SK_2023_11_28(self):
        processor = avacore.processor_caamlv6.Processor2022()
        self._test_processor(processor, "SK")

    def test_SI(self):
        processor = avacore.processor_caamlv6.Processor()
        self._test_processor(processor, "SI")

    def test_SE_2022_12(self):
        processor = avacore.processor_SE.Processor()
        with self.assertRaises(Exception) as context:
            self._test_processor(processor, "SE")
        self.assertRegex(str(context.exception), "'bulletins' is a required property")

    def test_SE(self):
        processor = avacore.processor_SE.Processor()
        self._test_processor(processor, "SE")

    def test_UA_2024_01_17(self):
        processor = avacore.processor_UA.Processor()
        self._test_processor(processor, "UA")

    def test_UA_2024_01_24(self):
        processor = avacore.processor_UA.Processor()
        self._test_processor(processor, "UA")

    def test_RO_2025_03_14(self):
        processor = avacore.processor_RO.Processor()
        self._test_processor(processor, "RO")

    def test_RO_2025_12_08(self):
        processor = avacore.processor_RO.Processor()
        self._test_processor(processor, "RO")
