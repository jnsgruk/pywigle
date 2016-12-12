import argparse
import json
import requests

class Wigle:
    """
    Wigle class should be instantiated with wigle API Name and API Token which can be accessed from https://wigle.net/account
    """
    api_name  = None
    api_token = None

    def __init__(self, api_name, api_token):
        """
        Wigle Constructor

        :param api_name:    String with API Name
        :param api_token:   String with API Token
        """
        self.api_name = api_name
        self.api_token = api_token

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
                        "longrange2" : box[3],
                        "freenet" : "false",
                        "paynet" : "false"
                    }
                )

            if response.status_code == 200:
                response_json = json.loads(response.text)
                if response_json.get("error"):
                    print "network_search: " + response_json.get("error")
                    exit()
                else:
                    if response_json.get("resultCount") > 0:
                        results += response_json.get("results")
                        first += 100
                    else:
                        break
            else:
                print "network_search: " + response.status_code
                exit()

        return results

    def get_box(self, address):
        response = requests.get(
                url = "https://api.wigle.net/api/v2/network/geocode",
                auth = (self.api_name,  self.api_token),
                params = { "addresscode" : address }
            )

        if response.status_code == 200:
            response_json = json.loads(response.text)
            if response_json.get("error"):
                print "get_box: " + response_json.get("error")
                exit()
            else:
                return response_json.get("results")[0]["boundingbox"]
        else:
            print "get_box: " + response.status_code
            exit()


    def pp(self, json_stuff):
        print json.dumps(json_stuff, sort_keys=True, indent=4)


parser = argparse.ArgumentParser(description='Searches Wigle.net for all Wifi hotspots that have been seen in a specified area')
parser.add_argument('--location', '-l', required=True, type=str, help='Location to query. E.g. "Basingstoke, Hampshire, UK"')
args = vars(parser.parse_args())


wigle = Wigle("AIDf013644d91eea7d64d26593fb44bb4fb", "e3f1986ddaac1e1eec6a466ce200a183")
wigle.pp(wigle.network_search(args["location"]))
