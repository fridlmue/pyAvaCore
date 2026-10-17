#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Poll an FTP server for Sommer GPRS CSV files and append their data to SMET files.

Every --interval seconds:
1. list *.csv files in --ftp-dir on the FTP server
2. download each new file to --incoming-dir
3. copy it to --archive-dir
4. delete it from the FTP server
5. parse it (format "gprssommer", see https://prozessing.tbbm.at/format/gprssommer.html)
6. map logger channels to SMET fields using --metadata
7. convert values to SI units
8. append records to the corresponding SMET file in --smet-dir
9. remove it from --incoming-dir

Files left in --incoming-dir (e.g. after a crash) are processed again on the next run.

The local SMET files in --smet-dir are uncompressed copies of files such as
https://wiski.tirol.gv.at/lawine/grafiken/smet/woche/GGAL2.smet.gz
The mapping from Sommer GPRS channels to SMET fields is given by a metadata file
(exists, but not reachable yet, see load_metadata).

Usage:
    FTP_PASSWORD=... uv run scripts/gprssommer2smet.py --ftp-host ... --ftp-user ... --ftp-dir ...
"""

import argparse
import dataclasses
import datetime
import ftplib
import json
import logging
import os
import pathlib
import shutil
import time
from collections.abc import Callable, Iterator

log = logging.getLogger("gprssommer2smet")

# TODO: timezone of the logger timestamps is unknown; Sommer loggers are commonly set to
#  CET (UTC+1, no daylight saving time). Confirm with the station operator.
SOURCE_TZ = datetime.timezone(datetime.timedelta(hours=1))

# Unit conversions from Sommer GPRS units (CU: line) to SI units as used in SMET files.
# TODO: replace with the final list of (max. 7) unit conversions
UNIT_CONVERSIONS: dict[str, Callable[[float], float]] = {
    "°C": lambda v: v + 273.15,  # temperature -> K
    "km/h": lambda v: v / 3.6,  # wind speed -> m/s
    "% rF": lambda v: v / 100,  # relative humidity -> 1
    "%rF": lambda v: v / 100,  # relative humidity -> 1
    "cm": lambda v: v / 100,  # snow height -> m
    "mm": lambda v: v / 1000,  # TODO: precipitation in SMET is kg/m² (= mm), snow height in m?
    "hPa": lambda v: v * 100,  # air pressure -> Pa
}
# units that are already SI (as used in SMET), no conversion needed
# TODO: confirm, e.g. mmWS (snow pillow) = kg/m² SWE, Grad = ° wind direction
IDENTITY_UNITS = {"m", "m/s", "W/m2", "W/m²", "Grad", "°", "mmWS", "V"}


@dataclasses.dataclass
class Block:
    """One data block of a Sommer GPRS CSV file (starting with DS:)."""

    logger_id: str
    channels: list[str]  # CP: channel numbers
    labels: list[str]  # CL: channel labels
    units: list[str]  # CU: channel units
    records: list[tuple[datetime.datetime, list[float | None]]]


def parse_gprssommer(path: pathlib.Path) -> list[Block]:
    """
    Parse a Sommer GPRS CSV file, e.g.

        DS:;29600456
        CP:;1;2;3
        CL:;Lufttemperatur_1610m;Luftfeuchte_1610m;Schneekissen_1610m
        CU:;°C;% rF;mmWS
        2011-09-19 07:30:00;-0.1;97.1;-1
        #Si 6C136F23
    """
    # TODO: encoding unknown; example on prozessing.tbbm.at shows mojibake ("OberflÃ¤che")
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="latin-1")

    # TODO: the "SOMMER FX" variant (SID;/DEV;/CP;/CL;/CU;/D; lines, decimal comma) is not supported
    if text.lstrip().startswith("SOMMER FX"):
        raise NotImplementedError(f"{path}: SOMMER FX variant not supported")

    blocks: list[Block] = []
    block: Block | None = None
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            # "#Si ..." checksum and other comment lines
            # TODO: verify "#Si" checksum?
            continue
        key, _, rest = line.partition(";")
        values = [v.strip().strip('"') for v in rest.split(";")]
        if key == "DS:":
            block = Block(logger_id=values[0], channels=[], labels=[], units=[], records=[])
            blocks.append(block)
        elif block is None:
            log.warning("%s: ignoring line before DS: %r", path, line)
        elif key == "CP:":
            block.channels = values
        elif key == "CL:":
            block.labels = values
        elif key == "CU:":
            block.units = values
        else:
            timestamp = datetime.datetime.fromisoformat(key).replace(tzinfo=SOURCE_TZ)
            # empty values occur, e.g. for high-resolution precipitation in a non-equidistant grid
            record = [float(v) if v else None for v in values]
            block.records.append((timestamp, record))
    return blocks


@dataclasses.dataclass
class StationMapping:
    smet_station: str  # SMET file name w/o extension, e.g. GGAL2
    fields: dict[str, str]  # Sommer channel (CP:) -> SMET field, e.g. {"1": "TA"}


def load_metadata(path: pathlib.Path) -> dict[str, StationMapping]:
    """
    Load the mapping from Sommer GPRS logger/channels to SMET station/fields.

    TODO: the metadata file exists but is not reachable yet; format is unknown.
    Assumed JSON format:

        {
          "29600456": {
            "smet": "GGAL2",
            "fields": {"1": "TA", "2": "RH", "3": "SWE", "4": "TSS", "5": "ISWR"}
          }
        }

    TODO: map by channel number (CP:) or by label (CL:)?
    TODO: key by logger id (DS:) or by file name?
    """
    data = json.loads(path.read_text(encoding="utf-8"))
    return {
        logger_id: StationMapping(smet_station=m["smet"], fields=m["fields"])
        for logger_id, m in data.items()
    }


def to_si(value: float | None, unit: str) -> float | None:
    if value is None:
        return None
    if unit in UNIT_CONVERSIONS:
        return UNIT_CONVERSIONS[unit](value)
    if unit not in IDENTITY_UNITS:
        # TODO: fail hard on unknown units instead?
        log.warning("Unknown unit %r, keeping value as is", unit)
    return value


@dataclasses.dataclass
class SmetHeader:
    fields: list[str]
    nodata: str
    last_timestamp: datetime.datetime | None


def read_smet_header(path: pathlib.Path) -> SmetHeader:
    fields: list[str] = []
    nodata = "-999"
    last_line = ""
    in_data = False
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line == "[DATA]":
                in_data = True
            elif in_data:
                last_line = line
            elif "=" in line and not line.startswith("#"):
                key, _, value = (s.strip() for s in line.partition("="))
                if key == "fields":
                    fields = value.split()
                elif key == "nodata":
                    nodata = value
    if not fields or fields[0] != "timestamp":
        raise ValueError(f"{path}: unsupported SMET fields {fields}")
    last_timestamp = None
    if last_line:
        last_timestamp = datetime.datetime.fromisoformat(last_line.split()[0])
    return SmetHeader(fields=fields, nodata=nodata, last_timestamp=last_timestamp)


def format_value(value: float | None, nodata: str) -> str:
    return nodata if value is None else f"{value:.10g}"


def append_to_smet(block: Block, mapping: StationMapping, smet_dir: pathlib.Path) -> int:
    # TODO: SMET file naming, e.g. GGAL2.smet; create the file if missing?
    smet_file = smet_dir / f"{mapping.smet_station}.smet"
    header = read_smet_header(smet_file)

    # column index in block -> SMET field
    columns: dict[int, str] = {}
    for i, channel in enumerate(block.channels):
        field = mapping.fields.get(channel)
        if field is None:
            log.debug("Logger %s channel %s (%s) not mapped", block.logger_id, channel, block.labels[i])
        elif field not in header.fields:
            # TODO: add new fields to the SMET header instead?
            log.warning("%s: field %s not present in SMET header", smet_file, field)
        else:
            columns[i] = field

    lines = []
    for timestamp, record in block.records:
        # skip records already contained in the SMET file
        # TODO: records are assumed to be sorted; what about out-of-order or overlapping files?
        if header.last_timestamp and timestamp <= header.last_timestamp:
            continue
        values: dict[str, float | None] = {
            field: to_si(record[i], block.units[i]) for i, field in columns.items() if i < len(record)
        }
        if all(v is None for v in values.values()):
            # TODO: skip partial records (e.g. high-res precipitation only) or merge into 10 min grid?
            continue
        utc = timestamp.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        row = [utc] + [format_value(values.get(f), header.nodata) for f in header.fields[1:]]
        lines.append(" ".join(row) + "\n")

    # TODO: derived fields such as TD (dew point) are not computed and are written as nodata
    # TODO: locking/concurrency with other processes writing to the SMET file; update "creation" header?
    if lines:
        with smet_file.open("a", encoding="utf-8") as f:
            f.writelines(lines)
    return len(lines)


def process_file(path: pathlib.Path, metadata: dict[str, StationMapping], smet_dir: pathlib.Path) -> None:
    for block in parse_gprssommer(path):
        mapping = metadata.get(block.logger_id)
        if mapping is None:
            # TODO: unknown logger: error or ignore?
            log.warning("%s: no metadata for logger %s", path, block.logger_id)
            continue
        n = append_to_smet(block, mapping, smet_dir)
        log.info("%s: appended %d records of logger %s to %s", path.name, n, block.logger_id, mapping.smet_station)


def fetch_new_files(args: argparse.Namespace) -> Iterator[pathlib.Path]:
    """Download new CSV files, archive them, and delete them from the FTP server."""
    # TODO: plain FTP or FTPS (ftplib.FTP_TLS) or SFTP?
    with ftplib.FTP(args.ftp_host, timeout=30) as ftp:
        ftp.login(args.ftp_user, args.ftp_password)
        ftp.cwd(args.ftp_dir)
        # TODO: file name pattern? case-insensitive *.csv for now
        names = sorted(n for n in ftp.nlst() if n.lower().endswith(".csv"))
        for name in names:
            # TODO: avoid downloading files still being uploaded (check size/mtime stable?)
            target = args.incoming_dir / name
            partial = target.with_suffix(target.suffix + ".part")
            with partial.open("wb") as f:
                ftp.retrbinary(f"RETR {name}", f.write)
            partial.rename(target)
            # TODO: archive directory layout, e.g. per year/month? name clashes?
            shutil.copy2(target, args.archive_dir / name)
            ftp.delete(name)
            log.info("Downloaded and archived %s", name)
            yield target


def run_once(args: argparse.Namespace) -> None:
    for _ in fetch_new_files(args):
        pass
    # also picks up files left over from previous (failed) runs
    metadata = load_metadata(args.metadata)
    for path in sorted(args.incoming_dir.glob("*.csv")):
        try:
            process_file(path, metadata, args.smet_dir)
            path.unlink()
        except Exception:
            # TODO: move to an error directory to avoid retrying forever?
            log.exception("Failed to process %s", path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--ftp-host", required=True)
    parser.add_argument("--ftp-user", default="anonymous")
    parser.add_argument("--ftp-password", default=os.environ.get("FTP_PASSWORD", ""), help="default: $FTP_PASSWORD")
    parser.add_argument("--ftp-dir", default="/")
    parser.add_argument("--incoming-dir", type=pathlib.Path, default=pathlib.Path("incoming"))
    parser.add_argument("--archive-dir", type=pathlib.Path, default=pathlib.Path("archive"))
    parser.add_argument("--smet-dir", type=pathlib.Path, default=pathlib.Path("smet"))
    parser.add_argument("--metadata", type=pathlib.Path, default=pathlib.Path("metadata.json"))
    parser.add_argument("--interval", type=float, default=5, help="polling interval in seconds")
    parser.add_argument("--once", action="store_true", help="run once and exit")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    args.incoming_dir.mkdir(parents=True, exist_ok=True)
    args.archive_dir.mkdir(parents=True, exist_ok=True)

    while True:
        try:
            run_once(args)
        except Exception:
            log.exception("Polling failed")
        if args.once:
            break
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
