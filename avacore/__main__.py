"""
    Copyright (C) 2022 Friedrich Mütschele and other contributors
    This file is part of pyAvaCore.
    pyAvaCore is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    pyAvaCore is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with pyAvaCore. If not, see <http://www.gnu.org/licenses/>.
"""
# pylint: disable=too-many-locals

from pathlib import Path
import sys
from urllib.request import urlopen
import argparse
import json
import logging
import logging.handlers
from datetime import datetime

from .pyAvaCore import get_reports
from .avabulletins import Bulletins
from .avajson import JSONEncoder
from .geojson import FeatureCollection

parser = argparse.ArgumentParser(
    description="Download and parse EAWS avalanche bulletins"
)
parser.add_argument(
    "--regions",
    default="AT-02 AT-03 AT-04 AT-05 AT-06 AT-07 AT-08 DE-BY CH SI FR IT-21 IT-23 IT-25 IT-34 IT-36 IT-57"
    + " NO ES-CT-L GB IS ES-CT CZ ES AD SK",
    help="avalanche region to download",
)
parser.add_argument("--output", default="./data", help="output directory")
parser.add_argument("--cache", default="./cache", help="cache directory")
parser.add_argument(
    "--geojson",
    help="eaws-regions directory containing *micro-regions_elevation.geojson.json of",
)
parser.add_argument(
    "--cli",
    default="n",
    help="print output to cli? [y]es, [n]o or [o]nly to cli ([o] will not write files)",
)
args = parser.parse_args()

Path("logs").mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    format="[%(asctime)s] {%(module)s:%(lineno)d} %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.handlers.TimedRotatingFileHandler(
            filename="logs/pyAvaCore.log", when="midnight"
        ),
        logging.StreamHandler(),
    ],
)


def log_events(event, event_args):
    """Logs relevant events."""
    if event == "urllib.Request":
        logging.info("Fetching %s", event_args)
    elif event == 'open' and 'w' in event_args[1]:
        logging.info("Writing file %s", event_args[0])


sys.addaudithook(log_events)


def download_region(regionID):
    """
    Downloads the given region and converts it to JSON
    """
    reports, _, url = get_reports(regionID)
    bulletins = Bulletins()
    bulletins.bulletins = reports
    validity_dates = bulletins.main_dates(protect_overwrite_now=datetime.now())
    validity_date = None

    if args.cli != "o":
        directory = Path(args.output)
        directory.mkdir(parents=True, exist_ok=True)
        ext = "zip" if url[-3:] == "zip" else "xml"

        for validity_date in validity_dates:
            if url != "":
                with urlopen(url) as http, open(
                    f"{directory}/{validity_date}-{regionID}.{ext}", mode="wb"
                ) as f:
                    f.write(http.read())
            with open(
                f"{directory}/{validity_date}-{regionID}.json",
                mode="w",
                encoding="utf-8",
            ) as f:
                json.dump(bulletins, fp=f, cls=JSONEncoder, indent=2)
            with open(
                f"{directory}/{validity_date}-{regionID}.ratings.json",
                mode="w",
                encoding="utf-8",
            ) as f:
                ratings = bulletins.max_danger_ratings(validity_date)
                relevant_ratings = {}
                for key, value in ratings.items():
                    if key.startswith(regionID):
                        relevant_ratings[key] = value
                maxDangerRatings = {"maxDangerRatings": relevant_ratings}
                json.dump(maxDangerRatings, fp=f, indent=2, sort_keys=True)
        if args.cli in ("o", "y"):
            for bulletin in bulletins.bulletins:
                bulletin.cli_out()
        if args.geojson:
            with open(
                f"{args.geojson}/{regionID}_micro-regions_elevation.geojson.json",
                encoding="utf-8",
            ) as f:
                geojson = FeatureCollection.from_dict(json.load(f))
            bulletins.augment_geojson(geojson)
            with open(
                f"{directory}/{validity_date}-{regionID}.geojson",
                mode="w",
                encoding="utf-8",
            ) as f:
                # Rounding of feature.geometry.coordinates is performed in to_float_coordinate
                json.dump(geojson.to_dict(), fp=f)


if __name__ == "__main__":
    for region in args.regions.split():
        try:
            download_region(region)
        except Exception as e:  # pylint: disable=broad-except
            logging.error("Failed to download %s", region, exc_info=e)
