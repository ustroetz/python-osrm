
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

points = [([-70.6541383266449,-33.449597546702904], 0),
          ([-70.65479278564453,-33.45069861480559], 5),
          ([-70.65380573272705,-33.452023458708645], 7)]

print match(points, host='http://localhost:5000', geometry=False,gps_precision=-1, matching_beta=-1)
```
