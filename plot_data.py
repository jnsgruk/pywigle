import json
import argparse
from pykml.factory import KML_ElementMaker as KML
from lxml import etree

parser = argparse.ArgumentParser(description='Creates a KML file with data from Wigle. Takes a JSON file as input')
parser.add_argument('--in', '-i', required=True, type=str, help='JSON file to read.')
parser.add_argument('--out', '-o', required=False, type=str, help='KML file to write.')
args = vars(parser.parse_args())

data = open(args["in"]).read()
data = json.loads(data.decode('unicode_escape').encode('ascii','ignore'))

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
        id="circle"))


for net in data:
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

outfile = open(args["out"], 'w')
outfile.write(etree.tostring(document, pretty_print=True))