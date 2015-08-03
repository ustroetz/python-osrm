
# python-osrm
A Python wrapper around the [OSRM API](https://github.com/Project-OSRM/osrm-backend/wiki/Server-api)

## Install
```
git clone git@github.com:ustroetz/python-osrm.git
cd python-osrm
python setup.py install
```
# Requires
  * polyline
  * requests
  * numpy
  * pandas
  * GDAL

## Usage

### match
```
from osrm import osrm.match as match

points = [([-33.45017046193167,-70.65281867980957], 0),
          ([-33.45239047269638,-70.65300107002258], 5),
          ([-33.453867464504555,-70.65277576446533], 7)]

print match(points, host='http://localhost:5000', geometry=True,gps_precision=-1, matching_beta=-1, decode_polyline=True)
```

### table
A simple wrapping function to fetch the matrix computed by OSRM as a dataframe (or as a numpy array) :
```
list_coord = [[21.0566163803209, 42.004088575972],
              [21.3856064050746, 42.0094518118189],
              [20.9574645547597, 41.5286973392856],
              [21.1477394809847, 41.0691482795275],
              [21.5506463080973, 41.3532256406286]]

list_id = ['name1', 'name2', 'name3', 'name4', 'name5']

time_matrix = osrm.table(list_coord, list_id, output='dataframe', host='http://localhost:5000')

print(time_matrix)  # now in minutes
       name1  name2  name3  name4  name5
name1    0.0   25.7   69.8  169.7  126.8
name2   26.1    0.0   88.1  149.4  106.3
name3   70.2   88.6    0.0  100.0   65.6
name4  158.4  137.6   99.8    0.0   49.4
name5  115.4   94.6   65.6   48.8    0.0
```

### simple_viaroute
Return the original JSON reponse from OSRM (with optionnaly the geometry decoded in WKT or WKB)
```
import osrm
result = osrm.simple_viaroute([21.0566163803209,42.004088575972],
							  [20.9574645547597, 41.5286973392856], output='WKT')

result['route_summary']['total_distance']
76271

result['route_geometry']
'LINESTRING (21.056616 42.004088 0,21.056629 42.004078 0,21.056937 42.003885 0,
(...)
,20.957376 41.529222 0,20.957172 41.528817 0,20.957466 41.528699 0)'
```
