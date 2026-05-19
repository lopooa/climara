from __future__ import annotations

import numpy as np
import cartopy.crs as ccrs

from ._coords import infer_lon_lat_2d, to_numpy_lon_lat
from ._resources import split_resources


def overlay_vector(ax, u, v, lon=None, lat=None, res=None):
    """
    Overlay a vector/quiver field with NCL-style vc resources.
    """
    groups = split_resources(res)
    vcres = groups["vector"]

    uarr, lon, lat = to_numpy_lon_lat(u, lon=lon, lat=lat)

    if hasattr(v, "values"):
        varr = v.values
    else:
        varr = np.asarray(v)

    lon2d, lat2d = infer_lon_lat_2d(lon, lat)

    stride = int(vcres.get("vcStride", vcres.get("vcMinDistanceF", 1)))
    stride = max(stride, 1)

    q = ax.quiver(
        lon2d[::stride, ::stride],
        lat2d[::stride, ::stride],
        uarr[::stride, ::stride],
        varr[::stride, ::stride],
        color=vcres.get("vcGlyphStyleColor", vcres.get("vcVectorColor", "black")),
        scale=vcres.get("vcRefMagnitudeF", None),
        width=float(vcres.get("vcLineArrowThicknessF", 0.0025)),
        transform=ccrs.PlateCarree() if hasattr(ax, "projection") else None,
        zorder=float(vcres.get("vcZOrder", 25)),
    )

    if "vcRefAnnoString1" in vcres:
        ax.quiverkey(
            q,
            X=float(vcres.get("vcRefAnnoXF", 0.9)),
            Y=float(vcres.get("vcRefAnnoYF", -0.08)),
            U=float(vcres.get("vcRefMagnitudeF", 1.0)),
            label=vcres["vcRefAnnoString1"],
            labelpos="E",
        )

    return q
