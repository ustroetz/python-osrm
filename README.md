
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
from osrm import osrm.match as match

points = [([-33.45017046193167,-70.65281867980957], 0),
          ([-33.45239047269638,-70.65300107002258], 5),
          ([-33.453867464504555,-70.65277576446533], 7)]

print match(points, host='http://localhost:5000', geometry=True,gps_precision=-1, matching_beta=-1, decode_polyline=True)
```

### simple_viaroute
Return the original JSON reponse from OSRM (with optionnaly the geometry decoded in WKT or WKB)
```python
In [23]: import osrm
In [24]: result = osrm.simple_viaroute([21.0566163803209,42.004088575972],
							  [20.9574645547597, 41.5286973392856], output='WKT')

In [25]: result['route_summary']['total_distance']
Out[25]: 76271

In [26]: result['route_geometry']
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

In [31]: time_matrix = osrm.table(list_coord, list_id, output='dataframe', host='http://localhost:5000')

In [32]: time_matrix  # Now in minutes
Out[32]: 
       name1  name2  name3  name4  name5
name1    0.0   25.7   69.8  169.7  126.8
name2   26.1    0.0   88.1  149.4  106.3
name3   70.2   88.6    0.0  100.0   65.6
name4  158.4  137.6   99.8    0.0   49.4
name5  115.4   94.6   65.6   48.8    0.0
```

### table_OD
Function to get a time matrix (in minutes) between different origins and destinations (N:M) as a DataFrame.
The maximum size of matrix can be set when launching osrm-routed (for example 1000):
```
./osrm-routed file.osrm --max-table-size 1000
```
and the `OSRM_max_table` parameter have to be the same. If the size of the matrix exceed the `--max-table-size`
the function will make the needed queries and reassemble the matrix.
For example, let say i started my osrm instance with `--max-table-size 100` and i need a time matrix between
a group of 3 locations and a group of 105 location :
```python
In [27]: print('Nb origins : {}\nNb destinations : {}'.format(len(listOrigins), len(listDest)))
Nb origins : 3
Nb destinations : 105

In [28]: %time df_result = osrm.table_OD(listDest, nameDest,
					 listOrigins, nameOrigins, OSRM_max_table=100)
CPU times: user 200 ms, sys: 0 ns, total: 200 ms
Wall time: 555 ms

In [29]: df_result
Out[29]: 
          Name1  Name3  Name4  Name5  Name6  Name7  Name8  Name9  Name10  \
NAME_ABC   33.5   52.0   61.4  161.3  126.9  118.2  200.1   95.0   173.9   
NAME_EFG   59.1   77.6   50.6  150.5  116.1  143.8  225.7  120.6   199.5   
NAME_IJK   93.9  112.3   23.7   97.4   82.7  136.9  244.8  143.8   200.1   

          Name11   ...     Name126  Name127  Name128  Name129  Name130  \
NAME_ABC   151.4   ...        96.3    173.9    151.4    148.4    162.0   
NAME_EFG   177.0   ...       121.9    199.5    177.0    174.0    187.6   
NAME_IJK   170.1   ...       143.8    200.1    170.1    193.1    162.5   

          Name131  Name132  Name133  Name137  Name139  
NAME_ABC    127.6    135.0     88.8     97.3    113.7  
NAME_EFG    116.7    101.9     54.8     86.5    102.9  
NAME_IJK     63.6     71.0    112.7     33.4     49.8  

[3 rows x 105 columns]
```
The result is the same, but would have been computed quicker with an appropriate `--max-table-size` 
and the according `OSRM_max_table` parameter :
```python
In [30]: %time df_result2 = osrm.table_OD(listDest, nameDest,
					  listOrigins, nameOrigins, OSRM_max_table=1000)
CPU times: user 8 ms, sys: 4 ms, total: 12 ms
Wall time: 167 ms

In [31]: from pandas.util.testing import assert_frame_equal

In [32]: assert_frame_equal(df_result, df_result2)

In [33]: df_result.equals(df_result2)
Out[33]: True
```

### nearest

```python
In [22]: import osrm

In [23]: res = osrm.nearest([22.1021271845936,	41.5078687005805])

In [24]: res
Out[24]: {'mapped_coordinate': [41.50787, 22.102127], 'name': 'R1103', 'status': 0}
```

### locate

```python
In [25]: import osrm

In [26]: res = osrm.locate([20.9574645547597, 41.5286973392856])

In [27]: res
Out[27]: {'mapped_coordinate': [41.528706, 20.957441], 'status': 0}

```
