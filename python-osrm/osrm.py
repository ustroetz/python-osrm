import requests
from polyline.codec import PolylineCodec
import json

def match(points, host='http://localhost:5000', geometry=False,gps_precision=-1, matching_beta=-1, decoded_polyline=True):
    url = host + '/match?'
    for loc, t in points:
        url += 'loc=' + str(loc[0]) + ',' + str(loc[1]) + '&t=' + str(t)
    # url += '&geometry=' + str(geometry) + '&gps_precision=' + str(gps_precision) + '&matching_beta=' + str(matching_beta)
    print url
    r = requests.get(url)
    r_json = r.json()

    if decoded_polyline:
        r_json = r_json
    #     for matching in r_json['matchings']:
    #         print [[point[1]/10.0, point[0]/10.0] for point in PolylineCodec().decode(matching['geometry'])]
    #     city_geojson['features'] = [city for city in city_geojson['features']]

    print r_json
