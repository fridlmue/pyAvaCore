from avacore.processor_es import get_reports_from_file

from tests import SnowTest


class TestES(SnowTest):
    def test_ES(self):
        with open(f"{__file__}.xml", encoding="ISO-8859-1") as f:
            text = f.read()
        bulletins = get_reports_from_file(text)
        self.assertEqualBulletinJSON(__file__, bulletins)
