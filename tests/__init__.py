from pathlib import Path
import unittest


class SnowTest(unittest.TestCase):
    def assertEqualJSON(self, expected_basename: str, json: str):
        expected = Path(f"{expected_basename}.caaml.json")
        self.assertEqual(expected.read_text(encoding="utf-8"), json)
