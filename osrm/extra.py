# -*- coding: utf-8 -*-
"""
@author: mthh
"""
import numpy as np
from shapely.geometry import MultiPolygon, Polygon, Point
from geopandas import GeoDataFrame, pd
import matplotlib.pyplot as plt
from matplotlib.mlab import griddata
from math import ceil

from .core import table

def countour_poly(gdf, field_name, levels='auto'):
    """
    Parameters
    ----------
    gdf: :py:obj:`geopandas.GeoDataFrame`
        The GeoDataFrame containing points and associated values.
    field_name: String
        The name of the column of *gdf* containing the value to use.
    levels: int, or list of int, default 'auto'
        The number of levels to use for contour polygons if levels is an
        integer (exemple: levels=8).
        Or
        Limits of the class to use in a list/tuple (like [0, 200, 400, 800])
        Defaults is set to 15 class.
    Return
    ------
    collection_polygons: matplotlib.contour.QuadContourSet
        The shape of the computed polygons.
    levels: list of integers
    """
#    if plt.isinteractive():
#        plt.ioff()
#        switched = True
#    else:
#        switched = False

    # Dont take point without value :
    gdf = gdf.iloc[gdf[field_name].nonzero()[0]][:]
    # Try to avoid unvalid geom :
    if len(gdf.geometry.valid()) != len(gdf):
        # Invalid geoms have been encountered :
        valid_geoms = gdf.geometry.valid()
        valid_geoms = valid_geoms.reset_index()
        valid_geoms['idx'] = valid_geoms['index']
        del valid_geoms['index']
        valid_geoms[field_name] = \
            valid_geoms.idx.apply(lambda x: gdf[field_name][x])
    else:
        valid_geoms = gdf[['geometry', field_name]][:]

    # Always in order to avoid invalid value which will cause the fail
    # of the griddata function :
    try: # Normal way (fails if a non valid geom is encountered)
        x = np.array([geom.coords.xy[0][0] for geom in valid_geoms.geometry])
        y = np.array([geom.coords.xy[1][0] for geom in valid_geoms.geometry])
        z = valid_geoms[field_name].values
    except:  # Taking the long way to load the value... :
        x = np.array([])
        y = np.array([])
        z = np.array([], dtype=float)
        for idx, geom, val in gdf[['geometry', field_name]].itertuples():
            try:
                x = np.append(x, geom.coords.xy[0][0])
                y = np.append(y, geom.coords.xy[1][0])
                z = np.append(z, val)
            except Exception as err:
                print(err)

#    # compute min and max and values :
    minx = np.nanmin(x)
    miny = np.nanmin(y)
    maxx = np.nanmax(x)
    maxy = np.nanmax(y)

    # Assuming we want a square grid for the interpolation
    xi = np.linspace(minx, maxx, 200)
    yi = np.linspace(miny, maxy, 200)
    zi = griddata(x, y, z, xi, yi, interp='linear')
    if isinstance(levels, (str, bytes)) and 'auto' in levels:
        jmp = int(round((np.nanmax(z) - np.nanmin(z)) / 15))
        levels = [nb for nb in range(0, int(round(np.nanmax(z))+1)+jmp, jmp)]

    collec_poly = plt.contourf(
        xi, yi, zi, levels, cmap=plt.cm.rainbow,
        vmax=abs(zi).max(), vmin=-abs(zi).max(), alpha=0.35
        )

    if isinstance(levels, int):
        jmp = int(round((np.nanmax(z) - np.nanmin(z)) / levels))
        levels = [nb for nb in range(0, int(round(np.nanmax(z))+1)+jmp, jmp)]
#    if switched:
#        plt.ion()
    return collec_poly, levels


