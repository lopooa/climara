"""
Covariance and correlation functions.

NCL reference
-------------
Wrapper source:
- ni/src/lib/nfp/covcormW.c

Related Fortran routines include:
- dcovcorm
- dcovcorm_xy
- patternCor

Public NCL-style functions:
- covcorm
- covcorm_xy
- escorc
- esccr
- pattern_cor
"""

from __future__ import annotations

import numpy as np


def _is_xarray_obj(data):
    return hasattr(data, "dims") and hasattr(data, "mean")


def _normalize_dims(data, dim):
    if dim is None:
        if hasattr(data, "dims"):
            return list(data.dims)

        return tuple(range(np.asarray(data).ndim))

    if isinstance(dim, (str, int)):
        return [dim]

    return list(dim)


def _axis_from_dim(data, dim):
    if isinstance(dim, str):
        if hasattr(data, "get_axis_num"):
            return data.get_axis_num(dim)
        raise TypeError("dim must be an integer axis for numpy inputs")

    return int(dim)


def _axes_from_dim(data, dim):
    dims = _normalize_dims(data, dim)

    if hasattr(data, "get_axis_num"):
        return tuple(data.get_axis_num(d) if isinstance(d, str) else int(d) for d in dims)

    return tuple(int(d) for d in dims)


def _broadcast_weights_numpy(weights, shape, axes):
    w = np.asarray(weights, dtype=float)

    if w.ndim == 0:
        return w

    if w.shape == tuple(np.asarray(shape)[list(axes)]):
        new_shape = [1] * len(shape)

        for size, axis in zip(w.shape, axes):
            new_shape[axis] = size

        return w.reshape(new_shape)

    return w


def _covcorr_numpy(x, y, axis=0, ddof=1, skipna=True):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)

    if x.shape != y.shape:
        x, y = np.broadcast_arrays(x, y)

    axis = _axis_from_dim(x, axis)

    if skipna:
        valid = np.isfinite(x) & np.isfinite(y)
        x_work = np.where(valid, x, np.nan)
        y_work = np.where(valid, y, np.nan)
        count = np.sum(valid, axis=axis)
        x_mean = np.nanmean(x_work, axis=axis, keepdims=True)
        y_mean = np.nanmean(y_work, axis=axis, keepdims=True)
    else:
        valid = np.ones_like(x, dtype=bool)
        count = x.shape[axis]
        x_work = x
        y_work = y
        x_mean = np.mean(x_work, axis=axis, keepdims=True)
        y_mean = np.mean(y_work, axis=axis, keepdims=True)

    xa = np.where(valid, x_work - x_mean, np.nan)
    ya = np.where(valid, y_work - y_mean, np.nan)

    denom = count - ddof

    covariance = np.divide(
        np.nansum(xa * ya, axis=axis),
        denom,
        out=np.full(np.shape(np.nansum(xa * ya, axis=axis)), np.nan, dtype=float),
        where=denom > 0,
    )

    x_var = np.divide(
        np.nansum(xa * xa, axis=axis),
        denom,
        out=np.full(np.shape(covariance), np.nan, dtype=float),
        where=denom > 0,
    )
    y_var = np.divide(
        np.nansum(ya * ya, axis=axis),
        denom,
        out=np.full(np.shape(covariance), np.nan, dtype=float),
        where=denom > 0,
    )

    correlation = np.divide(
        covariance,
        np.sqrt(x_var * y_var),
        out=np.full(np.shape(covariance), np.nan, dtype=float),
        where=(x_var > 0) & (y_var > 0),
    )

    return covariance, correlation


def _covcorr_xarray(x, y, dim="time", ddof=1, skipna=True):
    try:
        import xarray as xr
    except Exception as exc:
        raise ImportError("xarray is required for xarray inputs") from exc

    x, y = xr.align(x, y, join="inner")

    if dim not in x.dims:
        raise ValueError(f"dimension {dim!r} not found in input")

    if skipna:
        valid = np.isfinite(x) & np.isfinite(y)
        x_work = x.where(valid)
        y_work = y.where(valid)
        count = valid.sum(dim=dim)
    else:
        x_work = x
        y_work = y
        count = x.sizes[dim]

    x_mean = x_work.mean(dim=dim, skipna=skipna)
    y_mean = y_work.mean(dim=dim, skipna=skipna)

    xa = x_work - x_mean
    ya = y_work - y_mean

    denom = count - ddof
    covariance = (xa * ya).sum(dim=dim, skipna=skipna) / denom

    x_var = (xa * xa).sum(dim=dim, skipna=skipna) / denom
    y_var = (ya * ya).sum(dim=dim, skipna=skipna) / denom

    correlation = covariance / np.sqrt(x_var * y_var)

    return covariance, correlation


def covcorm(x, y, dim="time", ddof=1, skipna=True, **kwargs):
    """Compute covariance and correlation along a dimension.

    Returns a dictionary with ``covariance`` and ``correlation``.
    """
    if _is_xarray_obj(x) or _is_xarray_obj(y):
        covariance, correlation = _covcorr_xarray(
            x,
            y,
            dim=dim,
            ddof=ddof,
            skipna=skipna,
        )
    else:
        covariance, correlation = _covcorr_numpy(
            x,
            y,
            axis=dim,
            ddof=ddof,
            skipna=skipna,
        )

    return {
        "covariance": covariance,
        "correlation": correlation,
    }


