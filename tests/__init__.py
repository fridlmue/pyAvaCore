import json
from pathlib import Path
import unittest
from jsonschema import validate
from avacore.pyAvaCore import get_report_provider

from avacore.avabulletins import Bulletins


class SnowTest(unittest.TestCase):
    def assertEqualBulletinJSON(
        self,
        expected_basename: str,
        bulletins: Bulletins,
        region_id: str = "",
        date: str = "",
    ):

        region_id = region_id or bulletins[0].get_region_list()[0].upper()
        provider = get_report_provider(region_id, date=date, lang="en")
        bulletins.append_provider(provider.name, provider.website)

        expected = Path(f"{expected_basename}.caaml.json")
        # expected.write_text(bulletins.to_json())
        self.assertEqual(
            expected.read_text(encoding="utf-8"),
            bulletins.to_json(),
        )

        maxDangerRatings = {
            "maxDangerRatings": bulletins.max_danger_ratings(bulletins.main_date()),
        }
        ratings = json.dumps(maxDangerRatings, indent=2, sort_keys=True)
        expected = Path(f"{expected_basename}.ratings.json")
        # expected.write_text(ratings)
        self.assertEqual(
            expected.read_text(encoding="utf-8"),
            ratings,
        )

        schema = Path(__file__).with_name("test_json_schema.py.schema.json").read_text()
        validate(
            instance=json.loads(bulletins.to_json()),
            schema=json.loads(schema),
        )
