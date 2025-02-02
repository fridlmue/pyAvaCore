# pyAvaCore

Python library to download and parse [EAWS](https://www.avalanches.org/) avalanche bulletins.
PyAvaCore can generate [CAAMLv6](https://gitlab.com/albina-euregio/albina-caaml/-/tree/master/6.0) (CAAMLv6 is not yet officially released) compliant JSON files for the supported regions and Avalanche Warning Services (AWS).

## License

This Project is Licensed under GPL-3.0

## Utilization

pyAvaCore is used in the [ALBINA](https://gitlab.com/albina-euregio) project to parse the neighbor bulletins in a unified way as JSON-File and a ratings.json file with the danger levels for the regions. This is used to augment the map with the danger rating information.

* https://avalanche.report/

pyAvaCore is used by [EAWS](https://www.avalanches.org/) to visualize (almost all) avalanche bulletins of Europe on a single map:

* https://www.avalanches.org/

It is also used as parser for the mobile app ["avaRisk"](https://github.com/fridlmue/harbour-avarisk) as background parser to fetch a wide variety of reports.

## Dependencies

As on some target platforms the number of available Python dependencies is limited, the project aims to work with minimal external dependencies. The dependencies can be found in the ["requirements.txt"](requirements.txt). Python 3.9 is the current Python target version. On Windows, please install the package `tzdata`.

## CLI Parameters

```
> python -m avacore --help
usage: avacore [-h] [--lang LANG] [--date DATE] [--regions REGIONS]
               [--merge-dates DATES] [--merge-regions REGIONS]
               [--protect-overwrite-now TIMESTAMP] [--output OUTPUT]
               [--geojson GEOJSON] [--cli CLI]

Download and parse EAWS avalanche bulletins

options:
  -h, --help            show this help message and exit
  --lang LANG           language to fetch avalanche bulletins for
  --date DATE           date to fetch avalanche bulletins for;
                        date is specified in ISO 8601 format `YYYY-MM-DD`;
                        multiple dates may be specified using a space separator;
                        an ISO 8601 interval may be specified as `YYYY-MM-DD/YYYY-MM-DD`
  --regions REGIONS     avalanche regions to download
  --merge-dates DATES   dates to merge into one file
  --merge-regions REGIONS
                        avalanche regions to merge into one file
  --protect-overwrite-now TIMESTAMP
                        exclude bulletins prior the given timestamp
  --output OUTPUT       output directory
  --log LOG             directory for log files
  --geojson GEOJSON     eaws-regions directory containing *micro-regions_elevation.geojson.json of
  --cli CLI             print output to cli? [y]es, [n]o or [o]nly to cli ([o] will not write files)
```

In default configuration, pyAvaCore will fetch the bulletins for all supported regions. 

The regions to fetch can be limited with the `--regions` parameter. Multiple regions can be entered delimited by space. E. g. `python -m avacore --regions AT-02 IT-57` will fetch the bulletins for AT-02 and IT-57 only.

The files are written to `./data` by default the folder can be adjusted by setting the `--output ./subfolder/of/choice`.
The log files are written to `./logs` by default the folder can be adjusted by setting the `--log ./subfolder/of/choice`.

A CLI output of the bulletin can be generated with the `--cli` parameter. Default is `n`, which gives no CLI output. With `y` a CLI output is generated in addition to the JSON files. With `o`, only the cli output is generated but no JSON files are written.

## Supported Regions
At the moment the following regions are supported with the localization versions mentioned:
- AD (Danger Ratings only)
- AT Tirol (https://avalanche.report) (EN/DE/FR)
- AT Kärnten (https://lawinenwarndienst.ktn.gv.at/) (DE)
- AT Oberöstereich (https://www.land-oberoesterreich.gv.at/lawinenwarndienst.htm) (DE)
- AT Niederösterreich (https://www.lawinenwarndienst-niederoesterreich.at/) (DE)
- AT Salzburg (https://lawine.salzburg.at/) (EN/DE)
- AT Styria (https://www.lawine-steiermark.at/) (EN/DE)
- AT Vorarlberg (https://warndienste.cnv.at/dibos/lawine/index.html) (EN/DE)
- CH (including FL) (https://www.slf.ch/en/index.html) (EN/DE)
- CZ (https://www.horskasluzba.cz/cz/avalanche-json) (CZ)
- DE Bavaria (https://www.lawinenwarndienst-bayern.de) (EN/DE)
- ES Pyrenees Basque (http://www.aemet.es/xml/montana/p18tarn1.xml) (ES)
- ES Pyrenees Catalan (https://bpa.icgc.cat) (ES)
- ES Val d'Aran (https://lauegi.conselharan.org/) (EN/DE)
- FR (https://meteofrance.com/meteo-montagne) (FR)
- GB (https://www.sais.gov.uk/) (EN)
- IS (https://en.vedur.is/avalanches/forecast) (IS/EN)
- IT Bolzano (https://avalanche.report) (EN/DE)
- IT Trentino (https://avalanche.report) (EN/DE)
- IT Piemonte (https://bollettini.aineva.it/) (EN/DE/FR)
- IT Valle d’Aosta (https://bollettini.aineva.it/) (EN/DE/FR)
- IT Lombardia (https://bollettini.aineva.it/) (EN/DE/FR)
- IT Veneto (https://bollettini.aineva.it/) (EN/DE/FR)
- IT Friuli – Venezia Giulia (https://bollettini.aineva.it/) (EN/DE/FR)
- IT Marche (https://bollettini.aineva.it/) (EN/DE/FR)
- SI (http://meteo.arso.gov.si/) (SI)
- SK (http://www.laviny.sk/) (SK)
- NO (https://www.varsom.no) (NO/EN)
- PL (https://www.gopr.pl/) (PL)
- PL (https://lawiny.topr.pl/) (PL)

### RegionIDs

The IDs for the different regions currently supported can be found [here](REGIONS.md).

## Credits

The parser uses the png.py file from the [PyPNG-Project](https://github.com/drj11/pypng) ([MIT License](https://github.com/drj11/pypng/blob/main/LICENCE)).
