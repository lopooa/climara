from __future__ import annotations

import numpy as np
from cartopy.util import add_cyclic_point

_LON_NAMES = ["lon", "longitude", "x", "X"]
_LAT_NAMES = ["lat", "latitude", "y", "Y"]


def _first_existing_name(obj, names):
    if obj is None:
        return None

    coords = getattr(obj, "coords", {})
    dims = getattr(obj, "dims", ())

    for name in names:
        if name in coords:
            return name

    for name in names:
        if name in dims:
            return name

    return None


def get_lon_lat(data, lon=None, lat=None):
    """
    Get lon/lat coordinates from xarray or user input.
    """
    if hasattr(data, "coords") and hasattr(data, "dims"):
        if lon is None:
            lon_name = _first_existing_name(data, _LON_NAMES)

            if lon_name is not None:
                lon = data[lon_name].values

        if lat is None:
            lat_name = _first_existing_name(data, _LAT_NAMES)

            if lat_name is not None:
                lat = data[lat_name].values

    return lon, lat


def to_numpy_lon_lat(data, lon=None, lat=None):
    """
    Convert data/lon/lat to numpy arrays.
    """
    lon, lat = get_lon_lat(data, lon=lon, lat=lat)

    if hasattr(data, "values"):
        arr = data.values
    else:
        arr = np.asarray(data)

    if arr.ndim != 2:
        raise ValueError(f"Expected 2D data, got shape {arr.shape}")

    if lon is None:
        lon = np.arange(arr.shape[-1])

    if lat is None:
        lat = np.arange(arr.shape[-2])

    lon = np.asarray(lon)
    lat = np.asarray(lat)

    return arr, lon, lat


def infer_lon_lat_2d(lon, lat):
    """
    Return 2D lon/lat arrays for scatter-like overlays.
    """
    lon = np.asarray(lon)
    lat = np.asarray(lat)

    if lon.ndim == 1 and lat.ndim == 1:
        return np.meshgrid(lon, lat)

    return lon, lat


def has_global_cyclic_lon(lon):
    lon = np.asarray(lon)

    if lon.ndim != 1 or lon.size < 2:
        return False

    step = float(np.nanmedian(np.diff(lon)))
    span = float(lon[-1] - lon[0] + step)

    return abs(abs(span) - 360.0) < max(abs(step) * 1.5, 1e-6)


def add_cyclic(data, lon=None, lat=None, axis=-1):
    """
    Add cyclic longitude point to data when lon is 1D.
    """
    arr = np.asarray(data)

    if lon is None:
        return arr, lon, lat

    lon = np.asarray(lon)

    if lon.ndim != 1:
        return arr, lon, lat

    if arr.shape[axis] != lon.size:
        return arr, lon, lat

    if has_global_cyclic_lon(lon):
        return arr, lon, lat

    arr_cyc, lon_cyc = add_cyclic_point(arr, coord=lon, axis=axis)

    return arr_cyc, lon_cyc, lat
