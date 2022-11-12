import json
from avacore.processor_catalunya import get_reports_fromjson

from tests import SnowTest


class TestCtIcgc(SnowTest):
    def test_ct_icgc(self):
        with open(f"{__file__}.json") as fp:
            icgc_report = json.load(fp)
        bulletins = get_reports_fromjson(icgc_report)
        self.assertEqualBulletinJSON(__file__, bulletins)
