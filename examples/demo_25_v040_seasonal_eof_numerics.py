from __future__ import annotations

import numpy as np
import xarray as xr

from climara.numerics import (
    calc_mon_anom,
    month_to_season,
    runave,
    eofunc,
    eofunc_ts,
    dim_standardize,
    pattern_cor,
    coslat_weights,
    sqrt_coslat_weights,
)


def make_monthly_mode_data(name, lat, lon, time, seed=0):
    rng = np.random.default_rng(seed)

    lon2d, lat2d = np.meshgrid(lon, lat)

    pattern_values = (
        np.cos(np.deg2rad(lat2d)) * np.cos(np.deg2rad(lon2d))
        + 0.6 * np.sin(np.deg2rad(2.0 * lon2d))
    )
    pattern_values = pattern_values / np.nanstd(pattern_values)

    pattern = xr.DataArray(
        pattern_values,
        dims=["lat", "lon"],
        coords={"lat": lat, "lon": lon},
        name=f"{name}_true_pattern",
    )

    t = np.arange(time.size, dtype=float)

    pc = xr.DataArray(
        np.sin(2.0 * np.pi * t / 48.0) + 0.4 * np.cos(2.0 * np.pi * t / 21.0),
        dims=["time"],
        coords={"time": time},
        name=f"{name}_pc",
    )

    month = xr.DataArray(time, dims=["time"], coords={"time": time}).dt.month
    seasonal_cycle = 2.5 * np.sin(2.0 * np.pi * (month - 1) / 12.0)

    noise = xr.DataArray(
        0.25 * rng.standard_normal((time.size, lat.size, lon.size)),
        dims=["time", "lat", "lon"],
        coords={"time": time, "lat": lat, "lon": lon},
        name="noise",
    )

    data = pc * pattern + seasonal_cycle + noise
    data.name = f"{name}_monthly_field"

    return data, pattern


def run_one_mode(name, lat, lon, time, seed=0):
    data, true_pattern = make_monthly_mode_data(name, lat, lon, time, seed=seed)

    anom = calc_mon_anom(data, dim="time")
    smooth = runave(anom, 3, dim="time")
    seasonal = month_to_season(smooth, season="DJF", dim="time")

    eof_weights = sqrt_coslat_weights(seasonal["lat"])

    info = eofunc(
        seasonal,
        neval=1,
        dim="season_year",
        weights=eof_weights,
        return_info=True,
    )

    eof_pattern = info["eof"].isel(mode=0)
    pc = info["pc"].isel(mode=0)
    pc = dim_standardize(pc, dim="season_year")

    projected_pc = eofunc_ts(
        seasonal,
        info["eof"],
        dim="season_year",
        weights=eof_weights,
    ).isel(mode=0)
    projected_pc = dim_standardize(projected_pc, dim="season_year")

    corr_weights = coslat_weights(seasonal["lat"])
    corr = pattern_cor(
        eof_pattern,
        true_pattern,
        weights=corr_weights,
        dim=("lat", "lon"),
    )

    if float(corr) < 0:
        eof_pattern = -eof_pattern
        pc = -pc
        projected_pc = -projected_pc
        corr = -corr

    pc_corr = pattern_cor(
        pc,
        projected_pc,
        dim="season_year",
    )

    print(f"{name}:")
    print(f"  monthly shape      : {data.shape}")
    print(f"  anomaly shape      : {anom.shape}")
    print(f"  smooth shape       : {smooth.shape}")
    print(f"  seasonal shape     : {seasonal.shape}")
    print(f"  EOF shape          : {eof_pattern.shape}")
    print(f"  PC shape           : {pc.shape}")
    print(f"  explained variance : {float(info['pcvar'][0]):.2f}%")
    print(f"  pattern corr       : {float(corr):.3f}")
    print(f"  PC projection corr : {float(pc_corr):.3f}")
    print()


def main():
    time = np.arange("1980-01", "2010-01", dtype="datetime64[M]")
    lon = np.linspace(0.0, 357.5, 144)

    lat_nh = np.linspace(20.0, 90.0, 37)
    lat_sh = np.linspace(-90.0, -20.0, 37)

    run_one_mode("NAM-like seasonal EOF", lat_nh, lon, time, seed=1)
    run_one_mode("NAO-like seasonal EOF", lat_nh, lon, time, seed=2)
    run_one_mode("SAM-like seasonal EOF", lat_sh, lon, time, seed=3)


if __name__ == "__main__":
    main()
