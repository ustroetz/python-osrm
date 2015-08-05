import requests
from polyline.codec import PolylineCodec
from osgeo.ogr import Geometry
from pandas import DataFrame
import numpy as np
from itertools import islice


def match(points, host='http://localhost:5000', geometry=True,
          gps_precision=-1, matching_beta=-1, decode_polyline=True):
    url = ''.join([host, '/match?'])
    for loc, t in points:
        url += 'loc=' + str(loc[0]) + ',' + str(loc[1]) + '&t=' + str(t) + '&'
    url = url[:-1]
    url = ''.join([url, '&geometry=', str(geometry).lower(), '&gps_precision=',
                   str(gps_precision), '&matching_beta=', str(matching_beta)])
    r = requests.get(url)
    r_json = r.json()
    if decode_polyline:
        if 'matchings' in r_json.keys():
            for i, matching in enumerate(r_json['matchings']):
                geom_encoded = r_json["matchings"][i]["geometry"]
                geom_decoded = [[point[0] / 10.0,
                                 point[1] / 10.0] for point
                                in PolylineCodec().decode(geom_encoded)]
                r_json["matchings"][i]["geometry"] = geom_decoded
        else:
            print('No matching geometry to decode')
    return r_json


def simple_viaroute(coord_origin, coord_dest, alt=False,
                    output='raw', host='http://localhost:5000'):
    """
    Function wrapping OSRM 'viaroute' function and returning the JSON reponse
    with the route_geometry decoded (in WKT or WKB) if needed.
    Params:
    coord_origine: list of two float
        [x ,y] where x is longitude and y is latitude
    coord_dest: list of two float
        [x ,y] where x is longitude and y is latitude
    alt: boolean, default False
        Query (and resolve geometry if asked) for alternatives routes
    output: str, default 'wkt'
        Define the type of output
    host: str, default 'http://localhost:5000'
        Url and port of the OSRM instance (no final bakslash)

    Output:
    - if 'raw' : the original json returned by OSRM
    - if 'WKT' : the json returned by OSRM with the 'route_geometry' converted
                 in WKT format
    - if 'WKB' : the json returned by OSRM with the 'route_geometry' converted
                 in WKB format
    """
    if output.lower() in ('wkt', 'well-known-text', 'text'):
        output = 1
    elif output.lower() in ('wkb', 'well-known-binary'):
        output = 2
    elif 'raw' in output.lower():
        output = 3
    else:
        print('Unknow \'output\' parameter')
        return -1

    url = ('{}/viaroute?loc={}&loc={}&instructions=false',
           '&alt=false').format(host,
                                str(coord_origin[1])+','+str(coord_origin[0]),
                                str(coord_dest[1])+','+str(coord_dest[0]))
    try:  # Querying the OSRM local instance..
        rep = requests.get(url)
        parsed_json = rep.json()
    except:
        print('Error while contacting OSRM instance')
        return -1
    if parsed_json['status'] is not 207:
        if output == 3:
            return parsed_json
        else:
            epa_dec = PolylineCodec().decode(parsed_json['route_geometry'])
            fausse_liste = str(epa_dec)
            ma_ligne = Geometry(2)
            lineAddPts = ma_ligne.AddPoint

            # List of points coordinates :
            lat, long = [], []
            latAppd, longAppd = lat.append, long.append
            valueliste = fausse_liste[1:len(fausse_liste) - 1].split(",")
            for i in valueliste:
                if '(' in i:
                    latAppd(float(i[i.find('(') + 1:])/10)
                elif ')' in i:
                    longAppd(float(i[i.find(' ') + 1:len(i) - 1])/10)
            for coord in zip(long, lat):
                lineAddPts(coord[0], coord[1])
            if output == 2:
                parsed_json['route_geometry'] = ma_ligne.ExportToWkb()
                return parsed_json
            elif output == 1:
                parsed_json['route_geometry'] = ma_ligne.ExportToWkt()
                return parsed_json
    else:
        print('Error - OSRM status : {} \n Full json reponse : {}'.format(
              parsed_json['status'], parsed_json))
        return -1


