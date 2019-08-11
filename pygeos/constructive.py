from enum import IntEnum
import numpy as np
from .geometry import Empty, Geometry  # NOQA
from . import ufuncs


__all__ = [
    "BufferCapStyles",
    "BufferJoinStyles",
    "boundary",
    "buffer",
    "centroid",
    "convex_hull",
    "delaunay_triangles",
    "envelope",
    "extract_unique_points",
    "point_on_surface",
    "simplify",
    "snap",
    "voronoi_polygons",
]


class BufferCapStyles(IntEnum):
    ROUND = 1
    FLAT = 2
    SQUARE = 3


class BufferJoinStyles(IntEnum):
    ROUND = 1
    MITRE = 2
    BEVEL = 3


def boundary(geometry, **kwargs):
    """Returns the topological boundary of a geometry.

    Parameters
    ----------
    geometry : Geometry or array_like
        This function will raise for non-empty geometrycollections.

    Examples
    --------
    >>> boundary(Geometry("POINT (0 0)"))
    <pygeos.Empty>
    >>> boundary(Geometry("LINESTRING(0 0, 1 1, 1 2)"))
    <pygeos.Geometry MULTIPOINT (0 0, 1 2)>
    >>> boundary(Geometry("LINEARRING (0 0, 1 0, 1 1, 0 1, 0 0)"))
    <pygeos.Empty>
    >>> boundary(Geometry("POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))"))
    <pygeos.Geometry LINESTRING (0 0, 1 0, 1 1, 0 1, 0 0)>
    >>> boundary(Geometry("MULTIPOINT (0 0, 1 2)"))
    <pygeos.Empty>
    >>> boundary(Geometry("MULTILINESTRING ((0 0, 1 1), (2 2, 3 3))"))
    <pygeos.Geometry MULTIPOINT (0 0, 1 1, 2 2, 3 3)>
    >>> boundary(Empty)
    <pygeos.Empty>
    """
    return ufuncs.boundary(geometry, **kwargs)


