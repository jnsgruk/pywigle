import argparse
import json
import requests
import csv
from pykml.factory import KML_ElementMaker as KML
from lxml import etree

class Wigle:
    
    api_name  = None
    api_token = None
    json_data = None

    def __init__(self):
        data = json.loads(open('config.json').read())
        self.api_name = data['api_creds']['api_name']
        self.api_token = data['api_creds']['api_token']

    def network_search(self, address):
        """
        Network Search - searches all networks when given an address.

        :param address:         String containing address to search for
        """
        box = self.get_box(address)
        first = 0
        results = []
        while True:
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

            try:
                if response_json.get("resultCount") > 0:
                    results += response_json.get("results")
                    first += 100
                else:
                    break
            except NameError:
                print "get_box: Unexpected response. Have you hit your query limit?"
                exit()
    
        self.json_data = results
        return results

    def import_json(self, filename):
        data = open(filename).read()
        self.json_data = json.loads(data.decode('unicode_escape').encode('ascii','ignore'))

    def export_kml(self, filename):
        try:
            document = KML.kml(KML.Document())
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

            for net in self.json_data:
                pm = KML.Placemark(
                    KML.name(net["ssid"]),
                    KML.styleUrl("#circle"),
                    KML.Point(KML.coordinates(net["trilong"],',',net["trilat"])),
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

            outfile = open(filename, 'w')
            outfile.write(etree.tostring(document, pretty_print=True))
            outfile.close()
        except TypeError:
            print "Export to KML: No data to export!"

    def export_csv(self, filename):
        try:
            outfile = open(filename,'w')
            csvwriter = csv.writer(outfile)
            for idx,net in enumerate(self.json_data):
                if idx == 0: csvwriter.writerow(net.keys())
                csvwriter.writerow(net.values())
            outfile.close()
        except TypeError:
            print "Export to CSV: No data to export!"
            exit()

    def export_json(self, filename):
        try:
            outfile = open(filename,'w')
            json.dump(self.json_data, outfile)
            outfile.close()
        except TypeError:
            print "Export to JSON: No data to export!"
            exit()

    def get_box(self, address):
        response = requests.get(url = "https://api.wigle.net/api/v2/network/geocode", auth = (self.api_name,  self.api_token), params = { "addresscode" : address })
        try:
            return response_json.get("results")[0]["boundingbox"]
        except NameError:
            print "get_box: Unexpected response. Have you hit your query limit?"
            exit()        

    def pp(self):
        print json.dumps(self.json_data, sort_keys=True, indent=4)


parser = argparse.ArgumentParser(description='Searches Wigle.net for all Wifi hotspots that have been seen in a specified area. If no output formats are specified (JSON/CSV/KML), the script will output JSON to stdout')
parser.add_argument('--location', '-l', required=False, type=str, help='Location to query. E.g. "Basingstoke, Hampshire, UK"')
parser.add_argument('--json-out', '-j', required=False, type=str, help='Name of JSON file to write if required.')
parser.add_argument('--kml-out', '-k', required=False, type=str, help='Name of KML file to write if required.')
parser.add_argument('--csv-out', '-c', required=False, type=str, help='Name of CSV file to write if required.')
parser.add_argument('--input-json', '-i', required=False, type=str, help='Name of JSON file to read from. Used to convert existing JSON file into CSV/KML.')
parser.add_argument('--print', '-p', required=False, action='store_true', help='Output JSON to stdout.')
args = parser.parse_args()

wigle = Wigle()
if args.location: wigle.network_search(args.location)
if args.input_json: wigle.import_json(args.input_json)

if args.json_out: wigle.export_json(args.json_out)
if args.csv_out: wigle.export_csv(args.csv_out)
if args.kml_out: wigle.export_kml(args.kml_out)

if (not(args.json_out or args.kml_out or args.csv_out)) or getattr(args, 'print') : wigle.pp()
