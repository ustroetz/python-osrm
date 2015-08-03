import requests
from polyline.codec import PolylineCodec
from osgeo import ogr
import sys


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
                geom_decoded = [[point[0]/10.0, point[1]/10.0] for point in PolylineCodec().decode(geom_encoded)]
                r_json["matchings"][i]["geometry"] = geom_decoded
        else:
            print('No matching geometry to decode')
    return r_json


def simple_viaroute(coord_origine, coord_dest, alt=False,
                    output='raw', host='http://localhost:5000'):
    """
    Params:
    coord_origine: list of two float
        [x ,y] where x is longitude and y is latitude
    coord_dest: list of two float
        [x ,y] where x is longitude and y is latitude
    alt: boolean, default=False
        Query (and resolve geometry if asked) for alternatives routes
    output: str, default= 'wkt'
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

    url = '{}/viaroute?loc={}&loc={}&instructions=false&alt=false'.format(host,
                               str(coord_origine[1])+','+str(coord_origine[0]),
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
            ma_ligne = ogr.Geometry(ogr.wkbLineString)
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


def table(list_coords, list_ids, input_geom='coord_list', output='pandas',
          host='http://localhost:5000'):
    """
    Params :
        list_coords: list
            A list of coord as [x, y]
            like list_coords = [[21.3224, 45.2358],
                                [21.3856, 42.0094],
                                [20.9574, 41.5286]] (coords have to be float)
        list_ids: list
            A list of the corresponding unique id
                like list_ids = ['name1',
                                 'name2',
                                 'name3'] (id can be str, int or float)
        host: str, default 'http://localhost:5000'
            Url and port of the OSRM instance (no final bakslash)
        output: str, default 'pandas'
            The type of matrice to return (DataFrame or numpy array)
                'pandas', 'df' or 'DataFrame' for a DataFrame
                'numpy', 'array' or 'np' for a numpy array
    Output:
        - if 'numpy' : a numpy array containing the time in minute
                (or NaN when OSRM encounter an error to compute a route)
        or
        - if 'pandas' : a labeled DataFrame containing the time in minute
                    (or NaN when OSRM encounter an error to compute a route)

        -1 is return in case of any other error (bad 'output' parameter,
            wrong list of coords/ids, unknow host,
            wrong response from the host, etc.)
    """
    from pandas import DataFrame as pdDF
    import numpy as np
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
        print("\nErreur lors du passage de l'URL\n")
        sys.exit(0)

    if 'distance_table' in parsed_json.keys():  # Preparing the result matrix
        mat = np.array(parsed_json['distance_table'])
        mat = mat/(10*60)  # Conversion in minutes
        mat = mat.round(1)
        mat[mat == 3579139.4] = np.NAN  # Flag the errors with NAN
        if output == 1:
            return mat
        elif output == 2:
            df = pdDF(mat, index=list_ids, columns=list_ids)
            return df
    else:
        print('No distance table return by OSRM local instance')
        return -1
