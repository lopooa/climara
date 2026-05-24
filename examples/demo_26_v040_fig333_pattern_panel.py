from __future__ import annotations

from pathlib import Path

import numpy as np
import xarray as xr

from climara.graphics import gsn_open_wks, gsn_panel
from climara.numerics import (
    calc_mon_anom,
    month_to_season,
    runave,
    eofunc,
    pattern_cor,
    coslat_weights,
    sqrt_coslat_weights,
)


def make_fake_monthly_field(name, lat, lon, time, mode="nh", seed=0):
    rng = np.random.default_rng(seed)

    lon2d, lat2d = np.meshgrid(lon, lat)

    if mode == "sam":
        pattern_values = (
            -1.2 * np.cos(np.deg2rad(lat2d + 55.0))
            + 0.8 * np.sin(np.deg2rad(2.0 * lon2d))
        )
        active = lat2d <= -20.0
    elif mode == "nao":
        pattern_values = (
            1.4 * np.cos(np.deg2rad(lat2d - 55.0))
            - 0.9 * np.cos(np.deg2rad(2.0 * lon2d))
        )
        active = lat2d >= 20.0
    else:
        pattern_values = (
            1.3 * np.cos(np.deg2rad(lat2d - 70.0))
            + 0.8 * np.sin(np.deg2rad(lon2d))
        )
        active = lat2d >= 20.0

    pattern_values = np.where(active, pattern_values, 0.0)
    pattern_values = pattern_values / np.nanstd(pattern_values[active])

    pattern = xr.DataArray(
        pattern_values,
        dims=["lat", "lon"],
        coords={"lat": lat, "lon": lon},
        name=f"{name}_true_pattern",
    )

    t = np.arange(time.size, dtype=float)

    pc = xr.DataArray(
        np.sin(2.0 * np.pi * t / 48.0)
        + 0.45 * np.cos(2.0 * np.pi * t / 19.0),
        dims=["time"],
        coords={"time": time},
        name=f"{name}_pc",
    )

    month = xr.DataArray(time, dims=["time"], coords={"time": time}).dt.month
    seasonal_cycle = 2.0 * np.sin(2.0 * np.pi * (month - 1) / 12.0)

    noise = xr.DataArray(
        0.35 * rng.standard_normal((time.size, lat.size, lon.size)),
        dims=["time", "lat", "lon"],
        coords={"time": time, "lat": lat, "lon": lon},
        name="noise",
    )

    data = pc * pattern + seasonal_cycle + noise
    data.name = f"{name}_monthly_psl_like"

    return data, pattern


def compute_mode_pattern(name, mode, lat, lon, time, seed=0, scale=1.0):
    data, true_pattern = make_fake_monthly_field(
        name,
        lat,
        lon,
        time,
        mode=mode,
        seed=seed,
    )

    if mode == "sam":
        data_region = data.sel(lat=slice(-90, -20))
        true_region = true_pattern.sel(lat=slice(-90, -20))
    else:
        data_region = data.sel(lat=slice(20, 90))
        true_region = true_pattern.sel(lat=slice(20, 90))

    anom = calc_mon_anom(data_region, dim="time")
    smooth = runave(anom, 3, dim="time")
    seasonal = month_to_season(smooth, season="DJF", dim="time")

    weights = sqrt_coslat_weights(seasonal["lat"])

    info = eofunc(
        seasonal,
        neval=1,
        dim="season_year",
        weights=weights,
        return_info=True,
    )

    eof_pattern = info["eof"].isel(mode=0)

    corr = pattern_cor(
        eof_pattern,
        true_region,
        weights=coslat_weights(seasonal["lat"]),
        dim=("lat", "lon"),
    )

    if float(corr) < 0:
        eof_pattern = -eof_pattern
        corr = -corr

    # Raw EOF vectors are normalized and usually too small for map plotting.
    # For this smoke demo, rescale the pattern to a unit spatial standard deviation.
    eof_std = eof_pattern.std(dim=("lat", "lon"), skipna=True)
    eof_pattern = eof_pattern / eof_std * scale

    full = xr.full_like(true_pattern, np.nan)
    full.loc[dict(lat=eof_pattern["lat"])] = eof_pattern

    return full, float(info["pcvar"][0]), float(corr)


