import json
import jsonschema
import unittest
import pytest
from jsonschema import validate

from avacore import pyAvaCore
from avacore.avajson import JSONEncoder, remove_empty_elements
from avacore.avabulletin import AvaBulletin
from avacore.avabulletins import Bulletins


class TestJsonSchema(unittest.TestCase):
    @pytest.mark.skip(
        reason="Test is designed for a local execution to ensure general compatibility agains JSON schema once."
    )
    def test_json_schema(self):

        with open(f"{__file__}.schema.json", "r") as f:
            json_schema = json.load(f)

        regions = "AT-02 AT-03 AT-04 AT-05 AT-06 AT-07 AT-08 DE-BY CH SI FR IT-21 IT-23 IT-25 IT-34 IT-36 IT-57 NO ES-CT-L GB IS ES-CT CZ ES SK".split(
            " "
        )

        for idx, regionID in enumerate(regions):
            try:
                reports, _, url = pyAvaCore.get_reports(regionID)
                bulletins = Bulletins()
                bulletins.bulletins = reports

                bulletins_generic = json.loads(
                    json.dumps(bulletins, cls=JSONEncoder, indent=2)
                )  # ToDo find better way. Probably with JSONEncoder directly
                bulletins_generic = remove_empty_elements(bulletins_generic)

                print(str(idx) + ": Test for:", regionID)

                validate(instance=bulletins_generic, schema=json_schema)

                bulletins_from_json = Bulletins()
                bulletins_from_json.from_json(bulletins_generic)
                bulletins_generic_compare = json.loads(
                    json.dumps(bulletins, cls=JSONEncoder, indent=2)
                )  # ToDo find better way. Probably with JSONEncoder directly
                bulletins_generic_compare = remove_empty_elements(
                    bulletins_generic_compare
                )

                self.assertEqual(bulletins_generic, bulletins_generic_compare)
            except:
                print("No more report issued for", regionID, "?")


if __name__ == "__main__":
    unittest.main()
