import argparse
import json
import requests
import csv
from pykml.factory import KML_ElementMaker as KML
from lxml import etree

class Wigle:
   
    def __init__(self):
        """ Constructor - loads API credentials from config.json """
        # Read and parse JSON file
        data = json.loads(open('config.json').read())
        self.api_name = data['api_creds']['api_name']
        self.api_token = data['api_creds']['api_token']
        self.json_data = []

    def get_networks(self, address):
        """
        Network Search - searches all networks when given an address.

        :param address:         String containing address to search for
        """
        # Get co-ordinates of search area
        box = self.get_box(address)
        first = 0
        # While loop iterates through pages of data - API limited to 100 results per page
        while True:
            try:
                # Send initial request, specifyng location and page
                response = requests.get(
                        url = "https://api.wigle.net/api/v2/network/search",
                        auth = (self.api_name,  self.api_token),
                        params = { 
                            "first" : first,
                            "resultsPerPage" : 100,
                            "latrange1" : box[0],
                            "latrange2" : box[1],
                            "longrange1" : box[2],
                            "longrange2" : box[3]
                        }
                    )

                # Check if we've hit the last page
                if response_json.get("resultCount") > 0:
                    self.json_data += response_json.get("results")
                    # Make sure we request the next page on the next iteration
                    first += 100
                else:
                    break
            except NameError:
                print "get_networks: Unexpected response. Have you hit your query limit?"
                exit()
            except requests.exceptions.RequestException:
                print "get_networks: RequestException"
                exit()
        return self.json_data

    def get_box(self, address):
        """ Given a plain text address, this function returns an array containing the four corners of a box specified using long/lat co-ordinates """
        try:
            # Use the geocode service from the API to convert a full text address to a lat/long box
            response = requests.get(url = "https://api.wigle.net/api/v2/network/geocode", auth = (self.api_name,  self.api_token), params = { "addresscode" : address })
            return response_json.get("results")[0]["boundingbox"]
        except NameError:
            print "get_box: Unexpected response. Have you hit your query limit?"
            exit()   
        except requests.exceptions.RequestException:
            print "get_box: RequestException"
            exit()

    def import_json(self, filename):
        """ Reads in a JSON file containing network information previously saved using this tool """
        data = open(filename).read()
        # Parse the data, having removed any spurious unicode characters.
        self.json_data = json.loads(data.decode('unicode_escape').encode('ascii','ignore'))
    
    def export_json(self, filename):
        """ Exports all network data to a JSON file """
        try:
            outfile = open(filename,'w')
            json.dump(self.json_data, outfile)
            outfile.close()
        except TypeError:
            print "Export to JSON: No data to export!"
            exit()

    def export_kml(self, filename):
        """ Exports all networks into a KML file with placemarks for each network """
        try:
            document = KML.kml(KML.Document())
            # Create an icon style for each Placemark to use
            document.Document.append(
                KML.Style(
                    KML.IconStyle(
                        KML.scale(1.0),
                        KML.color('ff0000ff'),
                        KML.Icon(
                            KML.href("http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png"),
                        ),
                        id="mystyle"
                    ),
                    id="circle"
                    )
                )
            # Loop through the network data, adding once placemark per network.
            for net in self.json_data:
                pm = KML.Placemark(
                    KML.name(net["ssid"]), # title of the placemark
                    KML.styleUrl("#circle"), # use the style we defined above
                    KML.Point(KML.coordinates(net["trilong"],',',net["trilat"])),
                    # This ExtendedData is shown when a Placemark is selected in Google Earth
                    KML.ExtendedData(
                        KML.Data(KML.value(net["ssid"]), name="SSID"),
                        KML.Data(KML.value(net["channel"]), name="Channel"),
                        KML.Data(KML.value(net["wep"]), name="Encryption"),
                        KML.Data(KML.value(net["type"]), name="Type"),
                        KML.Data(KML.value(net["netid"]), name="BSSID"),
                        KML.Data(KML.value(net["firsttime"]), name="First Seen"),
                        KML.Data(KML.value(net["lastupdt"]), name="Last Updated")
                    )
                )
                document.Document.append(pm)

            # Write the KML file out to disk.
            outfile = open(filename, 'w')
            outfile.write(etree.tostring(document, pretty_print=True))
            outfile.close()
        except TypeError:
            print "Export to KML: No data to export!"

    def export_csv(self, filename):
        """ Exports all JSON data to a CSV file """
        try:
            outfile = open(filename,'w')
            csvwriter = csv.writer(outfile)
            # Loop through the data
            for idx,net in enumerate(self.json_data):
                # If first iteration, write the column headers out too.
                if idx == 0: csvwriter.writerow(net.keys())
                csvwriter.writerow(net.values())
            outfile.close()
        except TypeError:
            print "Export to CSV: No data to export!"
            exit()

    def pp(self):
        """ Dumps JSON data to stdout, PrettyPrint style """
        print json.dumps(self.json_data, sort_keys=True, indent=4)


# Set up command line arguments
parser = argparse.ArgumentParser(description='Searches Wigle.net for all Wifi hotspots that have been seen in a specified area. If no output formats are specified (JSON/CSV/KML), the script will output JSON to stdout')
parser.add_argument('--location', '-l', required=False, type=str, help='Location to query. E.g. "Basingstoke, Hampshire, UK"')
parser.add_argument('--json-out', '-j', required=False, type=str, help='Name of JSON file to write if required.')
parser.add_argument('--kml-out', '-k', required=False, type=str, help='Name of KML file to write if required.')
parser.add_argument('--csv-out', '-c', required=False, type=str, help='Name of CSV file to write if required.')
parser.add_argument('--input-json', '-i', required=False, type=str, help='Name of JSON file to read from. Used to convert existing JSON file into CSV/KML.')
parser.add_argument('--print', '-p', required=False, action='store_true', help='Output JSON to stdout.')
args = parser.parse_args()

# Create a new instance of the Wigle class
wigle = Wigle()
if args.location: wigle.get_networks(args.location)
if args.input_json: wigle.import_json(args.input_json)
# Parse output arguments and call relevant functions
if args.json_out: wigle.export_json(args.json_out)
if args.csv_out: wigle.export_csv(args.csv_out)
if args.kml_out: wigle.export_kml(args.kml_out)

# If no output is specified, or the print argument is used, output data to stdout
if (not(args.json_out or args.kml_out or args.csv_out)) or getattr(args, 'print') : wigle.pp()
