import requests
from polyline.codec import PolylineCodec

def match(points, host='http://localhost:5000', geometry=True, gps_precision=-1, matching_beta=-1, decode_polyline=True):
    url = host + '/match?'
    for loc, t in points:
        url += 'loc=' + str(loc[0]) + ',' + str(loc[1]) + '&t=' + str(t)
    url += '&geometry=' + str(geometry).lower() + '&gps_precision=' + str(gps_precision) + '&matching_beta=' + str(matching_beta)
    print url
    r = requests.get(url)
    r_json = r.json()
    if decode_polyline:
        for i, matching in enumerate(r_json['matchings']):
            geom_encoded = r_json["matchings"][i]["geometry"]
            geom_decoded = [[point[0]/10.0,point[1]/10.0] for point in PolylineCodec().decode(geom_encoded)]
            r_json["matchings"][i]["geometry"] = geom_decoded
    return r_json

points = [([-33.45017046193167,-70.65281867980957], 0),
          ([-33.45239047269638,-70.65300107002258], 5),
          ([-33.453867464504555,-70.65277576446533], 7)]

print match(points, host='http://localhost:5000', geometry=True,gps_precision=-1, matching_beta=-1, decode_polyline=True)
