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

from dataclasses import dataclass
from pathlib import Path
import argparse
import json
import logging
import logging.handlers
import socket
import datetime as dt
from datetime import datetime, timedelta
from io import BytesIO
import urllib.error

from .pyAvaCore import get_bulletins, parse_dates
from .avajson import JSONEncoder
from .geojson import FeatureCollection

default_regions = [
    "AD",
    "AT-02",
    "AT-03",
    "AT-04",
    "AT-05",
    "AT-06",
    "AT-07",
    "AT-08",
    "CH",
    "CZ",
    "DE-BY",
    "ES-CT-L",
    "ES-CT",
    "ES",
    "FI",
    "FR",
    "GB",
    "IS",
    "IT-21",
    "IT-23",
    "IT-25",
    "IT-25-SO-LI",
    "IT-32-BZ",
    "IT-32-TN",
    "IT-34",
    "IT-36",
    "IT-57",
    "IT-MeteoMont",
    "NO",
    "PL",
    "PL-12",
    "RO",
    "SE",
    "SI",
    "SK",
    "UA",
]

parser = argparse.ArgumentParser(
    description="Download and parse EAWS avalanche bulletins"
)
parser.add_argument(
    "--lang",
    default="en",
    help="language to fetch avalanche bulletins for",
)
parser.add_argument(
    "--date",
    help="date to fetch avalanche bulletins for; "
    "date is specified in ISO 8601 format `YYYY-MM-DD`; "
    "multiple dates may be specified using a space separator; "
    "an ISO 8601 interval may be specified as `YYYY-MM-DD/YYYY-MM-DD`",
)
parser.add_argument(
    "--regions",
    default=" ".join(default_regions),
    help="avalanche regions to download",
)
parser.add_argument(
    "--merge-dates",
    default=" ".join(
        [(dt.date.today() + timedelta(days=days)).isoformat() for days in (-1, 0, +1)]
    ),
    metavar="DATES",
    help="dates to merge into one file",
)
parser.add_argument(
    "--merge-regions",
    default=" ".join(default_regions),
    metavar="REGIONS",
    help="avalanche regions to merge into one file",
)
parser.add_argument(
    "--protect-overwrite-now",
    metavar="TIMESTAMP",
    help="exclude bulletins prior the given timestamp",
)
parser.add_argument(
    "--output",
    default=Path("./data"),
    type=Path,
    help="output directory",
)
parser.add_argument(
    "--log",
    default=Path("./logs"),
    type=Path,
    help="output directory for logs",
)
parser.add_argument(
    "--geojson",
    type=Path,
    help="eaws-regions directory containing *micro-regions_elevation.geojson.json of",
)
parser.add_argument(
    "--cli",
    default="n",
    help="print output to cli? [y]es, [n]o or [o]nly to cli ([o] will not write files)",
)


@dataclass
class CliArgs:
    cli: str
    date: str
    geojson: str
    lang: str
    merge_dates: str
    merge_regions: str
    output: Path
    log: Path
    protect_overwrite_now: str
    regions: str


args = parser.parse_args(namespace=CliArgs)


def init_logging(filename="pyAvaCore.log"):
    """Initialize the logging system"""
    log_path = args.log / filename
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        format="[%(asctime)s] {%(module)s:%(lineno)d} %(levelname)s - %(message)s",
        level=logging.INFO,
        handlers=[
            logging.handlers.TimedRotatingFileHandler(
                filename=log_path, when="midnight"
            ),
            logging.StreamHandler(),
        ],
    )


