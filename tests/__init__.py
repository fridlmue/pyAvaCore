import json
import os
import pathlib
import unittest
from jsonschema import validate
from avacore.pyAvaCore import get_report_provider

from avacore.avabulletins import Bulletins

ROOT = pathlib.Path(__file__).parent


class SnowTest(unittest.TestCase):
    def assertEqualBulletinJSON(
        self,
        bulletins: Bulletins,
        region_id: str = "",
        date: str = "",
        overwrite: bool = False,
    ):
        if overwrite and os.getenv("CI_JOB_NAME"):
            # https://docs.gitlab.com/ee/ci/variables/#list-all-environment-variables
            raise ValueError("overwrite=True must not be used in CI!")

        region_id = region_id or bulletins[0].get_region_list()[0].upper()
        provider = get_report_provider(region_id, date=date, lang="en")
        bulletins.append_provider(provider.name, provider.website)

        expected = self._fixture("caaml.json")
        if overwrite:
            expected.write_text(bulletins.to_json())
        self.assertEqual(
            expected.read_text(encoding="utf-8"),
            bulletins.to_json(),
        )

        maxDangerRatings = {
            "maxDangerRatings": bulletins.max_danger_ratings(bulletins.main_date()),
        }
        ratings = json.dumps(maxDangerRatings, indent=2, sort_keys=True)
        expected = self._fixture("ratings.json")
        if overwrite:
            expected.write_text(ratings)
        self.assertEqual(
            expected.read_text(encoding="utf-8"),
            ratings,
        )

        schema = (ROOT / "CAAMLv6_BulletinEAWS.json").read_text()
        validate(
            instance=json.loads(bulletins.to_json()),
            schema=json.loads(schema),
        )

    def _fixture(self, ext=""):
        return ROOT / "fixtures" / f"{self._testMethodName}.{ext}"

    @property
    def _json(self):
        return self._fixture("json")

    @property
    def _xml(self):
        return self._fixture("xml")
