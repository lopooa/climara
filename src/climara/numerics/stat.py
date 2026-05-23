"""
Statistical numerical functions.

NCL reference
-------------
Wrapper source:
- ni/src/lib/nfp/statW.c

Related Fortran routines include:
- dstat2
- dstat4
- drmvmean
- dxstnd

Public NCL-style functions:
- dim_rmvmean
- dim_rmvmean_n
- dim_standardize
- dim_standardize_n
- dim_rmsd
- dim_rmsd_n
- dim_stat4
- dim_stat4_n
"""

from __future__ import annotations

import numpy as np


def _is_xarray_obj(data):
    return hasattr(data, "dims") and hasattr(data, "mean")


def _axis_from_dim(data, dim):
    if isinstance(dim, str):
        if hasattr(data, "get_axis_num"):
            return data.get_axis_num(dim)
        raise TypeError("dim must be an integer axis for numpy inputs")

    return int(dim)


def _maybe_keep_attrs(data, out, keep_attrs=True):
    if keep_attrs and hasattr(out, "attrs") and hasattr(data, "attrs"):
        out.attrs.update(data.attrs)

    return out


def dim_rmvmean(data, dim="time", **kwargs):
    """Remove the mean along a dimension.

    xarray inputs preserve coordinates and dimensions.  numpy inputs return an
    ndarray.
    """
    if _is_xarray_obj(data):
        if dim not in data.dims:
            raise ValueError(f"dimension {dim!r} not found in input")

        out = data - data.mean(dim=dim, skipna=True)
        return _maybe_keep_attrs(data, out)

    axis = _axis_from_dim(data, dim)
    arr = np.asarray(data, dtype=float)
    mean = np.nanmean(arr, axis=axis, keepdims=True)

    return arr - mean


def dim_rmvmean_n(data, dim="time", **kwargs):
    """Remove the mean along a selected dimension."""
    return dim_rmvmean(data, dim=dim, **kwargs)


def dim_standardize(data, dim="time", ddof=1, **kwargs):
    """Standardize data along a dimension.

    The standardized result is ``(data - mean) / std`` using NaN-aware
    statistics.
    """
    if _is_xarray_obj(data):
        if dim not in data.dims:
            raise ValueError(f"dimension {dim!r} not found in input")

        mean = data.mean(dim=dim, skipna=True)
        std = data.std(dim=dim, skipna=True, ddof=ddof)
        out = (data - mean) / std
        return _maybe_keep_attrs(data, out)

    axis = _axis_from_dim(data, dim)
    arr = np.asarray(data, dtype=float)
    mean = np.nanmean(arr, axis=axis, keepdims=True)
    std = np.nanstd(arr, axis=axis, ddof=ddof, keepdims=True)

    return (arr - mean) / std


def dim_standardize_n(data, dim="time", ddof=1, **kwargs):
    """Standardize data along a selected dimension."""
    return dim_standardize(data, dim=dim, ddof=ddof, **kwargs)


def dim_rmsd(x, y, dim="time", **kwargs):
    """Compute RMS difference along a dimension."""
    if _is_xarray_obj(x):
        diff = x - y

        if dim not in diff.dims:
            raise ValueError(f"dimension {dim!r} not found in input")

        return np.sqrt((diff ** 2).mean(dim=dim, skipna=True))

    axis = _axis_from_dim(x, dim)
    diff = np.asarray(x, dtype=float) - np.asarray(y, dtype=float)

    return np.sqrt(np.nanmean(diff ** 2, axis=axis))


def dim_rmsd_n(x, y, dim="time", **kwargs):
    """Compute RMS difference along a selected dimension."""
    return dim_rmsd(x, y, dim=dim, **kwargs)


def dim_stat4(data, dim="time", ddof=1, **kwargs):
    """Compute four basic statistics along a dimension.

    Returns a dictionary with ``mean``, ``std``, ``min``, and ``max``.
    """
    if _is_xarray_obj(data):
        if dim not in data.dims:
            raise ValueError(f"dimension {dim!r} not found in input")

        return {
            "mean": data.mean(dim=dim, skipna=True),
            "std": data.std(dim=dim, skipna=True, ddof=ddof),
            "min": data.min(dim=dim, skipna=True),
            "max": data.max(dim=dim, skipna=True),
        }

    axis = _axis_from_dim(data, dim)
    arr = np.asarray(data, dtype=float)

    return {
        "mean": np.nanmean(arr, axis=axis),
        "std": np.nanstd(arr, axis=axis, ddof=ddof),
        "min": np.nanmin(arr, axis=axis),
        "max": np.nanmax(arr, axis=axis),
    }


def dim_stat4_n(data, dim="time", **kwargs):
    """Compute four basic statistics along a selected dimension."""
    return dim_stat4(data, dim=dim, **kwargs)
