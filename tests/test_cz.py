import json
from avacore.processor_cz import get_reports_fromjson

from tests import SnowTest


class TestCZ(SnowTest):
    def test_cz(self):
        with open(f"{__file__}.json") as fp:
            data = json.load(fp)
        cz_report = data
        bulletins = get_reports_fromjson(cz_report)
        self.assertEqualBulletinJSON(__file__, bulletins)
