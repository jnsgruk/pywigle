import json
import requests
import unicodecsv as csv
from dateutil import parser as date_parser
from dateutil.relativedelta import relativedelta
from datetime import date
import random
import simplekml
from proxy import ProxyList
from termcolor import cprint
from xml.sax.saxutils import escape as esc


class Wigle:

    def __init__(self, config):
        self.config = config
        self.debug = self.config["debug"]
        self.creds = self.config["creds"]
        self.proxy_list = None
        self.json_data = []

    def get_creds(self):
        """ Gets a random set of credentials from the list ingested at the start """
        try:
            creds = random.choice(self.creds)
        except IndexError:
            cprint(
                f"[ERROR] Run out of working creds! Results may not be complete!", "red", attrs=["bold"])
            return None

        return creds["api_name"], creds["api_token"]

    def get_networks(self, address=None, ssid=None, bssid=None):
        """
        Network Search - searches all networks when given an address.

        :param address:         String containing address to search for
        """

        # Initialise the proxy list if not already done
        if not self.proxy_list:
            self.proxy_list = ProxyList(
                debug=self.config["debug"], num_proxies=self.config["numProxies"])

        # Start at first page
        first = 0
        # Build params dict for query
        params = {
            "first": first,
            "resultsPerPage": 100
        }

        if address:
            # Get co-ordinates of search area
            box = self.get_box(address)
            # Set search params
            params["latrange1"] = box[0]
            params["latrange2"] = box[1]
            params["longrange1"] = box[2]
            params["longrange2"] = box[3]

        if ssid:
            params["ssidlike"] = ssid

        if bssid:
            params["bssid"] = bssid

        # While loop iterates through pages of data - API limited to 100 results per page
        while True:
            try:
                # Get some random creds and proxy
                api_name, api_token = self.get_creds()
                proxy = self.proxy_list.random()

                if self.debug:
                    cprint(
                        f"[DEBUG] Proxying via {proxy.host}:{proxy.port} with creds {api_name}/{api_token}", "grey", attrs=["bold"])

                # Send initial request, specifyng location and page
                response = requests.get(
                    url="https://api.wigle.net/api/v2/network/search",
                    auth=(api_name, api_token),
                    params=params,
                    proxies={"https": f"http://{proxy.host}:{proxy.port}"}
                )

                response_json = json.loads(response.content.decode("utf-8"))
                resultCount = response_json.get("resultCount")
                # Check if we've hit the last page
                if resultCount == 0:
                    break

                if resultCount:
                    self.json_data += response_json.get("results")

                    if self.debug:
                        cprint(
                            f"[DEBUG] Success! Added {len(response_json.get('results'))} hits to the result list", "green", attrs=["bold"])

                    # Make sure we request the next page on the next iteration
                    first += 100
                else:
                    # Probably a creds error, so we'll remove these creds and try again!
                    message = response_json.get("message")
                    if message == "too many queries today":
                        self.creds.remove(
                            {"api_name": api_name, "api_token": api_token})

                        if self.debug:
                            cprint(
                                f"[DEBUG] Failed! Removing expired creds and trying again...", "red", attrs=["bold"])

            except requests.exceptions.RequestException:
                # Probably a proxy error, so we'll remove this proxy and try again!
                if self.debug:
                    cprint(
                        f"[DEBUG] RequestException in get_networks: Removing proxy {proxy.host}:{proxy.port} and retrying...", "red", attrs=["bold"])
                self.proxy_list.remove(proxy)
            except TypeError:
                # Run out of creds, carry on processing any results we did actually get!
                break

        return self.json_data

    def get_box(self, address):
        """ Given a plain text address, this function returns an array containing the four corners of a box specified using long/lat co-ordinates """
        try:
            # Get some random creds and proxy
            api_name, api_token = self.get_creds()
            proxy = self.proxy_list.random()

            if self.debug:
                cprint(
                    f"[DEBUG] Proxying via {proxy.host}:{proxy.port} with creds {api_name}/{api_token}", "grey", attrs=["bold"])

            # Use the geocode service from the API to convert a full text address to a lat/long box
            response = requests.get(
                url="https://api.wigle.net/api/v2/network/geocode",
                auth=(api_name,  api_token),
                params={"addresscode": address},
                proxies={"https": f"http://{proxy.host}:{proxy.port}"}
            )

            # Parse the response from the web request
            response_json = json.loads(response.content)
            results = response_json.get("results")
            if results:
                box = results[0]["boundingbox"]
                # Return the bounding box if successful request
                if self.debug:
                    cprint(
                        f"[DEBUG] Success! Got Geo-Box! {box}", "green", attrs=["bold"])
                return box
            else:
                # Check if creds have been blocked for the day
                message = response_json.get("message")
                if message == "too many queries today":
                    # Remove the creds from the pool
                    self.creds.remove(
                        {"api_name": api_name, "api_token": api_token})
                else:
                    # Try again with new creds!
                    return self.get_box(address)

        except requests.exceptions.RequestException:
            if self.debug:
                cprint(
                    f"[DEBUG] RequestException in get_box: Removing proxy {proxy.host}:{proxy.port} and retrying...", "red", attrs=["bold"])
            # If there was a request error then remove the proxy and try a different one!
            self.proxy_list.remove(proxy)
            return self.get_box(address)
        except TypeError:
            cprint(
                f"[ERROR] Run out of working creds! Results may not be complete!", "red", attrs=["bold"])
            exit()

    def import_json(self, filename):
        """ Reads in a JSON file containing network information previously saved using this tool """
        data = open(filename).read()
        # Parse the data, having removed any spurious unicode characters.
        self.json_data = json.loads(data)

    def export_json(self, filename):
        """ Exports all network data to a JSON file """
        try:
            outfile = open(filename, 'w')
            json.dump(self.json_data, outfile, sort_keys=True, indent=4)
            outfile.close()
        except TypeError:
            cprint("[ERROR] Export to JSON: No data to export!",
                   "red", attrs=["bold"])
            exit()

    def export_kml(self, filename):
        """ Exports all networks into a KML file with placemarks for each network """
        try:
            # Initialise KML document
            kml = simplekml.Kml()

            # URL for circle icon
            circleUrl = "http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png"

            # Create some styles for different coloured icons
            amberCircle = simplekml.Style()
            amberCircle.iconstyle.icon.href = circleUrl
            amberCircle.iconstyle.color = simplekml.Color.orange

            greenCircle = simplekml.Style()
            greenCircle.iconstyle.icon.href = circleUrl
            greenCircle.iconstyle.color = simplekml.Color.green

            redCircle = simplekml.Style()
            redCircle.iconstyle.icon.href = circleUrl
            redCircle.iconstyle.color = simplekml.Color.red

            # Calulate date deltas to color code networks
            minus_twelve = date.today()+relativedelta(months=-12)
            minus_eighteen = date.today()+relativedelta(months=-18)
            # Loop through the network data, adding once placemark per network.
            for net in self.json_data:

                # Ensure all the fields we reference are actually present
                fields = ["ssid", "channel", "encryption",
                          "type", "netid", "firsttime", "lastupdt"]
                for f in fields:
                    if not net[f]:
                        net[f] = ""

                net["ssid"] = "".join(
                    i for i in net["ssid"] if 31 < ord(i) < 127)
                net["ssid"] = esc(net["ssid"])

                point = kml.newpoint(name=net["ssid"], coords=[
                    (net["trilong"], net["trilat"])])

                # Parse date of individual networks
                updated_date = date_parser.parse(net["lastupdt"]).date()

                # Colorise networks based on the time they were last seen
                if updated_date > minus_twelve:
                    point.style = greenCircle
                elif (updated_date > minus_eighteen) and (updated_date < minus_twelve):
                    point.style = amberCircle
                else:
                    point.style = redCircle

                # Add all the extra data to the KML point
                ed = point.extendeddata
                ed.newdata(name="SSID", value=net["ssid"])
                ed.newdata(name="Channel", value=net["channel"])
                ed.newdata(name="Encryption", value=net["encryption"])
                ed.newdata(name="Type", value=net["type"])
                ed.newdata(name="BSSID", value=net["netid"])
                ed.newdata(name="First Seen", value=net["firsttime"])
                ed.newdata(name="Last Updated", value=net["lastupdt"])

            kml.save(filename)

        except TypeError:
            cprint("[ERROR] Export to KML: No data to export!",
                   "red", attrs=["bold"])

    def export_csv(self, filename):
        """ Exports all JSON data to a CSV file """
        try:
            outfile = open(filename, 'w')
            csvwriter = csv.writer(outfile)
            # Loop through the data
            for idx, net in enumerate(self.json_data):
                # If first iteration, write the column headers out too.
                if idx == 0:
                    csvwriter.writerow(net.keys())
                csvwriter.writerow(net.values())
            outfile.close()
        except TypeError:
            cprint("[ERROR] Export to CSV: No data to export!",
                   "red", attrs=["bold"])

    def pp(self):
        """ Dumps JSON data to stdout, PrettyPrint style """
        print(json.dumps(self.json_data, sort_keys=True, indent=4))
