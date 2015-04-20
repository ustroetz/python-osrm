import requests
# from polyline.codec import PolylineCodec
import json

def match(points, host='http://localhost:5000', geometry=False,gps_precision=-1, matching_beta=-1, decode_polyline=True):
    url = host + '/match?'
    for loc, t in points:
        url += 'loc=' + str(loc[0]) + ',' + str(loc[1]) + '&t=' + str(t)
    # url += '&geometry=' + str(geometry) + '&gps_precision=' + str(gps_precision) + '&matching_beta=' + str(matching_beta)
    print url
    r = requests.get(url)
    r_json = r.json()
    if decode_polyline:
        for i, matching in enumerate(r_json['matchings']):
            my_new_value = 'something'
            r_json["matchings"][i]["geometry"] = my_new_value
    return r_json