def covcorm_xy(x, y, dim="time", ddof=1, skipna=True, **kwargs):
    """Compute covariance and correlation for paired x/y fields."""
    return covcorm(x, y, dim=dim, ddof=ddof, skipna=skipna, **kwargs)


def escorc(x, y, dim="time", ddof=1, skipna=True, **kwargs):
    """Compute correlation between x and y along a dimension."""
    return covcorm(
        x,
        y,
        dim=dim,
        ddof=ddof,
        skipna=skipna,
        **kwargs,
    )["correlation"]


def esccr(x, y, dim="time", ddof=1, skipna=True, **kwargs):
    """Compute cross-correlation between x and y.

    This first implementation is an alias of escorc.
    """
    return escorc(x, y, dim=dim, ddof=ddof, skipna=skipna, **kwargs)


def _pattern_cor_numpy(x, y, weights=None, axes=None, skipna=True):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)

    if x.shape != y.shape:
        x, y = np.broadcast_arrays(x, y)

    if axes is None:
        axes = tuple(range(x.ndim))
    elif isinstance(axes, int):
        axes = (axes,)
    else:
        axes = tuple(axes)

    if weights is None:
        w = np.ones_like(x, dtype=float)
    else:
        w = _broadcast_weights_numpy(weights, x.shape, axes)

    if skipna:
        valid = np.isfinite(x) & np.isfinite(y) & np.isfinite(w)
        x_work = np.where(valid, x, 0.0)
        y_work = np.where(valid, y, 0.0)
        w_work = np.where(valid, w, 0.0)
    else:
        x_work = x
        y_work = y
        w_work = w

    wsum = np.sum(w_work, axis=axes, keepdims=True)

    x_mean = np.divide(
        np.sum(x_work * w_work, axis=axes, keepdims=True),
        wsum,
        out=np.full_like(wsum, np.nan, dtype=float),
        where=wsum != 0,
    )
    y_mean = np.divide(
        np.sum(y_work * w_work, axis=axes, keepdims=True),
        wsum,
        out=np.full_like(wsum, np.nan, dtype=float),
        where=wsum != 0,
    )

    xa = x_work - x_mean
    ya = y_work - y_mean

    numerator = np.sum(w_work * xa * ya, axis=axes)
    xsum = np.sum(w_work * xa * xa, axis=axes)
    ysum = np.sum(w_work * ya * ya, axis=axes)

    return np.divide(
        numerator,
        np.sqrt(xsum * ysum),
        out=np.full(np.shape(numerator), np.nan, dtype=float),
        where=(xsum > 0) & (ysum > 0),
    )


def _pattern_cor_xarray(x, y, weights=None, dim=None, skipna=True):
    try:
        import xarray as xr
    except Exception as exc:
        raise ImportError("xarray is required for xarray inputs") from exc

    x, y = xr.align(x, y, join="inner")

    dims = _normalize_dims(x, dim)

    if weights is None:
        w = xr.ones_like(x)
    else:
        if _is_xarray_obj(weights):
            w = weights
        else:
            arr = np.asarray(weights, dtype=float)

            if arr.ndim == 1 and len(dims) >= 1:
                name = dims[-1]
                w = xr.DataArray(arr, dims=[name], coords={name: x[name]})
            else:
                w = xr.DataArray(arr)

    if skipna:
        valid = np.isfinite(x) & np.isfinite(y) & np.isfinite(w)
        x_work = x.where(valid)
        y_work = y.where(valid)
        w_work = w.where(valid)
    else:
        x_work = x
        y_work = y
        w_work = w

    wsum = w_work.sum(dim=dims, skipna=skipna)
    x_mean = (x_work * w_work).sum(dim=dims, skipna=skipna) / wsum
    y_mean = (y_work * w_work).sum(dim=dims, skipna=skipna) / wsum

    xa = x_work - x_mean
    ya = y_work - y_mean

    numerator = (w_work * xa * ya).sum(dim=dims, skipna=skipna)
    xsum = (w_work * xa * xa).sum(dim=dims, skipna=skipna)
    ysum = (w_work * ya * ya).sum(dim=dims, skipna=skipna)

    return numerator / np.sqrt(xsum * ysum)


def pattern_cor(x, y, weights=None, dim=None, skipna=True, **kwargs):
    """Compute pattern correlation.

    Parameters
    ----------
    x, y : array-like or xarray.DataArray
        Patterns to compare.
    weights : array-like or xarray.DataArray, optional
        Spatial weights.  For latitude-weighted pattern correlation, pass
        ``coslat_weights(lat)`` or compatible weights.
    dim : str, int, sequence, or None
        Pattern dimensions to reduce.  If None, all dimensions are reduced.
    """
    if _is_xarray_obj(x) or _is_xarray_obj(y):
        return _pattern_cor_xarray(
            x,
            y,
            weights=weights,
            dim=dim,
            skipna=skipna,
        )

    axes = _axes_from_dim(x, dim)

    return _pattern_cor_numpy(
        x,
        y,
        weights=weights,
        axes=axes,
        skipna=skipna,
    )
