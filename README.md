## Wigle API Network Search & Mapping Script

Wigle Python script that can search a specific area for hotspots and output the results as JSON, CSV or KML. Has the ability to use multiple API token pairs and will use different, autodetected proxies for each request.

To install/set up:

```
git clone git@github.com:jnsgruk/pywigle.git
cd pywigle
pip install -r requirements.txt
mv config.json.example config.json
```

Next, edit `config.json` and add your Wigle API key details. These can be found [here](https://wigle.net/account) (Wigle.net account required).

```
usage: wigle_query.py [-h] [--config-file CONFIG_FILE] [--location LOCATION]
                      [--ssid SSID] [--mac MAC] [--json-out JSON_OUT]
                      [--kml-out KML_OUT] [--csv-out CSV_OUT] [--print]
                      [--input-json INPUT_JSON]

Searches Wigle.net for all Wifi hotspots that have been seen in a specified
area. If no output formats are specified (JSON/CSV/KML), the script will
output JSON to stdout

optional arguments:
  -h, --help            show this help message and exit
  --config-file CONFIG_FILE, -C CONFIG_FILE
                        Path to config file"
  --location LOCATION, -l LOCATION
                        Location to query. E.g. "Basingstoke, Hampshire, UK"
  --ssid SSID, -s SSID  SSID to query
  --mac MAC, -m MAC     BSSID (MAC address) to query
  --json-out JSON_OUT, -j JSON_OUT
                        Name of JSON file to write if required.
  --kml-out KML_OUT, -k KML_OUT
                        Name of KML file to write if required.
  --csv-out CSV_OUT, -c CSV_OUT
                        Name of CSV file to write if required.
  --print, -p           Output JSON to stdout.
  --input-json INPUT_JSON, -i INPUT_JSON
                        Name of JSON file to read from. Used to convert
                        existing JSON file into CSV/KML.
```
