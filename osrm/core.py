# -*- coding: utf-8 -*-
import numpy as np
from polyline.codec import PolylineCodec
from pandas import DataFrame
from . import __version__, RequestConfig

try:
    from urllib.request import urlopen
except:
    from urllib2 import urlopen

try:
    from osgeo.ogr import Geometry
except:
    from ogr import Geometry

try:
    import ujson as json
except:
    import json


def _chain(*lists):
    for li in lists:
        for elem in li:
            yield elem

def check_host(host):
    """ Helper function to get the hostname in desired format """
    if not ('http' in host and '//' in host) and host[len(host)-1] == '/':
        return ''.join(['http://', host[:len(host)-1]])
    elif not ('http' in host and '//' in host):
        return ''.join(['http://', host])
    elif host[len(host)-1] == '/':
        return host[:len(host)-1]
    else:
        return host

def match(points, steps=False, overview="simplified", geometry="polyline",
          timestamps=None, radius=None, url_config=RequestConfig):
    """
    Function wrapping OSRM 'match' function,
    returning the reponse in JSON
    Params:

    points: list of tuple/list of point
        (x ,y) where x is longitude and y is latitude
    url_config: dict,
        Parameters regarding the host, version and profile to use

    Output:
        The response from the osrm instance, parsed as a dict
    """
    host = check_host(url_config.host)

    url = [
        host, '/match/', url_config.version, '/', url_config.profile, '/',
       ';'.join([','.join([str(coord[0]), str(coord[1])]) for coord in points]),
       "?overview={}&steps={}&geometries={}"
           .format(overview, str(steps).lower(), geometry)
    ]

    if radius:
        url.append(";".join([str(rad) for rad in radius]))
    if timestamps:
        url.append(";".join([str(timestamp) for timestamp in timestamps]))

    r = urlopen("".join(url))
    r_json = json.loads(r.read().decode('utf-8'))
    if not "code" in r_json or not "Ok" in r_json["code"]:
        if 'matchings' in r_json.keys():
            for i, _ in enumerate(r_json['matchings']):
                geom_encoded = r_json["matchings"][i]["geometry"]
                geom_decoded = [[point[1] / 10.0,
                                 point[0] / 10.0] for point
                                in PolylineCodec().decode(geom_encoded)]
                r_json["matchings"][i]["geometry"] = geom_decoded
        else:
            print('No matching geometry to decode')
    return r_json


def decode_geom(encoded_polyline):
    """
    Function decoding an encoded polyline (with 'encoded polyline
    algorithm') and returning an ogr.Geometry object

    Params:

    encoded_polyline: str
        The encoded string to decode
    """
    ma_ligne = Geometry(2)
    lineAddPts = ma_ligne.AddPoint_2D
    for coord in PolylineCodec().decode(encoded_polyline):
        lineAddPts(coord[1], coord[0])
    return ma_ligne


