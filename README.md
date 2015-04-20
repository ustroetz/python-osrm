
# python-osrm
A Python wrapper around the [OSRM API](https://github.com/Project-OSRM/osrm-backend/wiki/Server-api)

## Install
python setup.py install

# Requires
  * polyline==1.1
  * requests

## Usage

### match
```
from osrm import match

points = [([-33.45017046193167,-70.65281867980957], 0),
          ([-33.45239047269638,-70.65300107002258], 5),
          ([-33.453867464504555,-70.65277576446533], 7)]

print match(points, host='http://localhost:5000', geometry=True,gps_precision=-1, matching_beta=-1, decode_polyline=True)
```
