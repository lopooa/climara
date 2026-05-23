"""
Linear interpolation functions.

NCL reference
-------------
Wrapper source:
- ni/src/lib/nfp/linint2W.c

Related Fortran routines include:
- linint1
- linint2

Public NCL-style functions:
- linint1
- linint1_n
- linint2
- linint2_points
- area_hi2lores
"""


def linint1(xi, fi, xo, **kwargs):
    """One-dimensional linear interpolation."""
    raise NotImplementedError("linint1 is not implemented yet.")


def linint1_n(xi, fi, xo, dim=None, **kwargs):
    """One-dimensional linear interpolation along a selected dimension."""
    return linint1(xi, fi, xo, dim=dim, **kwargs)


def linint2(data, src_lon=None, src_lat=None, dst_lon=None, dst_lat=None, **kwargs):
    """Two-dimensional linear interpolation."""
    raise NotImplementedError("linint2 is not implemented yet.")


def linint2_points(data, src_lon=None, src_lat=None, points_lon=None, points_lat=None, **kwargs):
    """Interpolate gridded data to point locations."""
    raise NotImplementedError("linint2_points is not implemented yet.")


def area_hi2lores(data, target, **kwargs):
    """Area-weighted high-to-low resolution remapping."""
    raise NotImplementedError("area_hi2lores is not implemented yet.")