def main():
    out_dir = Path("outputs/figures")
    out_dir.mkdir(parents=True, exist_ok=True)

    time = np.arange("1980-01", "2010-01", dtype="datetime64[M]")
    lon = np.linspace(0.0, 357.5, 144)
    lat = np.linspace(-90.0, 90.0, 73)

    nam_obs, nam_var, nam_corr = compute_mode_pattern(
        "NAM obs",
        "nam",
        lat,
        lon,
        time,
        seed=1,
        scale=1.0,
    )
    nam_mme, _, _ = compute_mode_pattern(
        "NAM MME",
        "nam",
        lat,
        lon,
        time,
        seed=11,
        scale=0.85,
    )

    nao_obs, nao_var, nao_corr = compute_mode_pattern(
        "NAO obs",
        "nao",
        lat,
        lon,
        time,
        seed=2,
        scale=1.0,
    )
    nao_mme, _, _ = compute_mode_pattern(
        "NAO MME",
        "nao",
        lat,
        lon,
        time,
        seed=22,
        scale=0.8,
    )

    sam_obs, sam_var, sam_corr = compute_mode_pattern(
        "SAM obs",
        "sam",
        lat,
        lon,
        time,
        seed=3,
        scale=1.0,
    )
    sam_mme, _, _ = compute_mode_pattern(
        "SAM MME",
        "sam",
        lat,
        lon,
        time,
        seed=33,
        scale=0.9,
    )

    data_list = [
        nam_obs.values,
        nam_mme.values,
        nao_obs.values,
        nao_mme.values,
        sam_obs.values,
        sam_mme.values,
    ]

    base_res = {
        "gsnFrame": True,
        "gsnPanelLabelBar": True,
        "gsnPanelFigureStrings": ["a", "b", "c", "d", "e", "f"],
        "gsnPanelMainString": "Fig. 3.33 NAM / NAO / SAM pattern-panel smoke",
        "gsnPanelXWhiteSpacePercent": 0,
        "gsnPanelYWhiteSpacePercent": 1,
        "gsnPanelLeft": 0.06,
        "gsnPanelRight": 0.94,

        "cnFillOn": True,
        "cnLinesOn": False,
        "cnLevelSelectionMode": "ManualLevels",
        "cnMinLevelValF": -4,
        "cnMaxLevelValF": 4,
        "cnLevelSpacingF": 1,
        "cnFillPalette": "BlueWhiteOrangeRed",

        "mpProjection": "Stereographic",
        "mpGridAndLimbOn": True,
        "mpPerimOn": True,


        "lbLabelBarOn": True,
        "lbOrientation": "horizontal",
        "pmLabelBarWidthF": 0.56,
        "pmLabelBarHeightF": 0.025,
    }

    nh_res = {
        "mpCenterLatF": 90,
        "mpMinLatF": 20,
        "mpCenterLonF": 0,
    }

    sh_res = {
        "mpCenterLatF": -90,
        "mpMaxLatF": -20,
        "mpCenterLonF": 0,
    }

    wks = gsn_open_wks(
        "png",
        "v040_fig333_pattern_panel_smoke",
        output_dir=out_dir,
    )

    fig, axes, out = gsn_panel(
        data_list,
        lon=lon,
        lat=lat,
        res=base_res,
        titles=[
            "NAM obs",
            "NAM historical MME",
            "NAO obs",
            "NAO historical MME",
            "SAM obs",
            "SAM historical MME",
        ],
        ncol=2,
        figsize=(8.8, 12),
        common_labelbar=True,
        wks=wks,
        panel_res_list=[
            nh_res,
            nh_res,
            nh_res,
            nh_res,
            sh_res,
            sh_res,
        ],
    )

    print(out["frame_file"])
    print(f"NAM variance/corr: {nam_var:.2f}% / {nam_corr:.3f}")
    print(f"NAO variance/corr: {nao_var:.2f}% / {nao_corr:.3f}")
    print(f"SAM variance/corr: {sam_var:.2f}% / {sam_corr:.3f}")


if __name__ == "__main__":
    main()
