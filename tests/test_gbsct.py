import json
from avacore.processor_uk import get_reports_from_json

from tests import SnowTest


class TestGbSct(SnowTest):
    def test_gbsct(self):
        with open(f"{__file__}.json") as fp:
            sais_report = json.load(fp)
        bulletins = get_reports_from_json(sais_report)
        self.assertEqualBulletinJSON(__file__, bulletins)
