# -*- coding: utf-8 -*-
"""
@author: mthh
"""
from .core import table
from . import RequestConfig
import numpy as np
from math import ceil
from shapely.geometry import MultiPolygon, Polygon, Point
from geopandas import GeoDataFrame, pd
import matplotlib
if not matplotlib.get_backend():
    matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.mlab import griddata


def contour_poly(gdf, field_name, levels='auto'):
    """
    Parameters
    ----------
    gdf: :py:obj:`geopandas.GeoDataFrame`
        The GeoDataFrame containing points and associated values.
    field_name: String
        The name of the column of *gdf* containing the value to use.
    levels: int,
        The number of levels to use for contour polygons if levels is an
        integer (exemple: levels=8).
    Return
    ------
    collection_polygons: matplotlib.contour.QuadContourSet
        The shape of the computed polygons.
    levels: list of integers
    """
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

    interval_time = int(round((np.nanmax(z) - np.nanmin(z)) / levels))
    nb_inter = int(round(np.nanmax(z) / interval_time))
#    jmp = int(round((np.nanmax(z) - np.nanmin(z)) / 15))
#    levels = [nb for nb in range(0, int(round(np.nanmax(z))+1)+jmp, jmp)]
    levels = tuple([nb for nb in range(0, int(
        np.nanmax(z) + 1) + interval_time, interval_time)][:nb_inter+1])

    collec_poly = plt.contourf(
        xi, yi, zi, levels, cmap=plt.cm.rainbow,
        vmax=abs(zi).max(), vmin=-abs(zi).max(), alpha=0.35
        )

    return collec_poly, levels


def isopoly_to_gdf(collec_poly, field_name, levels):
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
        elif len(mpoly) == 1:
            polygons.append(mpoly[0])
            if levels:
                data.append(levels[i])

    if len(data) == len(polygons):
        return GeoDataFrame(geometry=polygons,
                            data=data,
                            columns=[field_name])
    else:
        return GeoDataFrame(geometry=polygons)


def make_grid(gdf, height):
    """
    Return a grid, based on the shape of *gdf* and on a *height* value (in
    units of *gdf*).
    Parameters
    ----------
    gdf: GeoDataFrame
        The collection of polygons to be covered by the grid.
    height: Integer
        The size (will be used as height and width) of the ceils to create,
        in units of *gdf*.

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
    for countcols in range(int(cols)):
        y_top = y_top_origin
        y_bottom = y_bottom_origin
        for countrows in range(int(rows)):
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


def access_isocrone(point_origin, precision=0.09, size=0.4, n_breaks=8,
                    url_config=RequestConfig):
    """
    Parameters
    ----------
    point_origin: 2-floats tuple
        The coordinates of the center point to use as (x, y).
    precision: float

    size: float
        Search radius (in degree).
    url_config:


    Return
    ------
    gdf_poly: GeoDataFrame
        The shape of the computed accessibility polygons.
    new_point_origin: 2-floats tuple
        The coord (x, y) of the origin point (could be the same as provided
        or have been slightly moved to be on a road).
    """
    gdf = GeoDataFrame(geometry=[Point(point_origin).buffer(size)])
    grid = make_grid(gdf, precision)
    if len(grid) > 3500:
        print('Too large query requiered - Reduce precision or size')
        return -1
    coords_grid = \
        [(i.coords.xy[0][0], i.coords.xy[1][0]) for i in grid.geometry.centroid]
    times, new_pt_origin, pts_dest = \
        table([point_origin], coords_grid, url_config)
    times = (times[0] / 60.0).round(2)  # Round values in minutes
    geoms, values = [], []
    for time, coord in zip(times, pts_dest):
        if time:
            geoms.append(Point(coord))
            values.append(time)
    grid = GeoDataFrame(geometry=geoms, data=values, columns=['time'])
    del geoms
    del values
    collec_poly, levels = contour_poly(grid, 'time', levels=n_breaks)
    gdf_poly = isopoly_to_gdf(collec_poly, 'time', levels)
    return gdf_poly, new_pt_origin
