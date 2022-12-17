from avacore.processor_it_livigno import Processor

from pathlib import Path
from tests import SnowTest


class TestLivigno(SnowTest):
    def test_it_livigno(self):
        processor = Processor()
        html = Path(f"{__file__}.html").read_text("utf-8")
        bulletins = processor.parse_html("IT-Livigno", html)
        self.assertEqual('2022-12-18', bulletins.main_date().isoformat())
        self.assertEqualBulletinJSON(__file__, bulletins)
