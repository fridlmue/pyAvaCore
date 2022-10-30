from avacore.processor_es import get_reports_from_file

from tests import SnowTest

# Día 25 de marzo de 2022 a las 14:34 hora oficial
# Día 26 de marzo de 2022 a las 17:50 hora oficial
# Día 27 de marzo de 2022 a las 17:03 hora oficial
# Día 28 de marzo de 2022 a las 15:16 hora oficial
# Día 29 de marzo de 2022 a las 16:20 hora oficial
# Día 30 de marzo de 2022 a las 16:06 hora oficial
# Día 31 de marzo de 2022 a las 16:19 hora oficial
# Día 1 de abril de 2022 a las 15:20 hora oficial
# Día 3 de abril de 2022 a las 15:20 hora oficial
# Día 3 de abril de 2022 a las 15:20 hora oficial
# Día 4 de abril de 2022 a las 17:36 hora oficial
# Día 4 de abril de 2022 a las 17:36 hora oficial
# Día 6 de abril de 2022 a las 17:27 hora oficial
# Día 6 de abril de 2022 a las 17:27 hora oficial
# Día 8 de abril de 2022 a las 17:30 hora oficial
# Día 9 de abril de 2022 a las 20:01 hora oficial
# Día 10 de abril de 2022 a las 20:02 hora oficial
# Día 10 de abril de 2022 a las 20:02 hora oficial
# Día 12 de abril de 2022 a las 15:39 hora oficial
# Día 12 de abril de 2022 a las 15:39 hora oficial
# Día 13 de abril de 2022 a las 15:38 hora oficial
# Día 15 de abril de 2022 a las 15:33 hora oficial
# Día 15 de abril de 2022 a las 15:33 hora oficial
# Día 17 de abril de 2022 a las 16:35 hora oficial
# Día 18 de abril de 2022 a las 19:14 hora oficial
# Día 18 de abril de 2022 a las 19:14 hora oficial
# Día 20 de abril de 2022 a las 18:33 hora oficial
# Día 21 de abril de 2022 a las 18:43 hora oficial
# Día 21 de abril de 2022 a las 18:43 hora oficial
# Día 23 de abril de 2022 a las 14:11 hora oficial
# Día 24 de abril de 2022 a las 14:08 hora oficial
# Día 25 de abril de 2022 a las 15:40 hora oficial
# Día 25 de abril de 2022 a las 15:40 hora oficial
# Día 27 de abril de 2022 a las 15:12 hora oficial
# Día 27 de abril de 2022 a las 15:12 hora oficial
# Día 29 de abril de 2022 a las 15:36 hora oficial
# Día 30 de abril de 2022 a las 16:10 hora oficial
# Día 30 de abril de 2022 a las 16:10 hora oficial
# Día 2 de mayo de 2022 a las 15:12 hora oficial
# Día 3 de mayo de 2022 a las 14:36 hora oficial
# Día 3 de mayo de 2022 a las 14:36 hora oficial
# Día 5 de mayo de 2022 a las 16:11 hora oficial
# Día 6 de mayo de 2022 a las 15:46 hora oficial
# Día 6 de mayo de 2022 a las 15:46 hora oficial
# Día 7 de mayo de 2022 a las 16:08 hora oficial


class TestES(SnowTest):
    def test_ES(self):
        with open(f"{__file__}.xml", encoding="ISO-8859-1") as f:
            text = f.read()
        bulletins = get_reports_from_file(text)
        self.assertEqualBulletinJSON(__file__, bulletins)
