from pathlib import Path
import unittest

from avacore.avabulletins import Bulletins


class SnowTest(unittest.TestCase):
    def assertEqualBulletinJSON(self, expected_basename: str, bulletins: Bulletins):
        expected = Path(f"{expected_basename}.caaml.json")
        # expected.write_text(bulletins.to_json())
        self.assertEqual(
            expected.read_text(encoding="utf-8"),
            bulletins.to_json(),
        )