def buffer(
    geometry,
    radius,
    quadsegs=8,
    cap_style="round",
    join_style="round",
    mitre_limit=5.0,
    single_sided=False,
):
    """
    Computes the buffer of a geometry for positive and negative buffer radius.

    The buffer of a geometry is defined as the Minkowski sum (or difference,
    for negative width) of the geometry with a circle with radius equal to the
    absolute value of the buffer radius.

    The buffer operation always returns a polygonal result. The negative
    or zero-distance buffer of lines and points is always empty.

    Since true buffer curves may contain circular arcs, computed buffer
    polygons can only be approximations to the true geometry. The user
    can control the accuracy of the curve approximation by specifying
    the number of linear segments with which to approximate a curve.

    Parameters
    ----------
    geometry : Geometry or array_like
    width : float or array_like
    quadsegs : int
    cap_style : {'round', 'flat', 'square'}
    join_style : {'round', 'mitre', 'bevel'}
    mitre_limit : float
    single_sided : bool

    Examples
    --------
    >>> buffer(Geometry("POINT (10 10)"), 2, quadsegs=1)
    <pygeos.Geometry POLYGON ((12 10, 10 8, 8 10, 10 12, 12 10))>
    >>> buffer(Geometry("POINT (10 10)"), 2, quadsegs=2)
    <pygeos.Geometry POLYGON ((12 10, 11.4 8.59, 10 8, 8.59 8.59, 8 10, 8.59 11.4, 10 12, 11.4 11.4, 12 10))>
    >>> buffer(Geometry("POINT (10 10)"), -2, quadsegs=1)
    <pygeos.Empty>
    >>> line = Geometry("LINESTRING (10 10, 20 10)")
    >>> buffer(line, 2, cap_style="square")
    <pygeos.Geometry POLYGON ((20 12, 22 12, 22 8, 10 8, 8 8, 8 12, 20 12))>
    >>> buffer(line, 2, cap_style="flat")
    <pygeos.Geometry POLYGON ((20 12, 20 8, 10 8, 10 12, 20 12))>
    >>> buffer(line, 2, single_sided=True, cap_style="flat")
    <pygeos.Geometry POLYGON ((20 10, 10 10, 10 12, 20 12, 20 10))>
    >>> line2 = Geometry("LINESTRING (10 10, 20 10, 20 20)")
    >>> buffer(line2, 2, cap_style="flat", join_style="bevel")
    <pygeos.Geometry POLYGON ((18 12, 18 20, 22 20, 22 10, 20 8, 10 8, 10 12, 18 12))>
    >>> buffer(line2, 2, cap_style="flat", join_style="mitre")
    <pygeos.Geometry POLYGON ((18 12, 18 20, 22 20, 22 8, 10 8, 10 12, 18 12))>
    >>> buffer(line2, 2, cap_style="flat", join_style="mitre", mitre_limit=1)
    <pygeos.Geometry POLYGON ((18 12, 18 20, 22 20, 21.8 9, 21 8.17, 10 8, 10 12, 18 12))>
    >>> square = Geometry("POLYGON((0 0, 10 0, 10 10, 0 10, 0 0))")
    >>> buffer(square, 2, join_style="mitre")
    <pygeos.Geometry POLYGON ((-2 -2, -2 12, 12 12, 12 -2, -2 -2))>
    >>> buffer(square, -2, join_style="mitre")
    <pygeos.Geometry POLYGON ((2 2, 2 8, 8 8, 8 2, 2 2))>
    >>> buffer(square, -5, join_style="mitre")
    <pygeos.Empty>
    >>> buffer(Empty, 1)
    <pygeos.Empty>
    """
    if isinstance(cap_style, str):
        cap_style = BufferCapStyles[cap_style.upper()].value
    if isinstance(join_style, str):
        join_style = BufferJoinStyles[join_style.upper()].value
    if not np.isscalar(quadsegs):
        raise TypeError("quadsegs only accepts scalar values")
    if not np.isscalar(cap_style):
        raise TypeError("cap_style only accepts scalar values")
    if not np.isscalar(join_style):
        raise TypeError("join_style only accepts scalar values")
    if not np.isscalar(mitre_limit):
        raise TypeError("mitre_limit only accepts scalar values")
    if not np.isscalar(single_sided):
        raise TypeError("single_sided only accepts scalar values")
    return ufuncs.buffer(
        geometry,
        radius,
        np.intc(quadsegs),
        np.intc(cap_style),
        np.intc(join_style),
        mitre_limit,
        np.bool(single_sided),
    )


def centroid(geometries):
    """Computes the geometric center (center-of-mass) of a geometry.

    For multipoints this is computed as the mean of the input coordinates.
    For multilinestrings the centroid is weighted by the length of each
    line segment. For multipolygons the centroid is weighted by the area of
    each polygon.

    Parameters
    ----------
    geometry : Geometry or array_like

    Examples
    --------
    >>> centroid(Geometry("POLYGON ((0 0, 10 0, 10 10, 0 10, 0 0))"))
    <pygeos.Geometry POINT (5 5)>
    >>> centroid(Geometry("LINESTRING (0 0, 2 2, 10 10)"))
    <pygeos.Geometry POINT (5 5)>
    >>> centroid(Geometry("MULTIPOINT (0 0, 10 10)"))
    <pygeos.Geometry POINT (5 5)>
    >>> centroid(Empty)
    <pygeos.Empty>
    """
    return ufuncs.centroid(geometries)


def convex_hull(geometries):
    return ufuncs.convex_hull(geometries)


def delaunay_triangles(geometry, tolerance=0.0, only_edges=False):
    return ufuncs.delaunay_triangles(geometry, tolerance, only_edges)


def envelope(geometries):
    return ufuncs.envelope(geometries)


def extract_unique_points(geometries):
    return ufuncs.extract_unique_points(geometries)


def point_on_surface(geometries):
    return ufuncs.point_on_surface(geometries)


def simplify(geometries, tolerance, preserve_topology=False):
    if preserve_topology:
        return ufuncs.simplify_preserve_topology(geometries, tolerance)
    else:
        return ufuncs.simplify(geometries, tolerance)


def snap(geometries, reference, tolerance):
    return ufuncs.snap(geometries, reference, tolerance)


def voronoi_polygons(geometry, envelope=None, tolerance=0.0, only_edges=False):
    return ufuncs.voronoi_polygons(geometry, envelope, tolerance, only_edges)
