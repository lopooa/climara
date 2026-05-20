from __future__ import annotations

import numpy as np
import matplotlib.colors as mcolors
from matplotlib.colors import ListedColormap
import cartopy.crs as ccrs

from ._colors import get_colormap
from ._labelbar import add_labelbar
from ._maps import create_map_axes
from ._resources import bool_resource, resolve_contour_levels, split_resources
from ._strings import add_gsn_strings
from ._utils import maybe_add_cyclic, mesh_lon_lat, to_numpy_data_lon_lat


_DASH_MAP = {
    0: "solid",
    1: "dashed",
    2: "dotted",
    3: "dashdot",
    4: "dashed",
    "solid": "solid",
    "dash": "dashed",
    "dashed": "dashed",
    "dot": "dotted",
    "dotted": "dotted",
    "dashdot": "dashdot",
}


def _normalize_extend(value):
    if value is None:
        return "both"

    value = str(value).lower()

    mapping = {
        "both": "both",
        "true": "both",
        "neither": "neither",
        "none": "neither",
        "false": "neither",
        "min": "min",
        "lower": "min",
        "max": "max",
        "upper": "max",
    }

    return mapping.get(value, "both")


def _needed_color_count(levels, extend):
    if levels is None:
        return None

    n_bins = max(len(levels) - 1, 1)

    if extend == "both":
        n_bins += 2
    elif extend in ["min", "max"]:
        n_bins += 1

    return n_bins


def _resample_cmap_if_needed(cmap, ncolors):
    if ncolors is None:
        return cmap

    if getattr(cmap, "N", ncolors) >= ncolors:
        return cmap

    if hasattr(cmap, "resampled"):
        return cmap.resampled(ncolors)

    colors = cmap(np.linspace(0, 1, ncolors))

    return ListedColormap(colors, name=f"{cmap.name}_{ncolors}")


def _get_fill_cmap(cnres, levels, extend):
    fill_colors = cnres.get("cnFillColors", None)

    if fill_colors is not None:
        cmap = ListedColormap(fill_colors, name="climara_cnFillColors")
    else:
        cmap = get_colormap(cnres.get("cnFillPalette", "viridis"))

    missing = cnres.get("cnMissingValFillColor", None)

    if missing is not None:
        cmap = cmap.copy()
        cmap.set_bad(missing)

    ncolors = _needed_color_count(levels, extend)
    cmap = _resample_cmap_if_needed(cmap, ncolors)

    return cmap


def _get_cmap_and_norm(levels, cmap, extend):
    if levels is None:
        return cmap, None

    norm = mcolors.BoundaryNorm(
        levels,
        ncolors=cmap.N,
        extend=extend,
    )

    return cmap, norm


def _map_dash(value):
    if isinstance(value, str):
        return _DASH_MAP.get(value.lower(), value)

    return _DASH_MAP.get(value, "solid")


def _as_list_or_value(value, mapper=None):
    if value is None:
        return None

    if isinstance(value, (list, tuple)):
        if mapper is None:
            return list(value)

        return [mapper(v) for v in value]

    if mapper is None:
        return value

    return mapper(value)


def _smooth_field(arr, cnres):
    if not bool_resource(cnres, "cnSmoothingOn", False):
        return arr

    sigma = float(cnres.get("cnSmoothingSigmaF", 1.0))

    try:
        from scipy.ndimage import gaussian_filter
    except Exception:
        return arr

    arr = np.asarray(arr, dtype=float)
    mask = np.isfinite(arr)

    filled = np.where(mask, arr, 0.0)
    weight = mask.astype(float)

    smooth_filled = gaussian_filter(filled, sigma=sigma, mode="nearest")
    smooth_weight = gaussian_filter(weight, sigma=sigma, mode="nearest")

    with np.errstate(invalid="ignore", divide="ignore"):
        out = smooth_filled / smooth_weight

    out[smooth_weight <= 0] = np.nan

    return out


def _is_constant_field(arr):
    finite = np.asarray(arr)[np.isfinite(arr)]

    if finite.size == 0:
        return False, np.nan

    vmin = np.nanmin(finite)
    vmax = np.nanmax(finite)

    return bool(np.isclose(vmin, vmax)), float(vmin)


