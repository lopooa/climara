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
from ._utils import maybe_add_cyclic, mesh_lon_lat
from ._workflow import apply_gsn_workflow


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


def _get_coord(data, names):
    if not hasattr(data, "coords"):
        return None

    for name in names:
        if name in data.coords:
            return np.asarray(data.coords[name])

    return None


def _prepare_contour_data(data, lon=None, lat=None):
    arr = getattr(data, "values", data)
    arr = np.asarray(arr, dtype=float)
    arr = np.squeeze(arr)

    if arr.ndim != 2:
        raise ValueError(
            f"ContourPlot only supports 2-D data after squeeze, got shape {arr.shape}"
        )

    if lon is None:
        lon = _get_coord(data, ["lon", "longitude", "x"])

    if lat is None:
        lat = _get_coord(data, ["lat", "latitude", "y"])

    if lon is None:
        lon = np.arange(arr.shape[1], dtype=float)

    if lat is None:
        lat = np.arange(arr.shape[0], dtype=float)

    lon = np.asarray(lon, dtype=float)
    lat = np.asarray(lat, dtype=float)

    arr = np.ma.masked_invalid(arr)

    return arr, lon, lat


def _finite_minmax(arr):
    values = np.asarray(arr, dtype=float)
    finite = values[np.isfinite(values)]

    if finite.size == 0:
        return None, None, True

    vmin = float(finite.min())
    vmax = float(finite.max())
    is_constant = bool(np.isclose(vmin, vmax))

    return vmin, vmax, is_constant


def _as_float_list(values):
    if values is None:
        return None

    if isinstance(values, str):
        values = values.replace(",", " ").split()

    try:
        return [float(v) for v in values]
    except TypeError:
        return [float(values)]


def _build_contour_levels(arr, cnres):
    cnres = dict(cnres or {})
    vmin, vmax, is_constant = _finite_minmax(arr)

    resolved = resolve_contour_levels(cnres)

    if resolved is not None and len(resolved) >= 2:
        return np.asarray(resolved, dtype=float), is_constant

    explicit = _as_float_list(cnres.get("cnExplicitLevels", None))

    if explicit is not None and len(explicit) >= 2:
        return np.asarray(explicit, dtype=float), is_constant

    if vmin is None or vmax is None:
        return np.asarray([0.0, 1.0], dtype=float), True

    if is_constant:
        center = vmin
        width = abs(center) * 0.05

        if width == 0:
            width = 1.0

        spacing = float(cnres.get("cnLevelSpacingF", width / 2.0))
        lo = float(cnres.get("cnMinLevelValF", center - width))
        hi = float(cnres.get("cnMaxLevelValF", center + width))

        if spacing <= 0:
            spacing = width / 2.0

        if lo == hi:
            lo = center - width
            hi = center + width

        levels = np.arange(lo, hi + spacing * 0.5, spacing, dtype=float)

        if levels.size < 2:
            levels = np.asarray([center - width, center + width], dtype=float)

        return levels, True

    count = max(3, int(cnres.get("cnMaxLevelCount", 11)))
    levels = np.linspace(vmin, vmax, count, dtype=float)

    if levels.size < 2:
        levels = np.asarray([vmin, vmax], dtype=float)

    return levels, False


def _normalize_extend(value):
    if value is None:
        return "both"

    value = str(value).lower()

    aliases = {
        "both": "both",
        "true": "both",
        "minmax": "both",
        "neither": "neither",
        "none": "neither",
        "false": "neither",
        "no": "neither",
        "min": "min",
        "lower": "min",
        "max": "max",
        "upper": "max",
    }

    return aliases.get(value, "both")


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
        cmap = ListedColormap(list(fill_colors), name="climara_cnFillColors")
    else:
        palette = cnres.get("cnFillPalette", "viridis")

        try:
            cmap = get_colormap(palette)
        except Exception:
            import matplotlib.pyplot as plt

            cmap = plt.get_cmap(palette)

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

    values = np.asarray(arr, dtype=float)
    mask = np.isfinite(values)

    filled = np.where(mask, values, 0.0)
    weight = mask.astype(float)

    smooth_filled = gaussian_filter(filled, sigma=sigma, mode="nearest")
    smooth_weight = gaussian_filter(weight, sigma=sigma, mode="nearest")

    with np.errstate(invalid="ignore", divide="ignore"):
        out = smooth_filled / smooth_weight

    out[smooth_weight <= 0] = np.nan

    return np.ma.masked_invalid(out)


