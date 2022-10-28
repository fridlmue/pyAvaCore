from avacore.processor_is import parse_reports_is
import unittest
import xml.etree.ElementTree as ET


class TestIceland(unittest.TestCase):
    def test_iceland(self):
        root = ET.ElementTree()
        root.parse(f"{__file__}.xml")
        reports = parse_reports_is(root).bulletins
        self.assertEqual(len(reports), 4)
        report = reports[0]
        self.assertEqual(report.bulletinID, "IS-SV-2022-02-21T16:40:51+00:00")
        self.assertEqual(
            report.publicationTime.isoformat(), "2022-02-21T16:40:51+00:00"
        )
        self.assertEqual(
            report.validTime.startTime.isoformat(), "2022-02-21T19:00:00+00:00"
        )
        self.assertEqual(
            report.validTime.endTime.isoformat(), "2022-02-22T19:00:00+00:00"
        )
        self.assertIn("IS-SV", report.get_region_list())
        self.assertNotIn("BYAMM", report.get_region_list())
        self.assertEqual(report.dangerRatings[0].mainValue, "high")
        self.assertEqual(report.avalancheProblems[0].problemType, "wind_drifted_snow")
        self.assertEqual(
            report.avalancheProblems[1].problemType, "persistent_weak_layers"
        )
        self.assertEqual(len(report.avalancheProblems), 2)
        self.assertIn("N", report.avalancheProblems[0].aspects)
        self.assertIn("W", report.avalancheProblems[0].aspects)
        self.assertRaises(AttributeError, getattr, report, "predecessor_id")


if __name__ == "__main__":
    unittest.main()