def _add_const_label(ax, value, cnres):
    if not bool_resource(cnres, "cnConstFLabelOn", False):
        return None

    label = cnres.get("cnConstFLabelString", f"Constant field: {value:.3g}")

    return ax.text(
        float(cnres.get("cnConstFLabelXF", 0.5)),
        float(cnres.get("cnConstFLabelYF", 0.5)),
        label,
        transform=ax.transAxes,
        ha="center",
        va="center",
        fontsize=float(cnres.get("cnConstFLabelFontHeightF", 10)),
        color=cnres.get("cnConstFLabelFontColor", "black"),
        bbox={
            "facecolor": cnres.get("cnConstFLabelBackgroundColor", "white"),
            "edgecolor": cnres.get("cnConstFLabelPerimColor", "black"),
            "alpha": float(cnres.get("cnConstFLabelBackgroundAlphaF", 0.8)),
        },
        zorder=float(cnres.get("cnConstFLabelZOrder", 20)),
    )


def _add_info_label(ax, arr, cnres):
    if not bool_resource(cnres, "cnInfoLabelOn", False):
        return None

    label = cnres.get(
        "cnInfoLabelString",
        f"min={np.nanmin(arr):.3g}, max={np.nanmax(arr):.3g}",
    )

    just = str(cnres.get("cnInfoLabelJust", "bottom_left")).lower()

    if just in ["bottom_left", "left"]:
        x, y, ha, va = 0.01, 0.01, "left", "bottom"
    elif just in ["bottom_right", "right"]:
        x, y, ha, va = 0.99, 0.01, "right", "bottom"
    elif just in ["top_left"]:
        x, y, ha, va = 0.01, 0.99, "left", "top"
    elif just in ["top_right"]:
        x, y, ha, va = 0.99, 0.99, "right", "top"
    else:
        x, y, ha, va = 0.01, 0.01, "left", "bottom"

    return ax.text(
        float(cnres.get("cnInfoLabelXF", x)),
        float(cnres.get("cnInfoLabelYF", y)),
        label,
        transform=ax.transAxes,
        ha=ha,
        va=va,
        fontsize=float(cnres.get("cnInfoLabelFontHeightF", 8)),
        color=cnres.get("cnInfoLabelFontColor", "black"),
        bbox={
            "facecolor": cnres.get("cnInfoLabelBackgroundColor", "white"),
            "edgecolor": cnres.get("cnInfoLabelPerimColor", "none"),
            "alpha": float(cnres.get("cnInfoLabelBackgroundAlphaF", 0.7)),
        },
        zorder=float(cnres.get("cnInfoLabelZOrder", 20)),
    )


def _add_title(ax, tires, gsnres):
    if "tiMainString" not in tires:
        return None

    has_gsn_strings = any(
        key in gsnres
        for key in ["gsnLeftString", "gsnCenterString", "gsnRightString"]
    )

    default_y = 1.12 if has_gsn_strings else None

    kwargs = {
        "label": tires["tiMainString"],
        "fontsize": float(tires.get("tiMainFontHeightF", 11)),
        "pad": float(tires.get("tiMainOffsetYF", 6)),
    }

    if "tiMainYF" in tires:
        kwargs["y"] = float(tires["tiMainYF"])
    elif default_y is not None:
        kwargs["y"] = default_y

    return ax.set_title(**kwargs)


def _style_line_labels(labels, cnres):
    background = cnres.get("cnLineLabelBackgroundColor", None)

    if background is None:
        return labels

    for label in labels:
        label.set_bbox(
            {
                "facecolor": background,
                "edgecolor": cnres.get("cnLineLabelPerimColor", "none"),
                "alpha": float(cnres.get("cnLineLabelBackgroundAlphaF", 0.8)),
                "pad": float(cnres.get("cnLineLabelBackgroundPadF", 0.1)),
            }
        )

    return labels


def _handle_frame(fig, gsnres):
    frame_on = bool_resource(gsnres, "gsnFrame", False)

    if not frame_on:
        return None

    filename = (
        gsnres.get("gsnFrameFileName")
        or gsnres.get("gsnFrameFilename")
        or gsnres.get("gsnFrameFile")
    )

    if filename is None:
        return None

    dpi = int(gsnres.get("gsnFrameDpi", 300))
    bbox_inches = gsnres.get("gsnFrameBBoxInches", "tight")

    fig.savefig(filename, dpi=dpi, bbox_inches=bbox_inches)

    return filename


