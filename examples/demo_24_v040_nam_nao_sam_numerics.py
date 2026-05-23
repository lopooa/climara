from __future__ import annotations

import numpy as np

from climara.numerics import (
    dim_rmvmean,
    dim_standardize,
    runave,
    eofunc,
    eofunc_ts,
    pattern_cor,
    coslat_weights,
    sqrt_coslat_weights,
)


def make_fake_mode_field(lat, lon, seed=0):
    rng = np.random.default_rng(seed)

    lon2d, lat2d = np.meshgrid(lon, lat)

    pattern = (
        np.cos(np.deg2rad(lat2d)) * np.cos(np.deg2rad(lon2d))
        + 0.6 * np.sin(np.deg2rad(2.0 * lon2d))
    )

    pattern = pattern / np.nanstd(pattern)

    nt = 120
    time = np.arange(nt)

    pc = (
        np.sin(2.0 * np.pi * time / 36.0)
        + 0.4 * np.cos(2.0 * np.pi * time / 17.0)
    )

    noise = 0.25 * rng.standard_normal((nt, lat.size, lon.size))
    data = pc[:, None, None] * pattern[None, :, :] + noise

    return data, pattern, pc


def run_one_mode(name, lat, lon, seed=0):
    data, true_pattern, true_pc = make_fake_mode_field(lat, lon, seed=seed)

    anom = dim_rmvmean(data, dim=0)
    smooth = runave(anom, 3, dim=0)

    # Centered 3-point running mean leaves NaNs at both edges.
    # Drop incomplete edge windows before EOF.
    smooth = smooth[1:-1, :, :]

    eof_weights = sqrt_coslat_weights(lat)

    info = eofunc(
        smooth,
        neval=1,
        dim=0,
        weights=eof_weights,
        return_info=True,
    )

    eof_pattern = info["eof"][0]
    pc = info["pc"][:, 0]
    pc = dim_standardize(pc, dim=0)

    projected_pc = eofunc_ts(
        smooth,
        info["eof"],
        dim=0,
        weights=eof_weights,
    )[:, 0]
    projected_pc = dim_standardize(projected_pc, dim=0)

    corr_weights = coslat_weights(lat)[:, None]
    corr = pattern_cor(
        eof_pattern,
        true_pattern,
        weights=corr_weights,
        dim=(0, 1),
    )

    if corr < 0:
        eof_pattern = -eof_pattern
        pc = -pc
        projected_pc = -projected_pc
        corr = -corr

    pc_corr = pattern_cor(
        pc,
        projected_pc,
        dim=0,
    )

    print(f"{name}:")
    print(f"  data shape        : {data.shape}")
    print(f"  smooth shape      : {smooth.shape}")
    print(f"  EOF shape         : {eof_pattern.shape}")
    print(f"  PC shape          : {pc.shape}")
    print(f"  explained variance: {info['pcvar'][0]:.2f}%")
    print(f"  pattern corr      : {corr:.3f}")
    print(f"  PC projection corr: {pc_corr:.3f}")
    print()


def main():
    lon = np.linspace(0.0, 357.5, 144)
    lat_nh = np.linspace(20.0, 90.0, 37)
    lat_sh = np.linspace(-90.0, -20.0, 37)

    run_one_mode("NAM-like NH smoke", lat_nh, lon, seed=1)
    run_one_mode("NAO-like NH smoke", lat_nh, lon, seed=2)
    run_one_mode("SAM-like SH smoke", lat_sh, lon, seed=3)


if __name__ == "__main__":
    main()
