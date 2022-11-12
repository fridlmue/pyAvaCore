import json
from avacore.processor_norway import Processor

from tests import SnowTest


class TestNorway(SnowTest):
    def test_norway(self):
        with open(f"{__file__}.json") as fp:
            data = json.load(fp)
        varsom_report = data
        processor = Processor()
        bulletins = processor.parse_json_no("NO-3016", varsom_report, fetch_time_dependant=False)
        self.assertEqualBulletinJSON(__file__, bulletins)
