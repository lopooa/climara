"""
Time and seasonal numerical functions.

NCL reference
-------------
Related NCL contributed-style functions include:
- clmMon*
- calcMonAnom*
- month_to_season

Public NCL-style / climara functions:
- clm_mon
- calc_mon_anom
- month_to_season
"""

from __future__ import annotations

import numpy as np


_SEASON_MONTHS = {
    "DJF": [12, 1, 2],
    "JFM": [1, 2, 3],
    "FMA": [2, 3, 4],
    "MAM": [3, 4, 5],
    "AMJ": [4, 5, 6],
    "MJJ": [5, 6, 7],
    "JJA": [6, 7, 8],
    "JAS": [7, 8, 9],
    "ASO": [8, 9, 10],
    "SON": [9, 10, 11],
    "OND": [10, 11, 12],
    "NDJ": [11, 12, 1],
    "ANN": list(range(1, 13)),
}


def _is_xarray_obj(data):
    return hasattr(data, "dims") and hasattr(data, "coords")


def _month_index_from_length(n, start_month=1):
    start_month = int(start_month)

    if start_month < 1 or start_month > 12:
        raise ValueError("start_month must be in 1..12")

    return ((np.arange(n) + start_month - 1) % 12) + 1


def _year_index_from_length(n, start_year=0, start_month=1):
    start_month = int(start_month)
    start_year = int(start_year)
    offset = start_month - 1

    return start_year + (np.arange(n) + offset) // 12


def _normalize_months(months, n, start_month=1):
    if months is None:
        return _month_index_from_length(n, start_month=start_month)

    months = np.asarray(months, dtype=int)

    if months.size != n:
        raise ValueError("months must have the same length as the time dimension")

    return months


def _normalize_years(years, n, start_year=0, start_month=1):
    if years is None:
        return _year_index_from_length(n, start_year=start_year, start_month=start_month)

    years = np.asarray(years, dtype=int)

    if years.size != n:
        raise ValueError("years must have the same length as the time dimension")

    return years


def clm_mon(data, dim="time", months=None, start_month=1, skipna=True, **kwargs):
    """Calculate monthly climatology.

    For xarray inputs, the time coordinate is used through ``time.month``.
    For numpy inputs, pass ``months`` or use ``start_month`` to infer monthly
    sequence positions.
    """
    if _is_xarray_obj(data):
        if dim not in data.dims:
            raise ValueError(f"dimension {dim!r} not found in input")

        return data.groupby(f"{dim}.month").mean(dim=dim, skipna=skipna)

    arr = np.asarray(data, dtype=float)
    axis = int(dim)
    arr = np.moveaxis(arr, axis, 0)

    month_index = _normalize_months(
        months,
        arr.shape[0],
        start_month=start_month,
    )

    out_shape = (12,) + arr.shape[1:]
    clim = np.full(out_shape, np.nan, dtype=float)

    for month in range(1, 13):
        mask = month_index == month

        if np.any(mask):
            if skipna:
                clim[month - 1] = np.nanmean(arr[mask], axis=0)
            else:
                clim[month - 1] = np.mean(arr[mask], axis=0)

    return clim


def calc_mon_anom(data, dim="time", months=None, start_month=1, skipna=True, **kwargs):
    """Calculate monthly anomalies by removing monthly climatology."""
    if _is_xarray_obj(data):
        if dim not in data.dims:
            raise ValueError(f"dimension {dim!r} not found in input")

        clim = data.groupby(f"{dim}.month").mean(dim=dim, skipna=skipna)

        return data.groupby(f"{dim}.month") - clim

    arr = np.asarray(data, dtype=float)
    axis = int(dim)
    arr_time_first = np.moveaxis(arr, axis, 0)

    month_index = _normalize_months(
        months,
        arr_time_first.shape[0],
        start_month=start_month,
    )

    clim = clm_mon(
        arr,
        dim=axis,
        months=month_index,
        start_month=start_month,
        skipna=skipna,
    )

    out = np.empty_like(arr_time_first, dtype=float)

    for i, month in enumerate(month_index):
        out[i] = arr_time_first[i] - clim[month - 1]

    return np.moveaxis(out, 0, axis)


def _season_months(season):
    season = str(season).upper()

    if season not in _SEASON_MONTHS:
        raise ValueError(
            f"unsupported season {season!r}; available: {sorted(_SEASON_MONTHS)}"
        )

    return _SEASON_MONTHS[season]


def _season_year_numpy(month_index, year_index, season):
    season = str(season).upper()

    if season in {"DJF", "NDJ"}:
        return year_index + np.isin(month_index, [11, 12]).astype(int)

    return year_index


def month_to_season(
    data,
    season="DJF",
    dim="time",
    months=None,
    years=None,
    start_month=1,
    start_year=0,
    skipna=True,
    require_complete=True,
    **kwargs,
):
    """Convert monthly data to seasonal means.

    For xarray inputs, output dimension is ``season_year``.
    For numpy inputs, the time axis is replaced by a season-year axis.
    """
    season = str(season).upper()
    season_months = _season_months(season)

    if _is_xarray_obj(data):
        try:
            import xarray as xr
        except Exception as exc:
            raise ImportError("xarray is required for xarray inputs") from exc

        if dim not in data.dims:
            raise ValueError(f"dimension {dim!r} not found in input")

        month = data[dim].dt.month
        year = data[dim].dt.year

        if season in {"DJF", "NDJ"}:
            season_year = year + xr.where(month.isin([11, 12]), 1, 0)
        else:
            season_year = year

        mask = month.isin(season_months)
        selected = data.where(mask, drop=True)
        selected_year = season_year.where(mask, drop=True)
        selected = selected.assign_coords(season_year=(dim, selected_year.data))

        grouped = selected.groupby("season_year").mean(dim=dim, skipna=skipna)

        if require_complete:
            ones = xr.DataArray(
                np.ones(selected.sizes[dim], dtype=int),
                dims=[dim],
                coords={dim: selected[dim]},
            )
            ones = ones.assign_coords(season_year=(dim, selected["season_year"].data))
            counts = ones.groupby("season_year").sum(dim=dim)
            valid_years = counts["season_year"].where(
                counts == len(season_months),
                drop=True,
            )
            grouped = grouped.sel(season_year=valid_years)

        grouped.attrs.update(data.attrs)

        return grouped

    arr = np.asarray(data, dtype=float)
    axis = int(dim)
    arr_time_first = np.moveaxis(arr, axis, 0)

    ntime = arr_time_first.shape[0]
    month_index = _normalize_months(
        months,
        ntime,
        start_month=start_month,
    )
    year_index = _normalize_years(
        years,
        ntime,
        start_year=start_year,
        start_month=start_month,
    )
    season_year = _season_year_numpy(month_index, year_index, season)

    mask = np.isin(month_index, season_months)
    selected = arr_time_first[mask]
    selected_year = season_year[mask]

    out = []
    out_years = []

    for year in np.unique(selected_year):
        group = selected[selected_year == year]

        if require_complete and group.shape[0] != len(season_months):
            continue

        if skipna:
            out.append(np.nanmean(group, axis=0))
        else:
            out.append(np.mean(group, axis=0))

        out_years.append(year)

    if not out:
        result = np.empty((0,) + arr_time_first.shape[1:], dtype=float)
    else:
        result = np.stack(out, axis=0)

    result = np.moveaxis(result, 0, axis)

    return result