def isopoly_to_gdf(collec_poly, field_name=None, levels=None):
    polygons, data = [], []

    for i, polygon in enumerate(collec_poly.collections):
        mpoly = []
        for path in polygon.get_paths():
            path.should_simplify = False
            poly = path.to_polygons()
            exterior, holes = [], []
            if len(poly) > 0 and len(poly[0]) > 3:
                exterior = poly[0]
                if len(poly) > 1:  # There's some holes
                    holes = [h for h in poly[1:] if len(h) > 3]
            mpoly.append(Polygon(exterior, holes))
        if len(mpoly) > 1:
            mpoly = MultiPolygon(mpoly)
            polygons.append(mpoly)
            if levels:
                data.append(levels[i])
        elif len(poly) == 1:
            polygons.append(mpoly[0])
            if levels:
                data.append(levels[i])

    if levels and isinstance(levels, (list, tuple)) \
            and len(data) == len(polygons):
        if not field_name:
            field_name = 'value'
        return GeoDataFrame(geometry=polygons,
                                data=data, columns=[field_name])
    else:
        return GeoDataFrame(geometry=polygons)

def make_grid(gdf, height):
    """
    Return a grid, based on the shape of *gdf* and on a *height* value (in
    units of *gdf*). If cut=False, the grid will not be intersected with *gdf*
    (i.e it makes a grid on the bounding-box of *gdf*).
    Parameters
    ----------
    gdf: GeoDataFrame
        The collection of polygons to be covered by the grid.
    height: Integer
        The dimension (will be used as height and width) of the ceils to create,
        in units of *gdf*.
    cut: Boolean, default True
        Cut the grid to fit the shape of *gdf* (ceil partially covering it will
        be truncated). If False, the returned grid will fit the bounding box
        of *gdf*.
    Returns
    -------
    grid: GeoDataFrame
        A collection of polygons.
    """
    xmin, ymin = [i.min() for i in gdf.bounds.T.values[:2]]
    xmax, ymax = [i.max() for i in gdf.bounds.T.values[2:]]
    rows = ceil((ymax-ymin) / height)
    cols = ceil((xmax-xmin) / height)

    x_left_origin = xmin
    x_right_origin = xmin + height
    y_top_origin = ymax
    y_bottom_origin = ymax - height

    res_geoms = []
    for countcols in range(cols):
        y_top = y_top_origin
        y_bottom = y_bottom_origin
        for countrows in range(rows):
            res_geoms.append((
                (x_left_origin, y_top), (x_right_origin, y_top),
                (x_right_origin, y_bottom), (x_left_origin, y_bottom)
                ))
            y_top = y_top - height
            y_bottom = y_bottom - height
        x_left_origin = x_left_origin + height
        x_right_origin = x_right_origin + height
    return GeoDataFrame(
        index=[i for i in range(len(res_geoms))],
        geometry=pd.Series(res_geoms).apply(lambda x: Polygon(x)),
        crs=gdf.crs
        )


def access_isocrone(point_origin, precision=0.03, size=0.4, n_breaks=8,
                    host='http://localhost:5000', profile="driving", version="v1"):
    """
    Parameters
    ----------
    point_origin: 2-floats tuple
        The coordinates of the center point to use as (x, y).
    precision: float

    size: float
        Search radius (in degree).
    host: string, default 'http://localhost:5000'
        OSRM instance URL (no final backslash)
    Return
    ------
    gdf_poly: GeoDataFrame
        The shape of the computed accessibility polygons.
    grid: GeoDataFrame
        The location and time of each used point.
    new_point_origin: 2-floats tuple
        The coord (x, y) of the origin point (could be the same as provided
        or have been slightly moved to be on a road).
    """
    gdf = GeoDataFrame(geometry=[Point(point_origin).buffer(size)])
    grid = make_grid(gdf, precision)
    if len(grid) > 5000:
        print('Too large query requiered - Reduce precision or size')
        return -1
    coords_grid = \
        [(i.coords.xy[0][0], i.coords.xy[1][0]) for i in grid.geometry.centroid]
    req_conf = {"server": host, "profile": profile, "version": version}
    times, new_pt_origin, pts_dest = \
        table([point_origin], coords_grid, url_config=req_conf)
    times = (times[0] / 60.0).round(2)  # Round values in minutes
    geoms, values = [], []
    for time, coord in zip(times, pts_dest):
        if time:
            geoms.append(Point(coord))
            values.append(time)
    grid = GeoDataFrame(geometry=geoms, data=values, columns=['time'])
    del geoms
    del values
    collec_poly, levels = countour_poly(grid, 'time', levels=n_breaks)
    gdf_poly = isopoly_to_gdf(collec_poly, 'time', levels)
    return gdf_poly, new_pt_origin