def table(list_coords, list_ids, output='df',
          host='http://localhost:5000'):
    """
    Function wrapping OSRM 'table' function in order to get a matrix of
    time distance as a numpy array or as a DataFrame
    Params :
        list_coords: list
            A list of coord as [x, y] , like :
                 list_coords = [[21.3224, 45.2358],
                                [21.3856, 42.0094],
                                [20.9574, 41.5286]] (coords have to be float)
        list_ids: list
            A list of the corresponding unique id, like :
                     list_ids = ['name1',
                                 'name2',
                                 'name3'] (id can be str, int or float)
        host: str, default 'http://localhost:5000'
            Url and port of the OSRM instance (no final bakslash)
        output: str, default 'pandas'
            The type of matrice to return (DataFrame or numpy array)
                'pandas', 'df' or 'DataFrame' for a DataFrame
                'numpy', 'array' or 'np' for a numpy array
    Output:
        - 'numpy' : a numpy array containing the time in minutes
                (or NaN when OSRM encounter an error to compute a route)
        or
        - 'pandas' : a labeled DataFrame containing the time matrix in minutes
                (or NaN when OSRM encounter an error to compute a route)

        -1 is return in case of any other error (bad 'output' parameter,
            wrong list of coords/ids, unknow host,
            wrong response from the host, etc.)
    """
    if output.lower() in ('numpy', 'array', 'np'):
        output = 1
    elif output.lower() in ('pandas', 'dataframe', 'df'):
        output = 2
    else:
        print('Unknow output parameter')
        return -1

    query = [host, '/table?loc=']
    for coord, uid in zip(list_coords, list_ids):  # Preparing the query
        tmp = ''.join([str(coord[1]), ',', str(coord[0]), '&loc='])
        query.append(tmp)
    query = (''.join(query))[:-5]
    try:  # Querying the OSRM local instance
        rep = requests.get(query)
        parsed_json = rep.json()
    except:
        print('Error while contacting OSRM instance')
        return -1

    if 'distance_table' in parsed_json.keys():  # Preparing the result matrix
        mat = np.array(parsed_json['distance_table'])
        mat = mat/(10*60)  # Conversion in minutes
        mat = mat.round(1)
        mat[mat == 3579139.4] = np.NaN  # Flag the errors with NaN
        if output == 1:
            return mat
        elif output == 2:
            df = DataFrame(mat, index=list_ids, columns=list_ids, dtype=float)
            return df
    else:
        print('No distance table return by OSRM local instance')
        return -1


def chunk(it, size):
    it = iter(it)
    return iter(lambda: tuple(islice(it, size)), ())


def mat_range2d(l):
    seen = []
    for i in l:
        for j in l:
            if i != j and j+i not in seen:
                seen.append(i+j)
                yield i+j


def table_OD(list_coordsO, list_idsO, list_coordsD, list_idsD,
             OSRM_max_table=100, host='http://localhost:5000'):
    """
    Function wrapping OSRM 'table' function in order to get a matrix of
    time distance between different origins and destinations (N:M)
    Params :
        list_coordsO: list
            A list of coord as [x, y] for the origins, like :
                 list_coords = [[21.3224, 45.2358],
                                [21.3856, 42.0094],
                                [20.9574, 41.5286]] (coords have to be float)
        list_idsO: list
            A list of the corresponding unique id for the origins, like :
                     list_ids = ['name1',
                                 'name2',
                                 'name3'] (id can be str, int or float)
        list_coordsD: list
            A list of coord as [x, y] for the destinations (same kind as the
            origins)
        list_idsD: list
            A list of the corresponding unique id for the destinations (same
            kind as the origins)
        OSRM_max_table: int, default=100
            The --max-table-size defined when lauching osrm-routed (default is
            100). It will be used to clip the request in many 'table' requests
            and reconstruct the matrix.
        host: str, default 'http://localhost:5000'
            Url and port of the OSRM instance (no final bakslash)

    Output:
        A labeled DataFrame containing the time matrix in minutes
            (or NaN when OSRM encounter an error to compute a route)

        -1 or an empty DataFrame is return in case of any other error
            (bad 'output' parameter, wrong list of coords/ids, unknow host,
            wrong response from the host, etc.)
    """
    if list_coordsO == list_coordsD and list_idsO == list_idsD:
        list_coords, list_ids = list_coordsO, list_idsO
    else:
        list_coords = list_coordsO + list_coordsD
        list_ids = list_idsO + list_idsD

    if len(list_coords) > OSRM_max_table:
        gpd_coords = list(chunk(list_coords, OSRM_max_table//2))
        gpd_ids = list(chunk(list_ids, OSRM_max_table//2))
        df = DataFrame(index=list_ids, columns=list_ids, dtype=float)
        for lcoord, lid in zip(mat_range2d(gpd_coords), mat_range2d(gpd_ids)):
            df = df.combine_first(table(list(lcoord), list(lid), host=host))
    else:
        df = table(list_coords, list_ids, host=host)

    try:
        return df[list_idsO].filter(list_idsD, axis=0)
    except:
        return -1
