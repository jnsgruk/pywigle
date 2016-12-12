##  Wigle API Network Search & Mapping Script

Wigle Python script that can search a specific area for hotspots and output the results as JSON, CSV or KML.

To install/set up:

```
git clone ssh://git@git.jon0.co.uk:2222/jon/pywigle.git
cd pywigle
pip install -r requirements.txt
mv config.json.example config.json
```

Next, edit `config.json` and add your Wigle API key details. These can be found [here](https://wigle.net/account) (Wigle.net account required).

```
usage: wigle_query.py [-h] [--location LOCATION] [--json-out JSON_OUT]
                      [--kml-out KML_OUT] [--csv-out CSV_OUT]
                      [--input-json INPUT_JSON] [--print]

Searches Wigle.net for all Wifi hotspots that have been seen in a specified
area

optional arguments:
  -h, --help            show this help message and exit
  --location LOCATION, -l LOCATION
                        Location to query. E.g. "Basingstoke, Hampshire, UK"
  --json-out JSON_OUT, -j JSON_OUT
                        Name of JSON file to write if required.
  --kml-out KML_OUT, -k KML_OUT
                        Name of KML file to write if required.
  --csv-out CSV_OUT, -c CSV_OUT
                        Name of CSV file to write if required.
  --input-json INPUT_JSON, -i INPUT_JSON
                        Name of JSON file to read from. Used to convert
                        existing JSON file into CSV/KML.
  --print, -p           Output JSON to stdout.
  ```
