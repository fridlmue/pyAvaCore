import json
from avacore.processor_norway import parse_json_no

from tests import SnowTest


class TestNorway(SnowTest):
    def test_norway(self):
        with open(f"{__file__}.json") as fp:
            data = json.load(fp)
        varsom_report = data
        bulletins = parse_json_no("NO-3016", varsom_report, fetch_time_dependant=False)
        self.assertEqualBulletinJSON(__file__, bulletins)
