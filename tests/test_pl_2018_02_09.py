from pathlib import Path
from avacore.processor_pl import Processor

from tests import SnowTest


class TestPl(SnowTest):
    def test_pl_2018_02_09(self):
        processor = Processor()
        processor.fetch_time_dependant = False
        html = Path(f"{__file__}.html").read_text("utf-8")
        bulletins = processor.parse_html("PL-01", html)
        self.assertEqualBulletinJSON(__file__, bulletins)
