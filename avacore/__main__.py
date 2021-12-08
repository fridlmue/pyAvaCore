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
from .avabulletin import AvaBulletin, DangerRatingType
from .geojson import Feature, FeatureCollection, Style

parser = argparse.ArgumentParser(description='Download and parse EAWS avalanche bulletins')
parser.add_argument('--regions',
                    default="AT-02 AT-03 AT-04 AT-05 AT-06 AT-08 DE-BY CH SI FR IT-AINEVA",
                    help='avalanche region to download')
parser.add_argument('--output',
                    default='./data',
                    help='output directory')
parser.add_argument('--cache',
                    default='./cache',
                    help='cache directory')
parser.add_argument('--geojson',
                    help='eaws-regions directory containing *micro-regions_elevation.geojson.json of')
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

    def augment_geojson(self, geojson: FeatureCollection):
        for feature in geojson.features:
            self.augment_feature(feature)
            
    def augment_feature(self, feature: Feature):
        WARNLEVEL_COLORS = ['', '#ccff66', '#ffff00', '#ff9900', '#ff0000', '#000000']
        id = feature.properties.id
        elevation = feature.properties.elevation
        def affects_region(b: AvaBulletin):
            return id in [r.regionID for r in b.regions]
        def affects_danger(d: DangerRatingType):
            if id.startswith('CH-') or id.startswith('IT-21-') or id.startswith('IT-23-') or id.startswith('IT-25-') or id.startswith('IT-25-') or id.startswith('IT-34-') or id.startswith('IT-36-') or id.startswith('IT-57-') or id.startswith('FR-'):
                return True
            elif not d.elevation:
                return True
            elif not (hasattr(d.elevation, 'lowerBound') or hasattr(d.elevation, 'upperBound')):
                return True
            elif hasattr(d.elevation, 'upperBound') and elevation == 'low':
                return True
            elif hasattr(d.elevation, 'lowerBound') and elevation == 'high':
                return True
            else:
                return False
        bulletins = [b for b in self.bulletins if affects_region(b)]
        dangers = [d.get_mainValue_int() for b in bulletins for d in b.dangerRatings if affects_danger(d)]
        if not dangers:
            return
        feature.properties.style = Style(
            stroke=False, 
            fill_color=WARNLEVEL_COLORS[max(dangers)],
            fill_opacity=0.5,
            class_name='mix-blend-mode-multiply',
        )


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
    if args.geojson:
        with open(f'{args.geojson}/{regionID}_micro-regions_elevation.geojson.json', encoding='utf-8') as f:
            geojson = FeatureCollection.from_dict(json.load(f))
        bulletins.augment_geojson(geojson)
        with open(f'{directory}/{validityDate}-{regionID}.geojson', mode='w', encoding='utf-8') as f:
            logging.info('Writing %s', f.name)
            json.dump(geojson.to_dict(), fp=f)


if __name__ == "__main__":
    for region in args.regions.split():
        try:
            download_region(region)
        except Exception as e: # pylint: disable=broad-except
            logging.error('Failed to download %s', region, exc_info=e)
