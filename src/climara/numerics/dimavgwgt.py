"""
Weighted dimension average functions.

NCL reference
-------------
Wrapper source:
- ni/src/lib/nfp/dimavgwgtW.c

Related Fortran routines include:
- dimavgwgt
- dimsumwgt
- areaAve

Public NCL-style functions:
- dim_avg_wgt
- dim_avg_wgt_n
- dim_sum_wgt
- dim_sum_wgt_n

Climara helper functions:
- coslat_weights
- sqrt_coslat_weights
"""

from __future__ import annotations

import numpy as np


def _is_xarray_obj(data):
    return hasattr(data, "dims") and hasattr(data, "weighted")


def _is_xarray_dataarray(data):
    return hasattr(data, "dims") and hasattr(data, "coords")


def _normalize_dims(data, dim):
    if dim is None:
        if hasattr(data, "dims"):
            return list(data.dims)

        return tuple(range(np.asarray(data).ndim))

    if isinstance(dim, (str, int)):
        return [dim]

    return list(dim)


def _axes_from_dim(data, dim):
    dims = _normalize_dims(data, dim)

    if hasattr(data, "get_axis_num"):
        return tuple(data.get_axis_num(d) if isinstance(d, str) else int(d) for d in dims)

    return tuple(int(d) for d in dims)


def _maybe_to_xarray_weight(data, weights, dim):
    if _is_xarray_dataarray(weights):
        return weights

    dims = _normalize_dims(data, dim)

    try:
        import xarray as xr
    except Exception as exc:
        raise ImportError("xarray is required to construct weights for xarray inputs") from exc

    arr = np.asarray(weights, dtype=float)

    if arr.ndim == 0:
        return xr.DataArray(arr)

    if arr.ndim != len(dims):
        if arr.ndim == 1 and len(dims) >= 1:
            dims = [dims[-1]]
        else:
            raise ValueError(
                "weights dimensions do not match selected dimensions; "
                "pass xarray weights with named dimensions for complex cases"
            )

    coords = {}

    for axis, name in enumerate(dims):
        if isinstance(name, str) and name in data.coords and arr.shape[axis] == data.sizes[name]:
            coords[name] = data[name]

    return xr.DataArray(arr, dims=dims, coords=coords)


def _weighted_sum_numpy(data, weights, axes, skipna=True):
    arr = np.asarray(data, dtype=float)
    w = np.asarray(weights, dtype=float)

    if skipna:
        valid = np.isfinite(arr)
        arr_work = np.where(valid, arr, 0.0)
        w_work = np.where(valid, w, 0.0)
    else:
        arr_work = arr
        w_work = w

    return np.sum(arr_work * w_work, axis=axes)


def _weighted_avg_numpy(data, weights, axes, skipna=True):
    arr = np.asarray(data, dtype=float)
    w = np.asarray(weights, dtype=float)

    if skipna:
        valid = np.isfinite(arr)
        arr_work = np.where(valid, arr, 0.0)
        w_work = np.where(valid, w, 0.0)
    else:
        arr_work = arr
        w_work = w

    numerator = np.sum(arr_work * w_work, axis=axes)
    denominator = np.sum(w_work, axis=axes)

    return np.divide(
        numerator,
        denominator,
        out=np.full_like(numerator, np.nan, dtype=float),
        where=denominator != 0,
    )


def dim_avg_wgt(data, weights, dim=None, opt=0, skipna=True, **kwargs):
    """Compute weighted average along one or more dimensions."""
    if _is_xarray_obj(data):
        dims = _normalize_dims(data, dim)
        w = _maybe_to_xarray_weight(data, weights, dims)

        return data.weighted(w).mean(dim=dims, skipna=skipna)

    axes = _axes_from_dim(data, dim)

    return _weighted_avg_numpy(data, weights, axes=axes, skipna=skipna)


def dim_avg_wgt_n(data, weights, dim=None, opt=0, skipna=True, **kwargs):
    """Compute weighted average along selected dimensions."""
    return dim_avg_wgt(
        data,
        weights=weights,
        dim=dim,
        opt=opt,
        skipna=skipna,
        **kwargs,
    )


def dim_sum_wgt(data, weights, dim=None, opt=0, skipna=True, **kwargs):
    """Compute weighted sum along one or more dimensions."""
    if _is_xarray_obj(data):
        dims = _normalize_dims(data, dim)
        w = _maybe_to_xarray_weight(data, weights, dims)
        weighted = data * w

        return weighted.sum(dim=dims, skipna=skipna)

    axes = _axes_from_dim(data, dim)

    return _weighted_sum_numpy(data, weights, axes=axes, skipna=skipna)


def dim_sum_wgt_n(data, weights, dim=None, opt=0, skipna=True, **kwargs):
    """Compute weighted sum along selected dimensions."""
    return dim_sum_wgt(
        data,
        weights=weights,
        dim=dim,
        opt=opt,
        skipna=skipna,
        **kwargs,
    )


def coslat_weights(lat):
    """Return cosine-latitude weights.

    The input latitude is assumed to be in degrees.
    """
    weights = np.cos(np.deg2rad(lat))
    weights = weights.clip(min=0)

    if hasattr(weights, "name"):
        weights.name = "coslat_weights"

    return weights


def sqrt_coslat_weights(lat):
    """Return square-root cosine-latitude weights for EOF analysis.

    The input latitude is assumed to be in degrees.
    """
    weights = np.sqrt(coslat_weights(lat))

    if hasattr(weights, "name"):
        weights.name = "sqrt_coslat_weights"

    return weights
