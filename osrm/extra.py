# -*- coding: utf-8 -*-
"""
@author: mthh
"""
from .core import table
from . import RequestConfig, Point as _Point
import numpy as np
from shapely.geometry import MultiPolygon, Polygon, Point
from geopandas import GeoDataFrame, pd
import matplotlib
if not matplotlib.get_backend():
    matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.mlab import griddata


def contour_poly(gdf, field_name, n_class):
    """
    Interpolate the time values (stored in the column `field_name`)
    from the points contained in `gdf` and compute the contour polygons
    in `n_class`.

    Parameters
    ----------
    gdf : :py:obj:`geopandas.GeoDataFrame`
        The GeoDataFrame containing points and associated values.
    field_name : str
        The name of the column of *gdf* containing the value to use.
    n_class : int
        The number of class to use for contour polygons if levels is an
        integer (exemple: levels=8).

    Returns
    -------
    collection_polygons : :py:obj:matplotlib.contour.QuadContourSet
        The shape of the computed polygons.
    levels : list of ints/floats
        The levels actually used when making the contours, excluding
        the minimum (should be a list of `n_class` values).
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
    try:  # Normal way (fails if a non valid geom is encountered)
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

    interval_time = int(round(np.nanmax(z) / n_class))
    nb_inter = n_class + 1
#    jmp = int(round((np.nanmax(z) - np.nanmin(z)) / 15))
#    levels = [nb for nb in range(0, int(round(np.nanmax(z))+1)+jmp, jmp)]
    levels = tuple([nb for nb in range(0, int(
        np.nanmax(z) + 1) + interval_time, interval_time)][:nb_inter+1])

    collec_poly = plt.contourf(
        xi, yi, zi, levels, cmap=plt.cm.rainbow,
        vmax=abs(zi).max(), vmin=-abs(zi).max(), alpha=0.35
        )

    return collec_poly, levels[1:]


def isopoly_to_gdf(collec_poly, field_name, levels):
    """
    Transform a collection of matplotlib polygons (:py:obj:`QuadContourSet`)
    to a :py:obj:`GeoDataFrame` with a columns (`field_name`) filled by the
    values contained in `levels`.

    Parameters
    ----------
    collec_poly : :py:obj:matplotlib.contour.QuadContourSet
        The previously retrieved collections of contour polygons.
    field_name : str
        The name of the column to create which will contain values from `levels`.
    levels : list of ints/floats
        The values to be used when creating the `GeoDataFrame` of polygons,
        likely the values corresponding to the bins values
        used to create the polygons in the contourf function.

    Returns
    -------
    gdf_polygons : :py:obj:`GeoDataFrame`
        The contour polygons as a GeoDataFrame, with a column filled
        with the corresponding levels.
    """
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


def make_grid(gdf, nb_points):
    """
    Return a grid, based on the shape of *gdf* and on a *height* value (in
    units of *gdf*).

    Parameters
    ----------
    gdf : GeoDataFrame
        The collection of polygons to be covered by the grid.
    nb_points : int
        The number of expected points of the grid.

    Returns
    -------
    grid : GeoDataFrame
        A collection of polygons.
    """
    xmin, ymin, xmax, ymax = gdf.total_bounds
    rows = int(nb_points**0.5)
    cols = int(nb_points**0.5)
    height = (ymax-ymin) / rows
    width = (xmax-xmin) / cols
    x_left_origin = xmin
    x_right_origin = xmin + width
    y_top_origin = ymax
    y_bottom_origin = ymax - height

    res_geoms = []
    for countcols in range(cols):
        y_top = y_top_origin
        y_bottom = y_bottom_origin
        for countrows in range(rows):
            res_geoms.append((
                (x_left_origin + x_right_origin) / 2, (y_top + y_bottom) / 2
                ))
            y_top = y_top - height
            y_bottom = y_bottom - height
        x_left_origin = x_left_origin + width
        x_right_origin = x_right_origin + width

    return GeoDataFrame(
        geometry=pd.Series(res_geoms).apply(lambda x: Point(x)),
        crs=gdf.crs
        )


class AccessIsochrone:
    """
    Object allowing to query an OSRM instance for a matrix of distance within
    a defined radius, store the distance (to avoid making the same query again
    when not needed), interpolate time values on a grid and render the contour
    polygons.

    Parameters
    ----------
    point_origin : 2-floats tuple
        The coordinates of the center point to use as (x, y).
    points_grid : int
        The number of points of the underlying grid to use.
    size : float
        Search radius (in degree).
    url_config : osrm.RequestConfig
        The OSRM url to be requested.

    Attributes
    ----------
    center_point : collections.namedtuple
        The coordinates of the point used a center (potentially moved from the
        original point in order to be on the network).
    grid : geopandas.GeoDataFrame
        The point locations retrieved from OSRM (ie. potentially moved
        to be on the routable network).
    times : numpy.ndarray
        The time-distance table retrieved from OSRM.

    Methods
    -------
    render_contour(nb_class)
        Render the contour polygon according to the choosen number of class.
    """

    def __init__(self, point_origin, points_grid=250,
                 size=0.4, url_config=RequestConfig):
        gdf = GeoDataFrame(geometry=[Point(point_origin).buffer(size)])
        grid = make_grid(gdf, points_grid)
        coords_grid = \
            [(i.coords.xy[0][0], i.coords.xy[1][0]) for i in grid.geometry]
        self.times, new_pt_origin, pts_dest = \
            table([point_origin], coords_grid, url_config=url_config)
        self.times = (self.times[0] / 60.0).round(2)  # Round values in minutes
        geoms, values = [], []
        for time, coord in zip(self.times, pts_dest):
            if time:
                geoms.append(Point(coord))
                values.append(time)
        self.grid = GeoDataFrame(geometry=geoms, data=values, columns=['time'])
        self.center_point = _Point(
            latitude=new_pt_origin[0][0], longitude=new_pt_origin[0][1])

    def render_contour(self, n_class):
        """
        Parameters
        ----------
        n_class : int
             The desired number of class.

        Returns
        -------
        gdf_poly : GeoDataFrame
            The shape of the computed accessibility polygons.
        """
        collec_poly, levels = contour_poly(self.grid, 'time', n_class=n_class)
        gdf_poly = isopoly_to_gdf(collec_poly, 'time', levels)
        return gdf_poly
