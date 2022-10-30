import json
from pathlib import Path
from avacore.avabulletins import Bulletins

from tests import SnowTest


class TestJson(SnowTest):
    def test_all(self):
        for path in Path(__file__).parent.glob("*.caaml.json"):
            bulletins = Bulletins()
            foobar = path.read_text()
            bulletins.from_json(json.loads(foobar))
            # xx.write_text(bulletins.to_json())
            self.assertEqual(bulletins.to_json(), foobar)
