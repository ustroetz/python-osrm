
# python-osrm
A Python wrapper around the [OSRM API](https://github.com/Project-OSRM/osrm-backend/wiki/Server-api),
providing an easy access to *viaroute*, *locate*, *nearest*, *match* and *table*.
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
```python
In [17]: import osrm

In [18]: points = [(-33.45017046193167,-70.65281867980957),
          (-33.45239047269638,-70.65300107002258),
          (-33.453867464504555,-70.65277576446533)]

In [19]: result = osrm.match(points, step=False, overview="simplified")
```

### route
Return the original JSON reponse from OSRM (with optionnaly the geometry decoded in WKT or WKB)
```python
In [23]: import osrm
In [24]: result = osrm.simple_route(
                      [21.0566163803209,42.004088575972], [20.9574645547597, 41.5286973392856],
                      output='route', overview="full", geometry='wkt')

In [25]: result['distance']
Out[25]: 76271

In [26]: result['geometry']
Out[26]:
'LINESTRING (21.056616 42.004088 0,21.056629 42.004078 0,21.056937 42.003885 0,
(...)
,20.957376 41.529222 0,20.957172 41.528817 0,20.957466 41.528699 0)'
```

### table
A simple wrapping function to fetch the matrix computed by OSRM as a dataframe (or as a numpy array) :
```python
In [28]: import osrm

In [29]: list_coord = [[21.0566163803209, 42.004088575972],
    ...:               [21.3856064050746, 42.0094518118189],
    ...:               [20.9574645547597, 41.5286973392856],
    ...:               [21.1477394809847, 41.0691482795275],
    ...:               [21.5506463080973, 41.3532256406286]]

In [30]: list_id = ['name1', 'name2', 'name3', 'name4', 'name5']

In [31]: time_matrix = osrm.table(list_coord,
                                  ids_origin=list_id,
                                  output='dataframe')

In [32]: time_matrix
Out[32]:
       name1  name2  name3  name4  name5
name1    0.0   25.7   69.8  169.7  126.8
name2   26.1    0.0   88.1  149.4  106.3
name3   70.2   88.6    0.0  100.0   65.6
name4  158.4  137.6   99.8    0.0   49.4
name5  115.4   94.6   65.6   48.8    0.0
```

### nearest

```python
In [22]: import osrm

In [23]: res = osrm.nearest([22.1021271845936,	41.5078687005805])

In [24]: res
Out[24]:
{'waypoints': [{'name': 'Friedrichstraße',
   'hint': 'niwKgGPotIqSrAAAEAAAABgAAAAGAAAAAAAAAP-KNAepXJkDbrcAAP9LzACoWCEDO0zMAKxYIQMBAAEBfDhq3w==',
   'location': [13.388799, 52.517032],
   'distance': 4.085341}],
 'code': 'Ok'}

```

### Accessibilit isochrones

```python
In [25]: from osrm import access_isochrone

In [26]: gdf, origin = osrm.access_isocrone((2.3888599, 48.5170365), n_breaks=7)


```
