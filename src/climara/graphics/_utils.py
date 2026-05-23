from __future__ import annotations

import numpy as np
from cartopy.util import add_cyclic_point


def guess_coord_name(data, candidates):
    for name in candidates:
        if hasattr(data, "coords") and name in data.coords:
            return name

    for name in candidates:
        if hasattr(data, "dims") and name in data.dims:
            return name

    return None


def to_numpy_data_lon_lat(data, lon=None, lat=None):
    if hasattr(data, "coords") and hasattr(data, "dims"):
        if lon is None:
            lon_name = guess_coord_name(data, ["lon", "longitude", "x"])
            if lon_name is not None:
                lon = data[lon_name].values

        if lat is None:
            lat_name = guess_coord_name(data, ["lat", "latitude", "y"])
            if lat_name is not None:
                lat = data[lat_name].values

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


def maybe_add_cyclic(arr, lon, add_cyclic=True):
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


def mesh_lon_lat(lon, lat):
    lon = np.asarray(lon)
    lat = np.asarray(lat)

    if lon.ndim == 2 and lat.ndim == 2:
        return lon, lat

    return np.meshgrid(lon, lat)
