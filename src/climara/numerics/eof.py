"""
EOF numerical functions.

NCL reference
-------------
Wrapper source:
- ni/src/lib/nfp/eofW.c

Related Fortran routines include:
- ddrveof
- xrveoft
- deof11

Public NCL-style functions:
- eofunc
- eofunc_n
- eofunc_ts
- eofunc_ts_n
- eofcov
- eofcor
- eof2data
"""

from __future__ import annotations

import numpy as np


def _is_xarray_obj(data):
    return hasattr(data, "dims") and hasattr(data, "coords")


def _time_axis(data, dim):
    if isinstance(dim, str):
        if hasattr(data, "get_axis_num"):
            return data.get_axis_num(dim)
        raise TypeError("dim must be an integer axis for numpy inputs")

    return int(dim)


def _move_time_first(arr, axis):
    arr = np.asarray(arr, dtype=float)

    return np.moveaxis(arr, axis, 0)


def _restore_spatial_shape(flat, spatial_shape):
    return np.asarray(flat).reshape((flat.shape[0],) + tuple(spatial_shape))


def _prepare_weights(weights, spatial_shape):
    if weights is None:
        return np.ones(spatial_shape, dtype=float)

    w = np.asarray(weights, dtype=float)

    if w.ndim == 0:
        return np.ones(spatial_shape, dtype=float) * float(w)

    if w.shape == tuple(spatial_shape):
        return w

    if w.ndim == 1 and len(spatial_shape) >= 1:
        if w.size == spatial_shape[0]:
            shape = [1] * len(spatial_shape)
            shape[0] = w.size
            return np.broadcast_to(w.reshape(shape), spatial_shape)

        if w.size == spatial_shape[-1]:
            shape = [1] * len(spatial_shape)
            shape[-1] = w.size
            return np.broadcast_to(w.reshape(shape), spatial_shape)

    try:
        return np.broadcast_to(w, spatial_shape)
    except ValueError as exc:
        raise ValueError(
            f"weights shape {w.shape} cannot be broadcast to spatial shape {spatial_shape}"
        ) from exc


def _as_numpy_core(data, dim, weights=None, center=True):
    axis = _time_axis(data, dim)
    arr = _move_time_first(np.asarray(data, dtype=float), axis)

    if arr.ndim < 2:
        raise ValueError("EOF input must have at least one time dimension and one spatial dimension")

    nt = arr.shape[0]
    spatial_shape = arr.shape[1:]
    matrix = arr.reshape(nt, -1)

    valid_space = np.all(np.isfinite(matrix), axis=0)

    if not np.any(valid_space):
        raise ValueError("no valid spatial points are available for EOF analysis")

    matrix_valid = matrix[:, valid_space]

    valid_time = np.all(np.isfinite(matrix_valid), axis=1)

    if np.count_nonzero(valid_time) < 2:
        raise ValueError("at least two valid time samples are required for EOF analysis")

    matrix_valid = matrix_valid[valid_time, :]

    mean = np.mean(matrix_valid, axis=0, keepdims=True)

    if center:
        matrix_work = matrix_valid - mean
    else:
        matrix_work = matrix_valid.copy()

    weight_grid = _prepare_weights(weights, spatial_shape)
    weight_flat = weight_grid.reshape(-1)[valid_space]

    if np.any(~np.isfinite(weight_flat)):
        raise ValueError("weights contain non-finite values at valid spatial points")

    matrix_weighted = matrix_work * weight_flat[None, :]

    return {
        "matrix_weighted": matrix_weighted,
        "matrix_valid": matrix_valid,
        "mean": mean,
        "valid_space": valid_space,
        "valid_time": valid_time,
        "weight_flat": weight_flat,
        "spatial_shape": spatial_shape,
        "time_axis": axis,
        "nt_valid": matrix_valid.shape[0],
        "nspace": np.prod(spatial_shape),
    }


def _solve_eof_numpy(core, neval):
    matrix_weighted = core["matrix_weighted"]
    nt = matrix_weighted.shape[0]

    if neval < 1:
        raise ValueError("neval must be >= 1")

    neval = min(int(neval), min(matrix_weighted.shape))

    u, singular_values, vt = np.linalg.svd(matrix_weighted, full_matrices=False)

    u = u[:, :neval]
    singular_values = singular_values[:neval]
    vt = vt[:neval, :]

    pcs = u * singular_values[None, :]

    denom = max(nt - 1, 1)
    evals = singular_values ** 2 / denom
    total = np.sum(np.linalg.svd(matrix_weighted, full_matrices=False, compute_uv=False) ** 2 / denom)

    if total == 0:
        pcvar = np.full_like(evals, np.nan, dtype=float)
    else:
        pcvar = evals / total * 100.0

    nspace = int(core["nspace"])
    valid_space = core["valid_space"]

    eof_flat = np.full((neval, nspace), np.nan, dtype=float)
    eof_flat[:, valid_space] = vt

    eofs = _restore_spatial_shape(eof_flat, core["spatial_shape"])

    return {
        "eof": eofs,
        "pc": pcs,
        "evals": evals,
        "pcvar": pcvar,
        "singular_values": singular_values,
    }


def _to_xarray_eof(data, eofs, info):
    try:
        import xarray as xr
    except Exception as exc:
        raise ImportError("xarray is required for xarray outputs") from exc

    spatial_dims = [d for d in data.dims if d != info["dim"]]
    coords = {"mode": np.arange(eofs.shape[0])}
    coords.update({d: data[d] for d in spatial_dims if d in data.coords})

    out = xr.DataArray(
        eofs,
        dims=["mode"] + spatial_dims,
        coords=coords,
        name="eof",
    )
    out.attrs["evals"] = info["evals"]
    out.attrs["pcvar"] = info["pcvar"]
    out.attrs["singular_values"] = info["singular_values"]

    return out