def simple_route(coord_origin, coord_dest, coord_intermediate=None,
                 alternatives=False, steps=False, output="full",
                 geometry='polyline', overview="simplified",
                 url_config=RequestConfig):
    """
    Function wrapping OSRM 'viaroute' function and returning the JSON reponse
    with the route_geometry decoded (in WKT or WKB) if needed.

    Params:

    coord_origin: list/tuple of two floats
        (x ,y) where x is longitude and y is latitude
    coord_dest: list/tuple of two floats
        (x ,y) where x is longitude and y is latitude
    coord_intermediate: list of list/tuple of two floats
        [(x ,y), (x, y), ...] where x is longitude and y is latitude
    alt: boolean, default False
        Query (and resolve geometry if asked) for alternatives routes
    output: str, default 'full'
        Define the type of output (full response or only route(s))
    url_config: dict,
        Parameters regarding the host, version and profile to use

    Output:
    - if 'raw' : the original json returned by OSRM
    - if 'WKT' : the json returned by OSRM with the 'route_geometry' converted
                 in WKT format
    - if 'WKB' : the json returned by OSRM with the 'route_geometry' converted
                 in WKB format
    """
    if geometry.lower() not in ('wkt', 'well-known-text', 'text', 'polyline',
                                'wkb', 'well-known-binary', 'geojson'):
        raise ValueError("Invalid output format")
    else:
        geom_request = "geojson" if "geojson" in geometry.lower() else "polyline"

    host = check_host(url_config.host)

    url = [host, "/route/", url_config.version, "/", url_config.version, "/",
           "{},{}".format(coord_origin[0], coord_origin[1]), ';']

    if coord_intermediate:
        url.append(";".join(
            [','.join([str(i), str(j)]) for i, j in coord_intermediate]))

    url.extend([
        '{},{}'.format(coord_dest[0], coord_dest[1]),
        "?overview={}&steps={}&alternatives={}&geometries={}".format(
         overview, str(steps).lower(), str(alternatives).lower(), geom_request)
        ])

    try:  # Querying the OSRM instance..
        rep = urlopen(''.join(url))
        parsed_json = json.loads(rep.read().decode('utf-8'))

    except Exception as err:
        raise ValueError(
            'Error while contacting OSRM instance : \n{}'.format(err))

    if "Ok" in parsed_json['code']:
        if geometry in ("polyline", "geojson") and output == "full":
            return parsed_json
        elif geometry in ("polyline", "geojson") and output == "routes":
            return parsed_json["routes"]
        else:
            if geometry == "wkb":
                func = Geometry.ExportToWkb
            elif geometry == "wkt":
                func = Geometry.ExportToWkt

            for route in parsed_json["routes"]:
                route["geometry"] = func(decode_geom(route["geometry"]))

        return parsed_json if output == "full" else parsed_json["routes"]

    else:
        raise ValueError(
            'Error - OSRM status : {} \n Full json reponse : {}'.format(
                parsed_json['code'], parsed_json))


def table(coords_src, coords_dest=None, ids_origin=None, ids_dest=None,
          output='np', minutes=False, url_config=RequestConfig):
    """
    Function wrapping OSRM 'table' function in order to get a matrix of
    time distance as a numpy array or as a DataFrame

    Params :

        coords_src: list
            A list of coord as (lat, long) , like :
                 list_coords = [(21.3224, 45.2358),
                                (21.3856, 42.0094),
                                (20.9574, 41.5286)] (coords have to be float)
        coords_dest: list, optionnal, default None
            A list of coord as (lat, long) , like :
                 list_coords = [(21.3224, 45.2358),
                                (21.3856, 42.0094),
                                (20.9574, 41.5286)] (coords have to be float)
    url_config: dict,
        Parameters regarding the host, version and profile to use
    output: str, default 'np'
            The type of durations matrice to return (DataFrame or numpy array)
                'raw' for the (parsed) json response from OSRM
                'pandas', 'df' or 'DataFrame' for a DataFrame
                'numpy', 'array' or 'np' for a numpy array
    Output:
        - 'raw' : Return the raw json response
        - 'numpy' : a numpy array containing the time in minutes, a list of snapped origin coordinates, a list of snapped destination coordinates
        - 'pandas' : a labeled DataFrame containing the time matrix in minutes, a list of snapped origin coordinates, a list of snapped destination coordinates
    """
    if output.lower() in ('numpy', 'array', 'np'):
        output = 1
    elif output.lower() in ('pandas', 'dataframe', 'df'):
        output = 2
    else:
        output = 3

    host = check_host(url_config.host)
    url = ''.join([host, '/table/', url_config.version, '/', url_config.profile, '/'])

    if not coords_dest:
        url = ''.join([
             url,
             ';'.join([','.join([str(coord[0]), str(coord[1])]) for coord in coords_src])
            ])
    else:
        src_end = len(coords_src)
        dest_end = src_end + len(coords_dest)
        url = ''.join([
            url,
            ';'.join([','.join([str(coord[0]), str(coord[1])]) for coord in _chain(coords_src, coords_dest)]),
            '?sources=',
            ';'.join([str(i) for i in range(src_end)]),
            '&destinations=',
            ';'.join([str(j) for j in range(src_end, dest_end)])
            ])

    try:  # Querying the OSRM local instance
        rep = urlopen(url)
        parsed_json = json.loads(rep.read().decode('utf-8'))
    except Exception as err:
        raise ValueError(
            'Error while contacting OSRM instance : \n{}'.format(err))

    if "code" not in parsed_json or "Ok" not in parsed_json["code"]:
        raise ValueError('No distance table return by OSRM instance')

    elif output == 3:
        return parsed_json

    else:
        durations = np.array(parsed_json["durations"], dtype=float)
        new_src_coords = [ft["location"] for ft in parsed_json["sources"]]
        new_dest_coords = None if not coords_dest \
            else [ft["location"] for ft in parsed_json["destinations"]]

        if minutes:  # Conversion in minutes with 2 decimals:
            durations = np.around((durations / 60), 2)
        if output == 2:
            if not ids_origin:
                ids_origin = [i for i in range(len(coords_src))]
            if not ids_dest:
                ids_dest = [i for i in range(len(coords_dest))] if coords_dest \
                    else ids_origin

            durations = DataFrame(durations,
                                  index=ids_origin,
                                  columns=ids_dest,
                                  dtype=float)

        return durations, new_src_coords, new_dest_coords


