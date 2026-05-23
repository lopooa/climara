"""
Running average functions.

NCL reference
-------------
Wrapper source:
- ni/src/lib/nfp/wrunaveW.c

Related Fortran routines:
- drunave
- dwgtrunave

Public NCL-style functions:
- runave
- runave_n
- wgt_runave
- wgt_runave_n
"""

from __future__ import annotations

import numpy as np


def _is_xarray_obj(data):
    return hasattr(data, "rolling") and hasattr(data, "dims")


def _normalize_axis(data, dim):
    if isinstance(dim, str):
        if hasattr(data, "dims"):
            return data.get_axis_num(dim)
        raise TypeError("dim must be an integer axis for numpy inputs")

    return int(dim)


def _nan_running_mean_1d(values, n):
    values = np.asarray(values, dtype=float)

    if n < 1:
        raise ValueError("n must be >= 1")

    if values.size < n:
        return np.full(values.shape, np.nan, dtype=float)

    valid = np.isfinite(values).astype(float)
    filled = np.where(np.isfinite(values), values, 0.0)

    kernel = np.ones(int(n), dtype=float)
    summed = np.convolve(filled, kernel, mode="valid")
    counted = np.convolve(valid, kernel, mode="valid")

    out_valid = np.divide(
        summed,
        counted,
        out=np.full_like(summed, np.nan, dtype=float),
        where=counted > 0,
    )

    left = int(n) // 2
    right = int(n) - 1 - left

    return np.concatenate(
        [
            np.full(left, np.nan, dtype=float),
            out_valid,
            np.full(right, np.nan, dtype=float),
        ]
    )


def _nan_weighted_running_mean_1d(values, weights):
    values = np.asarray(values, dtype=float)
    weights = np.asarray(weights, dtype=float)

    if weights.ndim != 1:
        raise ValueError("weights must be one-dimensional")

    n = weights.size

    if n < 1:
        raise ValueError("weights must contain at least one value")

    if values.size < n:
        return np.full(values.shape, np.nan, dtype=float)

    valid = np.isfinite(values).astype(float)
    filled = np.where(np.isfinite(values), values, 0.0)

    kernel = weights.astype(float)
    summed = np.convolve(filled, kernel, mode="valid")
    counted = np.convolve(valid, kernel, mode="valid")

    weight_sum = np.convolve(valid, kernel, mode="valid")

    out_valid = np.divide(
        summed,
        weight_sum,
        out=np.full_like(summed, np.nan, dtype=float),
        where=weight_sum != 0,
    )

    left = n // 2
    right = n - 1 - left

    return np.concatenate(
        [
            np.full(left, np.nan, dtype=float),
            out_valid,
            np.full(right, np.nan, dtype=float),
        ]
    )


def _rolling_numpy(data, n, axis):
    arr = np.asarray(data, dtype=float)
    axis = _normalize_axis(arr, axis)

    return np.apply_along_axis(_nan_running_mean_1d, axis, arr, int(n))


def _weighted_rolling_numpy(data, weights, axis):
    arr = np.asarray(data, dtype=float)
    axis = _normalize_axis(arr, axis)

    return np.apply_along_axis(_nan_weighted_running_mean_1d, axis, arr, weights)


def runave(data, n, opt=0, dim="time", **kwargs):
    """Compute a centered running average.

    Parameters
    ----------
    data : array-like or xarray.DataArray
        Input data.
    n : int
        Window length.
    opt : int, optional
        Kept for NCL-style API compatibility.  The current implementation uses
        centered windows and fills incomplete edge windows with missing values.
    dim : str or int, optional
        Dimension name for xarray inputs, or axis index for numpy inputs.

    Returns
    -------
    Same family as input
        xarray input returns xarray output; numpy-like input returns ndarray.
    """
    n = int(n)

    if n < 1:
        raise ValueError("n must be >= 1")

    if _is_xarray_obj(data):
        if dim not in data.dims:
            raise ValueError(f"dimension {dim!r} not found in input")

        return data.rolling({dim: n}, center=True, min_periods=n).mean()

    axis = _normalize_axis(data, dim)

    return _rolling_numpy(data, n=n, axis=axis)


def runave_n(data, n, opt=0, dim="time", **kwargs):
    """Compute a running average along a selected dimension."""
    return runave(data, n=n, opt=opt, dim=dim, **kwargs)


def wgt_runave(data, weights, opt=0, dim="time", **kwargs):
    """Compute a centered weighted running average.

    For xarray inputs, the implementation currently applies a custom
    one-dimensional weighted rolling calculation along ``dim``.
    """
    weights = np.asarray(weights, dtype=float)

    if _is_xarray_obj(data):
        if dim not in data.dims:
            raise ValueError(f"dimension {dim!r} not found in input")

        axis = data.get_axis_num(dim)
        values = _weighted_rolling_numpy(data.values, weights=weights, axis=axis)

        return data.copy(data=values)

    axis = _normalize_axis(data, dim)

    return _weighted_rolling_numpy(data, weights=weights, axis=axis)


def wgt_runave_n(data, weights, opt=0, dim="time", **kwargs):
    """Compute a weighted running average along a selected dimension."""
    return wgt_runave(data, weights=weights, opt=opt, dim=dim, **kwargs)