def _is_geoaxes(ax):
    return hasattr(ax, "projection")


def _data_transform(ax):
    if _is_geoaxes(ax):
        return ccrs.PlateCarree()

    return None


def _normalize_fill_mode(cnres):
    mode = str(cnres.get("cnFillMode", "AreaFill"))
    key = mode.replace("_", "").replace("-", "").replace(" ", "").lower()

    if key in ["rasterfill", "cellfill", "pcolorfill", "pcolormesh"]:
        return "pcolormesh"

    if key in ["contourf", "areafill", "area", "auto"]:
        return "contourf"

    return "contourf"


def _pcolormesh_shading(cnres):
    if "cnPcolormeshShading" in cnres:
        return cnres["cnPcolormeshShading"]

    if bool_resource(cnres, "cnRasterSmoothingOn", False):
        return "gouraud"

    return "auto"


def _draw_contour_fill(
    ax,
    lon,
    lat,
    arr,
    levels,
    cnres,
    cmap,
    norm,
    extend,
    is_constant,
):
    if not bool_resource(cnres, "cnFillOn", True):
        return None, None

    mode = _normalize_fill_mode(cnres)
    transform = _data_transform(ax)

    kwargs = {
        "cmap": cmap,
        "norm": norm,
        "zorder": float(cnres.get("cnFillZOrder", 3)),
    }

    if transform is not None:
        kwargs["transform"] = transform

    if is_constant:
        constant_mode = str(cnres.get("cnConstantFieldMode", "Fill")).lower()

        if constant_mode in ["skip", "none", "off"]:
            return None, None

        mode = "pcolormesh"

    if mode == "pcolormesh":
        lon2d, lat2d = mesh_lon_lat(lon, lat)

        mappable = ax.pcolormesh(
            lon2d,
            lat2d,
            arr,
            shading=_pcolormesh_shading(cnres),
            edgecolors=cnres.get("cnCellFillEdgeColor", "none"),
            linewidth=float(cnres.get("cnCellFillEdgeThicknessF", 0.0)),
            **kwargs,
        )

        return mappable, "pcolormesh"

    try:
        mappable = ax.contourf(
            lon,
            lat,
            arr,
            levels=levels,
            extend=extend,
            **kwargs,
        )

        return mappable, "contourf"

    except Exception:
        fallback = str(cnres.get("cnFillFallbackMode", "Pcolormesh")).lower()

        if fallback in ["none", "off", "raise"]:
            raise

        lon2d, lat2d = mesh_lon_lat(lon, lat)

        mappable = ax.pcolormesh(
            lon2d,
            lat2d,
            arr,
            shading=_pcolormesh_shading(cnres),
            **kwargs,
        )

        return mappable, "pcolormesh"


def _style_line_labels(labels, cnres):
    background = cnres.get("cnLineLabelBackgroundColor", None)

    for label in labels:
        if "cnLineLabelFontColor" in cnres:
            label.set_color(cnres["cnLineLabelFontColor"])

        if background is not None:
            label.set_bbox(
                {
                    "facecolor": background,
                    "edgecolor": cnres.get("cnLineLabelPerimColor", "none"),
                    "alpha": float(cnres.get("cnLineLabelBackgroundAlphaF", 0.8)),
                    "pad": float(cnres.get("cnLineLabelBackgroundPadF", 0.1)),
                }
            )

    return labels


def _draw_contour_lines(ax, lon, lat, arr, levels, cnres, is_constant):
    line_labels_on = bool_resource(cnres, "cnLineLabelsOn", False)
    lines_on = bool_resource(cnres, "cnLinesOn", False) or line_labels_on

    if not lines_on or is_constant:
        return None, []

    transform = _data_transform(ax)

    line_colors = cnres.get("cnLineColors", cnres.get("cnLineColor", "black"))
    line_thicknesses = cnres.get(
        "cnLineThicknesses",
        cnres.get("cnLineThicknessF", 0.6),
    )
    line_patterns = cnres.get(
        "cnLineDashPatterns",
        cnres.get("cnLineDashPattern", "solid"),
    )

    kwargs = {
        "levels": levels,
        "colors": _as_list_or_value(line_colors),
        "linewidths": _as_list_or_value(line_thicknesses),
        "linestyles": _as_list_or_value(line_patterns, mapper=_map_dash),
        "zorder": float(cnres.get("cnLineZOrder", 5)),
    }

    if transform is not None:
        kwargs["transform"] = transform

    contour = ax.contour(lon, lat, arr, **kwargs)
    label_artists = []

    if line_labels_on:
        interval = max(1, int(cnres.get("cnLineLabelInterval", 1)))
        label_levels = contour.levels[::interval]

        label_artists = ax.clabel(
            contour,
            label_levels,
            inline=bool_resource(cnres, "cnLineLabelPlacementInline", True),
            inline_spacing=float(cnres.get("cnLineLabelInlineSpacingF", 4.0)),
            fontsize=float(cnres.get("cnLineLabelFontHeightF", 8)),
            fmt=cnres.get("cnLineLabelFormat", "%g"),
        )

        _style_line_labels(label_artists, cnres)

    return contour, label_artists