def ncl_contour_map(data, lon=None, lat=None, res=None, fig=None, ax=None):
    groups = split_resources(res)

    cnres = groups["contour"]
    mpres = groups["map"]
    tmres = groups["tickmark"]
    lbres = groups["labelbar"]
    pmres = groups["plotmanager"]
    tires = groups["title"]
    gsnres = groups["gsn"]

    mpres = {**mpres, **tmres}

    arr, lon, lat = to_numpy_data_lon_lat(data, lon=lon, lat=lat)
    arr = _smooth_field(arr, cnres)

    arr, lon = maybe_add_cyclic(
        arr,
        lon,
        add_cyclic=bool_resource(gsnres, "gsnAddCyclic", True),
    )

    fig, ax = create_map_axes(fig=fig, ax=ax, mpres=mpres)

    levels = resolve_contour_levels(cnres)
    extend = _normalize_extend(cnres.get("cnFillExtendMode", "both"))

    cmap = _get_fill_cmap(cnres, levels, extend)
    cmap, norm = _get_cmap_and_norm(levels, cmap, extend)

    is_const, const_value = _is_constant_field(arr)

    fill_on = bool_resource(cnres, "cnFillOn", True)
    lines_on = bool_resource(cnres, "cnLinesOn", False)
    line_labels_on = bool_resource(cnres, "cnLineLabelsOn", False)

    fill_mode = cnres.get("cnFillMode", "AreaFill")

    mappable = None
    contour_lines = None
    line_label_artists = []
    const_label = None

    if fill_on:
        if fill_mode in ["RasterFill", "CellFill", "PcolorFill", "Pcolormesh"]:
            lon2d, lat2d = mesh_lon_lat(lon, lat)

            mappable = ax.pcolormesh(
                lon2d,
                lat2d,
                arr,
                cmap=cmap,
                norm=norm,
                shading=cnres.get("cnRasterSmoothingOn", "auto"),
                edgecolors=cnres.get("cnCellFillEdgeColor", "none"),
                linewidth=float(cnres.get("cnCellFillEdgeThicknessF", 0.0)),
                transform=ccrs.PlateCarree(),
                zorder=float(cnres.get("cnFillZOrder", 3)),
            )
        else:
            try:
                mappable = ax.contourf(
                    lon,
                    lat,
                    arr,
                    levels=levels,
                    cmap=cmap,
                    norm=norm,
                    extend=extend,
                    transform=ccrs.PlateCarree(),
                    zorder=float(cnres.get("cnFillZOrder", 3)),
                )
            except TypeError as exc:
                if "GeometryCollection" not in str(exc):
                    raise

                lon2d, lat2d = mesh_lon_lat(lon, lat)

                mappable = ax.pcolormesh(
                    lon2d,
                    lat2d,
                    arr,
                    cmap=cmap,
                    norm=norm,
                    shading="auto",
                    transform=ccrs.PlateCarree(),
                    zorder=float(cnres.get("cnFillZOrder", 3)),
                )

    if lines_on and not is_const:
        line_colors = cnres.get("cnLineColors", cnres.get("cnLineColor", "black"))
        line_thicknesses = cnres.get(
            "cnLineThicknesses",
            cnres.get("cnLineThicknessF", 0.5),
        )
        line_patterns = cnres.get(
            "cnLineDashPatterns",
            cnres.get("cnLineDashPattern", "solid"),
        )

        contour_lines = ax.contour(
            lon,
            lat,
            arr,
            levels=levels,
            colors=_as_list_or_value(line_colors),
            linewidths=_as_list_or_value(line_thicknesses),
            linestyles=_as_list_or_value(line_patterns, mapper=_map_dash),
            transform=ccrs.PlateCarree(),
            zorder=float(cnres.get("cnLineZOrder", 5)),
        )

        if line_labels_on:
            interval = int(cnres.get("cnLineLabelInterval", 1))

            if interval < 1:
                interval = 1

            label_levels = contour_lines.levels[::interval]

            line_label_artists = ax.clabel(
                contour_lines,
                label_levels,
                inline=bool_resource(cnres, "cnLineLabelPlacementInline", True),
                fontsize=float(cnres.get("cnLineLabelFontHeightF", 8)),
                fmt=cnres.get("cnLineLabelFormat", "%g"),
            )

            _style_line_labels(line_label_artists, cnres)

    if is_const:
        const_label = _add_const_label(ax, const_value, cnres)

    _add_title(ax, tires, gsnres)
    string_artists = add_gsn_strings(ax, gsnres)

    info_label = _add_info_label(ax, arr, cnres)

    cbar = None

    if bool_resource(lbres, "lbLabelBarOn", True) and mappable is not None:
        cbar = add_labelbar(fig, ax, mappable, lbres, pmres=pmres)

    frame_file = _handle_frame(fig, gsnres)

    return fig, ax, {
        "mappable": mappable,
        "contour_lines": contour_lines,
        "line_label_artists": line_label_artists,
        "constant_label": const_label,
        "info_label": info_label,
        "colorbar": cbar,
        "string_artists": string_artists,
        "frame_file": frame_file,
        "groups": groups,
    }
