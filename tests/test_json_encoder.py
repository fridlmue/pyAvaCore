from datetime import datetime
import json
import unittest
from avacore.avajson import JSONEncoder
from avacore.avabulletin import AvaBulletin, ValidTime


class TestJsonEncoder(unittest.TestCase):
    def test_json_encoder(self):
        bulletin = AvaBulletin()
        bulletin.validTime = ValidTime(datetime(2022, 3, 4))
        self.assertEqual(
            json.dumps(bulletin, cls=JSONEncoder),
            '{"validTime": {"startTime": "2022-03-04T00:00:00"}}',
        )


if __name__ == "__main__":
    unittest.main()
