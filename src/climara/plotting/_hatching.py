from __future__ import annotations

import numpy as np
import cartopy.crs as ccrs
from cartopy.util import add_cyclic_point


_HATCH_MAP = {
    0: "",
    1: "/",
    2: "\\",
    3: "|",
    4: "-",
    5: "+",
    6: "x",
    7: "o",
    8: ".",
    9: "*",
}


def _guess_coord_name(data, candidates):
    for name in candidates:
        if hasattr(data, "coords") and name in data.coords:
            return name

    for name in candidates:
        if hasattr(data, "dims") and name in data.dims:
            return name

    return None


def _to_numpy_data_lon_lat(data, lon=None, lat=None):
    if hasattr(data, "coords") and hasattr(data, "dims"):
        if lon is None:
            lon_name = _guess_coord_name(data, ["lon", "longitude", "x"])

            if lon_name is not None:
                lon = data[lon_name].values

        if lat is None:
            lat_name = _guess_coord_name(data, ["lat", "latitude", "y"])

            if lat_name is not None:
                lat = data[lat_name].values

        arr = data.values
    else:
        arr = np.asarray(data)

    if lon is None:
        lon = np.arange(arr.shape[-1])

    if lat is None:
        lat = np.arange(arr.shape[-2])

    return arr, np.asarray(lon), np.asarray(lat)


def _maybe_add_cyclic(arr, lon, add_cyclic=True):
    if not add_cyclic:
        return arr, lon

    if lon.ndim != 1:
        return arr, lon

    if arr.shape[-1] != lon.size:
        return arr, lon

    if lon.size < 2:
        return arr, lon

    span = abs(float(lon[-1] - lon[0]))

    if span >= 359.0:
        return arr, lon

    arr_cyclic, lon_cyclic = add_cyclic_point(arr, coord=lon, axis=-1)

    return arr_cyclic, lon_cyclic


def _style_contour_set(cs, color="black", linewidth=0.0, alpha=1.0):
    if hasattr(cs, "collections"):
        for coll in cs.collections:
            coll.set_facecolor("none")
            coll.set_edgecolor(color)
            coll.set_linewidth(linewidth)
            coll.set_alpha(alpha)
        return cs

    if hasattr(cs, "set_facecolor"):
        cs.set_facecolor("none")

    if hasattr(cs, "set_edgecolor"):
        cs.set_edgecolor(color)

    if hasattr(cs, "set_linewidth"):
        cs.set_linewidth(linewidth)

    if hasattr(cs, "set_alpha"):
        cs.set_alpha(alpha)

    return cs


def _resolve_hatch_pattern(res):
    pattern = res.get("gsnHatchPattern", res.get("gsnShadeFillPattern", "///"))

    if isinstance(pattern, int):
        pattern = _HATCH_MAP.get(pattern, "///")

    density = int(res.get("gsnHatchDensityF", 1))

    if density < 1:
        density = 1

    if pattern in ["", None]:
        return ""

    return str(pattern) * density


def add_hatching(ax, mask, lon=None, lat=None, res=None):
    """
    Add NCL-style hatching overlay.

    Supported resources
    -------------------
    gsnHatchPattern
    gsnHatchDensityF
    gsnHatchColor
    gsnHatchAlphaF
    gsnHatchLineThicknessF
    gsnAddCyclic
    """
    if res is None:
        res = {}

    arr, lon, lat = _to_numpy_data_lon_lat(mask, lon=lon, lat=lat)
    arr = np.where(arr, 1.0, 0.0)

    arr, lon = _maybe_add_cyclic(
        arr,
        lon,
        add_cyclic=bool(res.get("gsnAddCyclic", True)),
    )

    pattern = _resolve_hatch_pattern(res)

    cs = ax.contourf(
        lon,
        lat,
        arr,
        levels=[0.5, 1.5],
        colors="none",
        hatches=[pattern],
        transform=ccrs.PlateCarree(),
        zorder=float(res.get("gsnHatchZOrder", 8)),
    )

    _style_contour_set(
        cs,
        color=res.get("gsnHatchColor", "black"),
        linewidth=float(res.get("gsnHatchLineThicknessF", 0.0)),
        alpha=float(res.get("gsnHatchAlphaF", 1.0)),
    )

    return cs


def add_stipple(ax, mask, lon=None, lat=None, res=None):
    """
    Add NCL-style stippling overlay using scatter markers.

    Supported resources
    -------------------
    gsnStippleMarker
    gsnStippleColor
    gsnStippleSizeF
    gsnStippleAlphaF
    gsnStippleStride
    """
    if res is None:
        res = {}

    arr, lon, lat = _to_numpy_data_lon_lat(mask, lon=lon, lat=lat)
    arr = np.asarray(arr).astype(bool)

    stride = int(res.get("gsnStippleStride", 1))

    if stride < 1:
        stride = 1

    lon2d, lat2d = np.meshgrid(lon, lat)

    arr = arr[::stride, ::stride]
    lon2d = lon2d[::stride, ::stride]
    lat2d = lat2d[::stride, ::stride]

    x = lon2d[arr]
    y = lat2d[arr]

    sc = ax.scatter(
        x,
        y,
        s=float(res.get("gsnStippleSizeF", 5.0)),
        marker=res.get("gsnStippleMarker", "."),
        color=res.get("gsnStippleColor", "black"),
        alpha=float(res.get("gsnStippleAlphaF", 0.8)),
        linewidths=0,
        transform=ccrs.PlateCarree(),
        zorder=float(res.get("gsnStippleZOrder", 9)),
    )

    return sc
