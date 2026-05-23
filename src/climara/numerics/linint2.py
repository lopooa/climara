"""Two-dimensional interpolation functions.

NCL reference:
- ni/src/lib/nfp/linint2W.c
- ni/src/lib/nfpfort/linint2.f
"""

def linint2(data, src_lon=None, src_lat=None, dst_lon=None, dst_lat=None, **kwargs):
    """Interpolate a field to a new lon-lat grid."""
    raise NotImplementedError("linint2 is not implemented yet.")


def linint2_like(data, target, **kwargs):
    """Interpolate data to the grid of target."""
    raise NotImplementedError("linint2_like is not implemented yet.")


def interpolate_like(data, target, **kwargs):
    """Alias for linint2_like."""
    return linint2_like(data, target, **kwargs)
