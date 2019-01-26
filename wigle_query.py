import argparse
import json
from wigle import Wigle

# Set up command line arguments
parser = argparse.ArgumentParser(
    description='Searches Wigle.net for all Wifi hotspots that have been seen in a specified area. If no output formats are specified (JSON/CSV/KML), the script will output JSON to stdout')
# Allow user to pass a config file. Use config.json by default
parser.add_argument('--config-file', '-C', required=False, type=str,
                    help='Path to config file"', default="config.json")
# Search networks by location
parser.add_argument('--location', '-l', required=False, type=str,
                    help='Location to query. E.g. "Basingstoke, Hampshire, UK"')
# Search networks by SSID
parser.add_argument('--ssid', '-s', required=False, type=str,
                    help='SSID to query')
# Search networks by BSSID
parser.add_argument('--mac', '-m', required=False, type=str,
                    help='BSSID (MAC address) to query')

# Output Arguments
parser.add_argument('--json-out', '-j', required=False,
                    type=str, help='Name of JSON file to write if required.')
parser.add_argument('--kml-out', '-k', required=False,
                    type=str, help='Name of KML file to write if required.')
parser.add_argument('--csv-out', '-c', required=False,
                    type=str, help='Name of CSV file to write if required.')
parser.add_argument('--print', '-p', required=False,
                    action='store_true', help='Output JSON to stdout.')

# Ingest a previous JSON file to convert
parser.add_argument('--input-json', '-i', required=False, type=str,
                    help='Name of JSON file to read from. Used to convert existing JSON file into CSV/KML.')
args = parser.parse_args()


# Read in the config file
config = json.loads(open(args.config_file).read())

# Create a new instance of the Wigle class
wigle = Wigle(config)
if args.location:
    wigle.get_networks(address=args.location, ssid=args.ssid, bssid=args.mac)
if args.input_json:
    wigle.import_json(args.input_json)

# Parse output arguments and call relevant functions
if args.json_out:
    wigle.export_json(args.json_out)
if args.csv_out:
    wigle.export_csv(args.csv_out)
if args.kml_out:
    wigle.export_kml(args.kml_out)

# If no output is specified, or the print argument is used, output data to stdout
if (not(args.json_out or args.kml_out or args.csv_out)) or getattr(args, 'print'):
    wigle.pp()
