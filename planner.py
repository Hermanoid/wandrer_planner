from pykml import parser

with open("wandrer-23-08-23.kml", "r") as f:
    root = parser.parse(f).getroot()

namespace = {"kml": 'http://www.opengis.net/kml/2.2'}
pms = root.xpath(".//kml:Placemark[.//kml:Polygon]", namespaces=namespace)
# for p in pms:
#   print(p.Polygon.outerBoundaryIs.LinearRing.coordinates)
print(pms[0])

