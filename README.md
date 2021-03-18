# pyAvaCore

Python library to download and parse [EAWS](https://www.avalanches.org/) avalanche bulletins

## License

This Project is Licensed under GPL-3.0

## Utilization

pyAvaCore is used in the ALBINA project to parse the neighbours bulletins in a unified way as JSON-File.
It is also used as parser for the mobile app ["avaRisk"](https://github.com/fridlmue/harbour-avarisk) as background parser to fetch a wide variety of reports.

## Dependencies

As on some target platforms the number of available Python dependecies is limited, the project aims to work with minimal external dependencies. Python 3.6 is the current Python target version.

## Supported Regions
At the moment the following regions are supported with the localization versions mentioned:
- AT Tirol (https://avalanche.report) (EN/DE)
- AT Kärnten (https://lawinenwarndienst.ktn.gv.at/) (DE)
- AT Oberöstereich (https://www.land-oberoesterreich.gv.at/lawinenwarndienst.htm) (DE)
- AT Niederösterreich (https://www.lawinenwarndienst-niederoesterreich.at/) (DE)
- AT Salzburg (https://lawine.salzburg.at/) (EN/DE)
- AT Styria (https://www.lawine-steiermark.at/) (EN/DE)
- AT Vorarlberg (https://warndienste.cnv.at/dibos/lawine/index.html) (EN/DE)
- CH (including FL) (https://www.slf.ch/en/index.html) (EN/DE)
- DE Bavaria (https://www.lawinenwarndienst-bayern.de) (EN/DE)
- ES Val d'Aran (https://lauegi.conselharan.org/) (EN/DE)
- IT Bolzano (https://avalanche.report) (EN/DE)
- IT Trentino (https://avalanche.report) (EN/DE)

### RegionIDs

The IDs for the different regions currently supported can be found [here](REGIONS.md).

## Credits

The parser uses the png.py file from the [PyPNG-Project](https://github.com/drj11/pypng) ([MIT License](https://github.com/drj11/pypng/blob/main/LICENCE)).