def nearest(coord, url_config=RequestConfig):
    """
    Useless function wrapping OSRM 'nearest' function,
    returning the reponse in JSON
    Params:

    coord: list/tuple of two floats
        (x ,y) where x is longitude and y is latitude
    url_config: dict,
        Parameters regarding the host, version and profile to use

    Output:
        The response from the osrm instance, parsed as a dict
    """

    host = check_host(url_config.host)
    url = '/'.join(
        [host, 'nearest', url_config.version, url_config.profile,
         str(coord).replace('(', '').replace(')', '').replace(' ', '')]
        )
    try:
        rep = urlopen(url)
        parsed_json = json.loads(rep.read().decode('utf-8'))
        return parsed_json
    except Exception as err:
        raise ValueError(
            'Error while contacting OSRM instance : \n{}'.format(err))


def trip(coords, steps=False, output="full",
         geometry='polyline', overview="simplified",
         url_config=RequestConfig):
    """
    Function wrapping OSRM 'trip' function and returning the JSON reponse
    with the route_geometry decoded (in WKT or WKB) if needed.

    Params:

    coord_origin: list/tuple of two floats
        (x ,y) where x is longitude and y is latitude
    step: bool, default False
    output: str, default 'full'
        Define the type of output (full response or only route(s))
    overview: str, default "simplified"
    url_config: dict,
        Parameters regarding the host, version and profile to use

    Output:
    - if 'only_index' : a dict containing the respectiv index of trips and waypoints
    - if 'raw' : the original json returned by OSRM
    - if 'WKT' : the json returned by OSRM with the 'route_geometry' converted
                 in WKT format
    - if 'WKB' : the json returned by OSRM with the 'route_geometry' converted
                 in WKB format
    """
    if geometry.lower() not in ('wkt', 'well-known-text', 'text', 'polyline',
                                'wkb', 'well-known-binary', 'geojson'):
        raise ValueError("Invalid output format")
    else:
        geom_request = "geojson" if "geojson" in geometry.lower() else "polyline"

    host = check_host(url_config.host)

    url = ''.join([
         host, '/trip/', url_config.version, '/', url_config.profile, '/',
         ';'.join([','.join([str(coord[0]), str(coord[1])]) for coord in coords]),
         '?steps={}'.format(str(steps).lower()),
         '&geometries={}'.format(geom_request),
         '&overview={}'.format(overview)
         ])

    try:  # Querying the OSRM instance..
        rep = urlopen(url)
        parsed_json = json.loads(rep.read().decode('utf-8'))

    except Exception as err:
        raise ValueError(
            'Error while contacting OSRM instance : \n{}'.format(err))

    if "Ok" in parsed_json['code']:
        if "only_index" in output:
            return [
                {"waypoint": i["waypoint_index"], "trip": i["trips_index"]}
                for i in parsed_json['waypoints']
                ]
        if geometry in ("polyline", "geojson") and output == "full":
            return parsed_json
        elif geometry in ("polyline", "geojson") and output == "trip":
            return parsed_json["trips"]
        else:
            func = Geometry.ExportToWkb if geometry == "wkb" else Geometry.ExportToWkt

            for trip_route in parsed_json["trips"]:
                trip_route["geometry"] = func(decode_geom(trip_route["geometry"]))

        return parsed_json if output == "full" else parsed_json["routes"]

    else:
        raise ValueError(
            'Error - OSRM status : {} \n Full json reponse : {}'
            .format(parsed_json['code'], parsed_json))