def download_region(regionID, date: str):
    """
    Downloads the given region and converts it to JSON
    """
    bulletins = get_bulletins(regionID, date=date, lang=args.lang)

    protect_overwrite_now = datetime.fromisoformat(
        args.protect_overwrite_now
        or date
        or datetime.now().replace(microsecond=0).isoformat()
    )
    validity_dates = bulletins.main_dates(protect_overwrite_now)
    validity_date = None

    if args.cli == "o":
        return
    for validity_date in validity_dates:
        directory = args.output / validity_date.isoformat()
        directory.mkdir(parents=True, exist_ok=True)
        data = bulletins.customData.pop("data", "")
        ext = bulletins.customData.pop("file_extension", "")
        if data and ext:
            raw = directory / f"{validity_date}-{regionID}.raw.{ext}"
            logging.info("Writing %s", raw)
            if isinstance(data, BytesIO):
                raw.write_bytes(data.getvalue())
            else:
                raw.write_text(data, encoding="utf-8")
        with (directory / f"{validity_date}-{regionID}.json").open(
            mode="w",
            encoding="utf-8",
        ) as f:
            logging.info("Writing %s", f.name)
            json.dump(bulletins, fp=f, cls=JSONEncoder, indent=2)
        with (directory / f"{validity_date}-{regionID}.ratings.json").open(
            mode="w",
            encoding="utf-8",
        ) as f:
            ratings = bulletins.max_danger_ratings(validity_date, regionID)
            maxDangerRatings = {"maxDangerRatings": ratings}
            logging.info("Writing %s", f.name)
            json.dump(maxDangerRatings, fp=f, indent=2, sort_keys=True)
        with (directory / f"{validity_date}-{regionID}.problems.json").open(
            mode="w",
            encoding="utf-8",
        ) as f:
            problems = bulletins.all_avalanche_problems(validity_date, regionID)
            avalancheProblems = {"avalancheProblems": problems}
            logging.info("Writing %s", f.name)
            json.dump(avalancheProblems, fp=f, indent=2, sort_keys=True)
    if args.cli in ("o", "y"):
        for bulletin in bulletins.bulletins:
            bulletin.cli_out()
    if args.geojson:
        geojson_path = args.geojson / f"{regionID}_micro-regions_elevation.geojson.json"
        with geojson_path.open(encoding="utf-8") as f:
            geojson = FeatureCollection.from_dict(json.load(f))
        bulletins.augment_geojson(geojson)
        with (directory / f"{validity_date}-{regionID}.geojson").open(
            mode="w",
            encoding="utf-8",
        ) as f:
            # Rounding of feature.geometry.coordinates is performed in to_float_coordinate
            logging.info("Writing %s", f.name)
            json.dump(geojson.to_dict(), fp=f)


def download_regions():
    """Downloads all regions"""
    failed_regions = []
    for region in args.regions.split():
        for date in parse_dates(args.date):
            try:
                download_region(region, date)
            except urllib.error.HTTPError as e:
                failed_regions.append(region)
                logging.warning(
                    "Failed to download %s from %s: %s %s",
                    region,
                    e.filename,
                    e.status,
                    e.reason,
                )
            except Exception as e:
                failed_regions.append(region)
                logging.error("Failed to download %s", region, exc_info=e)
    if failed_regions:
        logging.error(
            "Failed to download the following regions: %s",
            " ".join(failed_regions),
        )


def merge_json_files(validity_date: str, suffix: str, json_key: str):
    """Create ratings JSON containing all regions"""
    directory = args.output / validity_date
    merge_keys = {}
    for regionID in args.merge_regions.split():
        try:
            path = directory / f"{validity_date}-{regionID}.{suffix}"
            if not path.exists():
                continue
            with path.open(encoding="utf-8") as f:
                logging.info("Reading %s", f.name)
                ratings = json.load(fp=f)
            if json_key in ratings:
                merge_keys.update(ratings[json_key])
        except Exception as e:
            logging.error("Failed to load %s from %s", regionID, path, exc_info=e)
    path = directory / f"{validity_date}.{suffix}"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open(mode="w", encoding="utf-8") as f:
        logging.info("Writing %s", f.name)
        json.dump({json_key: merge_keys}, fp=f, indent=2, sort_keys=True)


def main():
    socket.setdefaulttimeout(13)
    init_logging()
    download_regions()
    for date_string in parse_dates(args.date or args.merge_dates):
        merge_json_files(date_string, "ratings.json", "maxDangerRatings")
        merge_json_files(date_string, "problems.json", "avalancheProblems")


if __name__ == "__main__":
    main()