def _add_constant_label(ax, value, cnres, is_constant):
    if not is_constant:
        return None

    if not bool_resource(cnres, "cnConstFLabelOn", False):
        return None

    label = cnres.get("cnConstFLabelString", f"constant field = {value:.4g}")

    return ax.text(
        float(cnres.get("cnConstFLabelXF", 0.5)),
        float(cnres.get("cnConstFLabelYF", 0.5)),
        str(label),
        transform=ax.transAxes,
        ha="center",
        va="center",
        fontsize=float(cnres.get("cnConstFLabelFontHeightF", 10)),
        color=cnres.get("cnConstFLabelFontColor", "black"),
        bbox={
            "facecolor": cnres.get("cnConstFLabelBackgroundColor", "white"),
            "edgecolor": cnres.get("cnConstFLabelPerimColor", "0.4"),
            "alpha": float(cnres.get("cnConstFLabelBackgroundAlphaF", 0.75)),
            "pad": float(cnres.get("cnConstFLabelBackgroundPadF", 0.3)),
        },
        zorder=float(cnres.get("cnConstFLabelZOrder", 30)),
    )


def _add_info_label(ax, arr, levels, cnres, is_constant):
    if not bool_resource(cnres, "cnInfoLabelOn", False):
        return None

    vmin, vmax, _ = _finite_minmax(arr)
    label = cnres.get("cnInfoLabelString", None)

    if label is None:
        if is_constant:
            label = f"constant field = {vmin:.4g}"
        elif levels is not None and len(levels) >= 2:
            spacing = levels[1] - levels[0]
            label = f"min={vmin:.3g}, max={vmax:.3g}, interval={spacing:.3g}"
        else:
            label = f"min={vmin:.3g}, max={vmax:.3g}"

    if "cnInfoLabelParallelPosF" in cnres or "cnInfoLabelOrthogonalPosF" in cnres:
        x = float(cnres.get("cnInfoLabelParallelPosF", 0.98))
        y = float(cnres.get("cnInfoLabelOrthogonalPosF", 0.02))
    else:
        just0 = str(cnres.get("cnInfoLabelJust", "bottom_left")).lower()

        if just0 in ["bottom_left", "left"]:
            x, y = 0.01, 0.01
        elif just0 in ["bottom_right", "right"]:
            x, y = 0.99, 0.01
        elif just0 in ["top_left"]:
            x, y = 0.01, 0.99
        elif just0 in ["top_right"]:
            x, y = 0.99, 0.99
        else:
            x, y = 0.98, 0.02

    just = str(cnres.get("cnInfoLabelJust", "BottomRight")).lower()

    if "left" in just:
        ha = "left"
    elif "center" in just:
        ha = "center"
    else:
        ha = "right"

    if "top" in just:
        va = "top"
    elif "center" in just:
        va = "center"
    else:
        va = "bottom"

    bbox = None

    if bool_resource(cnres, "cnInfoLabelPerimOn", True):
        bbox = {
            "facecolor": cnres.get("cnInfoLabelBackgroundColor", "white"),
            "edgecolor": cnres.get("cnInfoLabelPerimColor", "0.4"),
            "linewidth": float(cnres.get("cnInfoLabelPerimThicknessF", 0.5)),
            "alpha": float(cnres.get("cnInfoLabelBackgroundAlphaF", 0.75)),
            "pad": float(cnres.get("cnInfoLabelBackgroundPadF", 0.25)),
        }

    return ax.text(
        x,
        y,
        str(label),
        transform=ax.transAxes,
        ha=ha,
        va=va,
        fontsize=float(cnres.get("cnInfoLabelFontHeightF", 8.0)),
        color=cnres.get("cnInfoLabelFontColor", "black"),
        bbox=bbox,
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


def ncl_contour_map(data, lon=None, lat=None, res=None, fig=None, ax=None, wks=None):
    """
    Draw an NCL-style contour map using one unified contour workflow.
    """
    res = dict(res or {})
    groups = split_resources(res)

    cnres = groups["contour"]
    mpres = groups["map"]
    tmres = groups["tickmark"]
    lbres = groups["labelbar"]
    pmres = groups["plotmanager"]
    tires = groups["title"]
    gsnres = groups["gsn"]

    mpres = {**mpres, **tmres}

    if bool_resource(gsnres, "gsnPolar", False):
        polar_keys = [
            "gsnPolar",
            "gsnPolarLabelOn",
            "gsnPolarLabelDistance",
            "gsnPolarLabelFontHeightF",
            "gsnPolarLabelFontColor",
            "gsnPolarLongitudeLabelsOn",
            "gsnPolarLongitudeLabelValues",
            "gsnPolarLatitudeLabelOn",
            "gsnPolarLatitudeLabelString",
            "gsnPolarLatitudeLabelPosition",
            "gsnPolarLatitudeLabelDistance",
            "gsnPolarBoundaryOn",
            "mpPolarHideRectangularFrameOn",
            "gsnPolarBottomLabelYF",
            "gsnPolarClampBottomLabelsOn",
            "gsnPolarLatitudeLabelYF",
        ]

        for key in polar_keys:
            if key in gsnres:
                mpres[key] = gsnres[key]

        if "gsnPolarBoundaryOn" in gsnres:
            mpres["mpPolarBoundaryOn"] = gsnres["gsnPolarBoundaryOn"]

        if "mpPolarHideRectangularFrameOn" in gsnres:
            mpres["mpPolarHideRectangularFrameOn"] = gsnres["mpPolarHideRectangularFrameOn"]

        mpres.setdefault("mpPolarBoundaryOn", True)
        mpres.setdefault("mpPolarHideRectangularFrameOn", True)

    arr, lon, lat = _prepare_contour_data(data, lon=lon, lat=lat)
    arr = _smooth_field(arr, cnres)

    if lon.ndim == 1:
        arr, lon = maybe_add_cyclic(
            arr,
            lon,
            add_cyclic=bool_resource(gsnres, "gsnAddCyclic", True),
        )

    levels, is_constant = _build_contour_levels(arr, cnres)
    extend = _normalize_extend(
        cnres.get("cnFillExtendMode", cnres.get("cnExtendMode", "both"))
    )

    cmap = _get_fill_cmap(cnres, levels, extend)
    cmap, norm = _get_cmap_and_norm(levels, cmap, extend)

    fig, ax = create_map_axes(fig=fig, ax=ax, mpres=mpres)

    mappable, fill_method = _draw_contour_fill(
        ax,
        lon,
        lat,
        arr,
        levels,
        cnres,
        cmap,
        norm,
        extend,
        is_constant,
    )

    contour_lines, line_label_artists = _draw_contour_lines(
        ax,
        lon,
        lat,
        arr,
        levels,
        cnres,
        is_constant,
    )

    const_value, _, _ = _finite_minmax(arr)
    constant_label = _add_constant_label(ax, const_value, cnres, is_constant)
    info_label = _add_info_label(ax, arr, levels, cnres, is_constant)
    title_artist = _add_title(ax, tires, gsnres)
    string_artists = add_gsn_strings(ax, gsnres)

    cbar = None

    if bool_resource(lbres, "lbLabelBarOn", True) and mappable is not None:
        cbar = add_labelbar(fig, ax, mappable, lbres, pmres=pmres)

    out = {
        "mappable": mappable,
        "contour": contour_lines,
        "contour_lines": contour_lines,
        "colorbar": cbar,
        "line_label_artists": line_label_artists,
        "constant_label": constant_label,
        "info_label": info_label,
        "title_artist": title_artist,
        "string_artists": string_artists,
        "levels": levels,
        "is_constant": is_constant,
        "fill_method": fill_method,
        "groups": groups,
    }

    fig, ax, out = apply_gsn_workflow(
        fig,
        ax=ax,
        out=out,
        gsnres=gsnres,
        wks=wks,
    )

    return fig, ax, out


gsn_csm_contour_map = ncl_contour_map
gsn_csm_contour = ncl_contour_map