def _to_xarray_pc(data, pcs, valid_time, dim):
    try:
        import xarray as xr
    except Exception as exc:
        raise ImportError("xarray is required for xarray outputs") from exc

    time_coord = data[dim].values[valid_time] if dim in data.coords else np.arange(pcs.shape[0])

    return xr.DataArray(
        pcs,
        dims=[dim, "mode"],
        coords={dim: time_coord, "mode": np.arange(pcs.shape[1])},
        name="pc",
    )


def eofunc(data, neval=1, opt=None, dim="time", weights=None, center=True, return_info=False, **kwargs):
    """Compute EOF patterns using SVD.

    Parameters
    ----------
    data : array-like or xarray.DataArray
        Input data with one time dimension and one or more spatial dimensions.
    neval : int
        Number of EOF modes to return.
    opt : object, optional
        Kept for NCL-style API compatibility.
    dim : str or int
        Time dimension name for xarray inputs, or time axis for numpy inputs.
    weights : array-like, optional
        Spatial weights.  For NAM/NAO/SAM EOFs, this is commonly
        ``sqrt_coslat_weights(lat)``.
    center : bool
        Whether to remove the temporal mean before SVD.
    return_info : bool
        If True, return a dictionary containing EOFs, PCs, eigenvalues, and
        variance fractions.
    """
    is_xarray = _is_xarray_obj(data)

    core = _as_numpy_core(data, dim=dim, weights=weights, center=center)
    result = _solve_eof_numpy(core, neval=neval)

    if is_xarray:
        result["eof"] = _to_xarray_eof(
            data,
            result["eof"],
            {
                "dim": dim,
                "evals": result["evals"],
                "pcvar": result["pcvar"],
                "singular_values": result["singular_values"],
            },
        )
        result["pc"] = _to_xarray_pc(data, result["pc"], core["valid_time"], dim)

    if return_info:
        result["valid_space"] = core["valid_space"]
        result["valid_time"] = core["valid_time"]
        result["center"] = center
        return result

    return result["eof"]


def eofunc_n(data, neval=1, opt=None, dim="time", weights=None, center=True, return_info=False, **kwargs):
    """Compute EOF patterns along a selected dimension."""
    return eofunc(
        data,
        neval=neval,
        opt=opt,
        dim=dim,
        weights=weights,
        center=center,
        return_info=return_info,
        **kwargs,
    )


def _project_numpy(data, eof, dim="time", weights=None, center=True):
    axis = _time_axis(data, dim)
    arr = _move_time_first(np.asarray(data, dtype=float), axis)

    nt = arr.shape[0]
    spatial_shape = arr.shape[1:]
    matrix = arr.reshape(nt, -1)

    eof_arr = np.asarray(eof, dtype=float)

    if eof_arr.ndim == len(spatial_shape):
        eof_arr = eof_arr[None, ...]

    if eof_arr.shape[1:] != spatial_shape:
        raise ValueError(
            f"EOF spatial shape {eof_arr.shape[1:]} does not match data spatial shape {spatial_shape}"
        )

    eof_flat = eof_arr.reshape(eof_arr.shape[0], -1)

    valid_space = np.all(np.isfinite(eof_flat), axis=0) & np.all(np.isfinite(matrix), axis=0)

    matrix_valid = matrix[:, valid_space]

    if center:
        matrix_valid = matrix_valid - np.nanmean(matrix_valid, axis=0, keepdims=True)

    weight_grid = _prepare_weights(weights, spatial_shape)
    weight_flat = weight_grid.reshape(-1)[valid_space]

    matrix_weighted = matrix_valid * weight_flat[None, :]
    eof_valid = eof_flat[:, valid_space]

    return matrix_weighted @ eof_valid.T


def eofunc_ts(data, eof, opt=None, dim="time", weights=None, center=True, **kwargs):
    """Compute principal component time series from EOF patterns."""
    is_xarray = _is_xarray_obj(data)

    pcs = _project_numpy(data, eof, dim=dim, weights=weights, center=center)

    if is_xarray:
        try:
            import xarray as xr
        except Exception as exc:
            raise ImportError("xarray is required for xarray outputs") from exc

        time_coord = data[dim] if isinstance(dim, str) and dim in data.coords else np.arange(pcs.shape[0])

        return xr.DataArray(
            pcs,
            dims=[dim, "mode"] if isinstance(dim, str) else ["time", "mode"],
            coords={dim if isinstance(dim, str) else "time": time_coord, "mode": np.arange(pcs.shape[1])},
            name="pc",
        )

    return pcs


def eofunc_ts_n(data, eof, opt=None, dim="time", weights=None, center=True, **kwargs):
    """Compute principal component time series along a selected dimension."""
    return eofunc_ts(
        data,
        eof,
        opt=opt,
        dim=dim,
        weights=weights,
        center=center,
        **kwargs,
    )


def eofcov(data, neval=1, opt=None, dim="time", weights=None, **kwargs):
    """Compute covariance EOFs.

    This first implementation delegates to eofunc.
    """
    return eofunc(data, neval=neval, opt=opt, dim=dim, weights=weights, **kwargs)


def eofcor(data, neval=1, opt=None, dim="time", weights=None, **kwargs):
    """Compute correlation EOFs.

    This is not implemented separately yet.
    """
    raise NotImplementedError("eofcor is not implemented yet.")


def eof2data(eof, pc, **kwargs):
    """Reconstruct data from EOF patterns and principal components."""
    raise NotImplementedError("eof2data is not implemented yet.")
