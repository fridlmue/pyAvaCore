"""
CLI for pyAvaCore
"""
from datetime import datetime
from datetime import timedelta
from pathlib import Path
from urllib.request import urlopen
import argparse
import json
import typing
import logging
import logging.handlers

from .pyAvaCore import JSONEncoder, get_reports
from .avabulletin import AvaBulletin

parser = argparse.ArgumentParser(description='Download and parse EAWS avalanche bulletins')
parser.add_argument('--regions',
                    default="AT-02 AT-03 AT-04 AT-05 AT-06 AT-07 AT-08 DE-BY CH SI FR IT-AINEVA",
                    help='avalanche region to download')
parser.add_argument('--output',
                    default='./data',
                    help='output directory')
parser.add_argument('--cache',
                    default='./cache',
                    help='cache directory')
args = parser.parse_args()

Path('logs').mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    format='[%(asctime)s] {%(module)s:%(lineno)d} %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.handlers.TimedRotatingFileHandler(filename='logs/pyAvaCore.log', when='midnight'),
        logging.StreamHandler()])

class Bulletins:
    '''
    Class for the AvaBulletin collection
    Follows partly CAAMLv6 caaml:Bulletins
    '''
    bulletins: typing.List[AvaBulletin]

def download_region(regionID):
    """Downloads the given region and converts it to JSON"""
    reports, _, url = get_reports(regionID)
    report: AvaBulletin
    for report in reports:
        if isinstance(report.validTime.startTime, datetime):
            validityDate = report.validTime.startTime
            if validityDate.hour > 15:
                validityDate = validityDate + timedelta(days=1)
            validityDate = validityDate.date().isoformat()
        for region in report.regions:
            if 'AT8R' in region.regionID:
                region.regionID = region.regionID.replace('AT8R', 'AT-08-0')

    bulletins = Bulletins()
    bulletins.bulletins = reports

    directory = Path(args.output)
    directory.mkdir(parents=True, exist_ok=True)
    ext = 'zip' if url[-3:] == 'zip' else 'xml'
    if url != '':
        with urlopen(url) as http, open(f'{directory}/{validityDate}-{regionID}.{ext}', mode='wb') as f:
            logging.info('Writing %s to %s', url, f.name)
            f.write(http.read())
    with open(f'{directory}/{validityDate}-{regionID}.json', mode='w', encoding='utf-8') as f:
        logging.info('Writing %s', f.name)
        json.dump(bulletins, fp=f, cls=JSONEncoder, indent=2)


if __name__ == "__main__":
    for region in args.regions.split():
        try:
            download_region(region)
        except Exception as e: # pylint: disable=broad-except
            logging.error('Failed to download %s', region, exc_info=e)
