from __future__ import annotations

import numpy as np
import matplotlib.patches as mpatches
import cartopy.crs as ccrs

from ._colors import get_colormap
from ._resources import bool_resource, resolve_contour_levels
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

_MARKER_MAP = {
    0: "o",
    1: "o",
    2: "+",
    3: "x",
    4: "*",
    5: "s",
    6: "D",
    7: "^",
    8: "v",
    9: "<",
    10: ">",
    11: "p",
    12: "h",
    13: "H",
    14: "1",
    15: "2",
    16: "o",
}


def _map_dash(value):
    if isinstance(value, str):
        return _DASH_MAP.get(value.lower(), value)

    return _DASH_MAP.get(value, "solid")


def _map_marker(value):
    if isinstance(value, str):
        return value

    return _MARKER_MAP.get(value, "o")


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


def _tx_just_to_align(just):
    just = str(just).lower()

    ha = "center"
    va = "center"

    if "left" in just:
        ha = "left"
    elif "right" in just:
        ha = "right"
    elif "center" in just:
        ha = "center"

    if "top" in just:
        va = "top"
    elif "bottom" in just:
        va = "bottom"
    elif "center" in just:
        va = "center"

    return ha, va


def overlay_contour(ax, data, lon=None, lat=None, res=None):
    """
    Overlay contour lines on an existing map axes.

    Supported resources
    -------------------
    cnLevelSelectionMode
    cnLevels
    cnMinLevelValF
    cnMaxLevelValF
    cnLevelSpacingF
    cnLineColor
    cnLineColors
    cnLineThicknessF
    cnLineThicknesses
    cnLineDashPattern
    cnLineDashPatterns
    cnLineLabelsOn
    cnLineLabelInterval
    cnLineLabelFontHeightF
    cnLineLabelFormat
    cnLineLabelBackgroundColor
    gsnAddCyclic
    """
    if res is None:
        res = {}

    arr, lon, lat = to_numpy_data_lon_lat(data, lon=lon, lat=lat)

    arr, lon = maybe_add_cyclic(
        arr,
        lon,
        add_cyclic=bool_resource(res, "gsnAddCyclic", True),
    )

    levels = resolve_contour_levels(res)

    line_colors = res.get("cnLineColors", res.get("cnLineColor", "black"))
    line_thicknesses = res.get(
        "cnLineThicknesses",
        res.get("cnLineThicknessF", 0.7),
    )
    line_patterns = res.get(
        "cnLineDashPatterns",
        res.get("cnLineDashPattern", "solid"),
    )

    cs = ax.contour(
        lon,
        lat,
        arr,
        levels=levels,
        colors=_as_list_or_value(line_colors),
        linewidths=_as_list_or_value(line_thicknesses),
        linestyles=_as_list_or_value(line_patterns, mapper=_map_dash),
        transform=ccrs.PlateCarree(),
        zorder=float(res.get("cnZOrder", res.get("cnLineZOrder", 8))),
    )

    labels = []

    if bool_resource(res, "cnLineLabelsOn", False):
        interval = int(res.get("cnLineLabelInterval", 1))

        if interval < 1:
            interval = 1

        label_levels = cs.levels[::interval]

        labels = ax.clabel(
            cs,
            label_levels,
            inline=bool_resource(res, "cnLineLabelPlacementInline", True),
            fontsize=float(res.get("cnLineLabelFontHeightF", 8)),
            fmt=res.get("cnLineLabelFormat", "%g"),
        )

        background = res.get("cnLineLabelBackgroundColor", None)

        if background is not None:
            for label in labels:
                label.set_bbox(
                    {
                        "facecolor": background,
                        "edgecolor": res.get("cnLineLabelPerimColor", "none"),
                        "alpha": float(res.get("cnLineLabelBackgroundAlphaF", 0.85)),
                        "pad": float(res.get("cnLineLabelBackgroundPadF", 0.1)),
                    }
                )

    return {
        "contour": cs,
        "labels": labels,
    }


def overlay_filled_contour(ax, data, lon=None, lat=None, res=None):
    """
    Overlay filled contours on an existing map axes.
    """
    if res is None:
        res = {}

    arr, lon, lat = to_numpy_data_lon_lat(data, lon=lon, lat=lat)

    arr, lon = maybe_add_cyclic(
        arr,
        lon,
        add_cyclic=bool_resource(res, "gsnAddCyclic", True),
    )

    levels = resolve_contour_levels(res)
    cmap = get_colormap(res.get("cnFillPalette", "viridis"))

    fill_mode = res.get("cnFillMode", "AreaFill")

    if fill_mode in ["RasterFill", "CellFill", "PcolorFill", "Pcolormesh"]:
        return overlay_pcolormesh(ax, arr, lon=lon, lat=lat, res=res)

    cs = ax.contourf(
        lon,
        lat,
        arr,
        levels=levels,
        cmap=cmap,
        alpha=float(res.get("cnFillAlphaF", 1.0)),
        extend=res.get("cnFillExtendMode", "both"),
        transform=ccrs.PlateCarree(),
        zorder=float(res.get("cnFillZOrder", 4)),
    )

    return cs


def overlay_pcolormesh(ax, data, lon=None, lat=None, res=None):
    """
    Overlay raster-like field on an existing map axes.
    """
    if res is None:
        res = {}

    arr, lon, lat = to_numpy_data_lon_lat(data, lon=lon, lat=lat)

    arr, lon = maybe_add_cyclic(
        arr,
        lon,
        add_cyclic=bool_resource(res, "gsnAddCyclic", True),
    )

    levels = resolve_contour_levels(res)
    cmap = get_colormap(res.get("cnFillPalette", "viridis"))

    norm = None

    if levels is not None:
        import matplotlib.colors as mcolors

        norm = mcolors.BoundaryNorm(levels, cmap.N)

    lon2d, lat2d = mesh_lon_lat(lon, lat)

    mesh = ax.pcolormesh(
        lon2d,
        lat2d,
        arr,
        cmap=cmap,
        norm=norm,
        alpha=float(res.get("cnFillAlphaF", 1.0)),
        shading=res.get("cnRasterSmoothingOn", "auto"),
        transform=ccrs.PlateCarree(),
        zorder=float(res.get("cnFillZOrder", 4)),
    )

    return mesh


def overlay_vectors(ax, u, v, lon=None, lat=None, res=None):
    """
    Overlay vectors with quiver.

    Supported resources
    -------------------
    vcMinDistanceF
    vcVectorColor
    vcVectorScaleF
    vcLineArrowThicknessF
    vcRefAnnoOn
    vcRefMagnitudeF
    vcRefAnnoString
    vcRefAnnoXF
    vcRefAnnoYF
    """
    if res is None:
        res = {}

    u, lon, lat = to_numpy_data_lon_lat(u, lon=lon, lat=lat)
    v = np.asarray(v.values if hasattr(v, "values") else v)

    stride = int(res.get("vcMinDistanceF", 1))

    if stride < 1:
        stride = 1

    lon2d, lat2d = np.meshgrid(lon, lat)

    q = ax.quiver(
        lon2d[::stride, ::stride],
        lat2d[::stride, ::stride],
        u[::stride, ::stride],
        v[::stride, ::stride],
        color=res.get("vcVectorColor", "black"),
        scale=res.get("vcVectorScaleF", None),
        width=float(res.get("vcLineArrowThicknessF", 0.0025)),
        alpha=float(res.get("vcVectorAlphaF", 1.0)),
        transform=ccrs.PlateCarree(),
        zorder=float(res.get("vcZOrder", 9)),
    )

    qk = None

    if bool_resource(res, "vcRefAnnoOn", False):
        ref = float(res.get("vcRefMagnitudeF", 1.0))
        label = res.get("vcRefAnnoString", f"{ref:g}")

        qk = ax.quiverkey(
            q,
            float(res.get("vcRefAnnoXF", 0.88)),
            float(res.get("vcRefAnnoYF", -0.08)),
            ref,
            label,
            labelpos=res.get("vcRefAnnoLabelPos", "E"),
            coordinates="axes",
            fontproperties={
                "size": float(res.get("vcRefAnnoFontHeightF", 9)),
            },
        )

    return {
        "quiver": q,
        "quiverkey": qk,
    }


def overlay_markers(ax, x, y, res=None, values=None):
    """
    Overlay markers on an existing map axes.

    Supported resources
    -------------------
    gsMarkerIndex
    gsMarkerColor
    gsMarkerSizeF
    gsMarkerAlphaF
    gsMarkerEdgeColor
    gsMarkerLineThicknessF
    """
    if res is None:
        res = {}

    marker = _map_marker(res.get("gsMarkerIndex", "o"))
    color = res.get("gsMarkerColor", "black")
    size = float(res.get("gsMarkerSizeF", 20))
    alpha = float(res.get("gsMarkerAlphaF", 1.0))
    edgecolor = res.get("gsMarkerEdgeColor", color)
    linewidth = float(res.get("gsMarkerLineThicknessF", 0.0))

    sc = ax.scatter(
        x,
        y,
        c=values if values is not None else color,
        s=size,
        marker=marker,
        alpha=alpha,
        edgecolors=edgecolor,
        linewidths=linewidth,
        transform=ccrs.PlateCarree(),
        zorder=float(res.get("gsMarkerZOrder", 10)),
    )

    return sc


def overlay_text(ax, x, y, text, res=None):
    """
    Overlay text on an existing map axes.

    Supported resources
    -------------------
    txFontHeightF
    txFontColor
    txJust
    txAngleF
    txFontWeight
    txBackgroundFillColor
    txPerimColor
    """
    if res is None:
        res = {}

    ha, va = _tx_just_to_align(res.get("txJust", "CenterCenter"))

    bbox = None

    if "txBackgroundFillColor" in res:
        bbox = {
            "facecolor": res.get("txBackgroundFillColor", "white"),
            "edgecolor": res.get("txPerimColor", "none"),
            "alpha": float(res.get("txBackgroundAlphaF", 0.8)),
            "pad": float(res.get("txBackgroundPadF", 0.2)),
        }

    txt = ax.text(
        x,
        y,
        text,
        ha=ha,
        va=va,
        color=res.get("txFontColor", "black"),
        fontsize=float(res.get("txFontHeightF", 10)),
        fontweight=res.get("txFontWeight", "normal"),
        rotation=float(res.get("txAngleF", 0.0)),
        bbox=bbox,
        transform=ccrs.PlateCarree(),
        zorder=float(res.get("txZOrder", 11)),
        clip_on=bool_resource(res, "txClipOn", False),
    )

    return txt


def overlay_polyline(ax, x, y, res=None):
    """
    Overlay a polyline.

    Supported resources
    -------------------
    gsLineColor
    gsLineThicknessF
    gsLineDashPattern
    gsLineAlphaF
    gsLineMarker
    """
    if res is None:
        res = {}

    line = ax.plot(
        x,
        y,
        color=res.get("gsLineColor", "black"),
        linewidth=float(res.get("gsLineThicknessF", 1.0)),
        linestyle=_map_dash(res.get("gsLineDashPattern", "solid")),
        alpha=float(res.get("gsLineAlphaF", 1.0)),
        marker=res.get("gsLineMarker", None),
        transform=ccrs.PlateCarree(),
        zorder=float(res.get("gsLineZOrder", 9)),
    )

    return line


def overlay_polygon(ax, xy, res=None):
    """
    Overlay a polygon in lon/lat coordinates.

    Supported resources
    -------------------
    gsFillColor
    gsFillOpacityF
    gsEdgeColor
    gsLineThicknessF
    gsLineDashPattern
    """
    if res is None:
        res = {}

    patch = mpatches.Polygon(
        xy,
        closed=bool_resource(res, "gsPolygonClosed", True),
        facecolor=res.get("gsFillColor", "none"),
        edgecolor=res.get("gsEdgeColor", res.get("gsLineColor", "black")),
        linewidth=float(res.get("gsLineThicknessF", 1.0)),
        linestyle=_map_dash(res.get("gsLineDashPattern", "solid")),
        alpha=float(res.get("gsFillOpacityF", 1.0)),
        transform=ccrs.PlateCarree(),
        zorder=float(res.get("gsPolygonZOrder", 9)),
    )

    ax.add_patch(patch)

    return patch


def overlay_rectangle(ax, x0, y0, x1, y1, res=None):
    """
    Overlay a rectangle in lon/lat coordinates.
    """
    if res is None:
        res = {}

    width = x1 - x0
    height = y1 - y0

    patch = mpatches.Rectangle(
        (x0, y0),
        width,
        height,
        facecolor=res.get("gsFillColor", "none"),
        edgecolor=res.get("gsEdgeColor", res.get("gsLineColor", "black")),
        linewidth=float(res.get("gsLineThicknessF", 1.0)),
        linestyle=_map_dash(res.get("gsLineDashPattern", "solid")),
        alpha=float(res.get("gsFillOpacityF", 1.0)),
        transform=ccrs.PlateCarree(),
        zorder=float(res.get("gsRectangleZOrder", 9)),
    )

    ax.add_patch(patch)

    return patch


add_contour_overlay = overlay_contour
add_filled_contour_overlay = overlay_filled_contour
add_marker_overlay = overlay_markers
add_markers = overlay_markers
add_text_overlay = overlay_text
add_text = overlay_text
add_vector_overlay = overlay_vectors
add_vectors = overlay_vectors
overlay_quiver = overlay_vectors
add_polyline = overlay_polyline
add_polygon = overlay_polygon
add_rectangle = overlay_rectangle

# climara v0.2.6 overlay resource override begin

def _v026_transform(ax, res=None, default="data"):
    res = dict(res or {})
    mode = str(
        res.get(
            "gsCoordinateMode",
            res.get("txCoordinateMode", res.get("vcCoordinateMode", default)),
        )
    ).lower()

    if mode in ["axes", "axis", "normalized", "ndc", "figureaxes"]:
        return ax.transAxes

    if mode in ["figure", "fig"]:
        return ax.figure.transFigure

    if hasattr(ax, "projection"):
        return ccrs.PlateCarree()

    return ax.transData


def _v026_is_geo_transform(transform):
    return isinstance(transform, ccrs.CRS)


def _v026_to_array(value):
    if value is None:
        return None

    if hasattr(value, "values"):
        value = value.values

    return np.asarray(value)


def _v026_subsample_xy(x, y, stride=1):
    x = np.asarray(x)
    y = np.asarray(y)

    stride = max(1, int(stride))

    return x[::stride], y[::stride]


def _v026_subsample_2d(arr, stride_y=1, stride_x=1):
    arr = np.asarray(arr)
    stride_y = max(1, int(stride_y))
    stride_x = max(1, int(stride_x))

    return arr[::stride_y, ::stride_x]


def _v026_build_norm(values, res, prefix="gsMarker"):
    if values is None:
        return None

    vmin = res.get(f"{prefix}MinValF", res.get("gsMarkerMinValF", None))
    vmax = res.get(f"{prefix}MaxValF", res.get("gsMarkerMaxValF", None))

    if vmin is None and vmax is None:
        return None

    import matplotlib.colors as mcolors

    return mcolors.Normalize(
        vmin=None if vmin is None else float(vmin),
        vmax=None if vmax is None else float(vmax),
    )


def _v026_get_cmap(res, key="gsMarkerPalette", default="viridis"):
    palette = res.get(key, default)

    try:
        return get_colormap(palette)
    except Exception:
        import matplotlib.pyplot as plt

        return plt.get_cmap(palette)


def _v026_apply_clip(artist, res, key="gsClipOn"):
    clip_on = bool_resource(res, key, bool_resource(res, "gsClipOn", True))

    try:
        artist.set_clip_on(clip_on)
    except Exception:
        pass

    return artist


def overlay_markers(ax, x, y, res=None, values=None, mask=None):
    """Overlay markers with NCL-style gsMarker resources."""
    res = dict(res or {})

    x = _v026_to_array(x)
    y = _v026_to_array(y)

    if mask is not None:
        mask = np.asarray(mask).astype(bool)
        x = x[mask]
        y = y[mask]

        if values is not None:
            values = np.asarray(values)[mask]

    stride = int(res.get("gsMarkerStride", res.get("gsMarkerSkip", 1)))

    if stride > 1:
        x, y = _v026_subsample_xy(x, y, stride=stride)

        if values is not None:
            values = np.asarray(values)[::stride]

    marker = _map_marker(res.get("gsMarkerIndex", res.get("gsMarkerType", "o")))
    size = float(res.get("gsMarkerSizeF", res.get("gsMarkerSize", 24)))
    alpha = float(res.get("gsMarkerAlphaF", res.get("gsMarkerOpacityF", 1.0)))
    linewidth = float(res.get("gsMarkerLineThicknessF", res.get("gsMarkerEdgeThicknessF", 0.8)))
    zorder = float(res.get("gsMarkerZOrder", res.get("gsZOrder", 20)))

    transform = _v026_transform(ax, res)

    color = res.get("gsMarkerColor", "black")
    edgecolor = res.get("gsMarkerEdgeColor", color)

    kwargs = {
        "s": size,
        "marker": marker,
        "alpha": alpha,
        "edgecolors": edgecolor,
        "linewidths": linewidth,
        "zorder": zorder,
    }

    if _v026_is_geo_transform(transform):
        kwargs["transform"] = transform
    else:
        kwargs["transform"] = transform

    if values is not None:
        kwargs["c"] = values
        kwargs["cmap"] = _v026_get_cmap(res, key="gsMarkerPalette")
        norm = _v026_build_norm(values, res, prefix="gsMarker")

        if norm is not None:
            kwargs["norm"] = norm
    else:
        kwargs["c"] = color

    sc = ax.scatter(x, y, **kwargs)

    _v026_apply_clip(sc, res, key="gsMarkerClipOn")

    return sc


def overlay_stipple(ax, mask, lon=None, lat=None, res=None):
    """Overlay stipple markers from a boolean mask."""
    res = dict(res or {})

    mask = np.asarray(mask).astype(bool)

    if lon is None:
        lon = np.arange(mask.shape[1], dtype=float)

    if lat is None:
        lat = np.arange(mask.shape[0], dtype=float)

    lon = np.asarray(lon, dtype=float)
    lat = np.asarray(lat, dtype=float)

    if lon.ndim == 1 and lat.ndim == 1:
        lon2d, lat2d = np.meshgrid(lon, lat)
    else:
        lon2d, lat2d = lon, lat

    stride_y = int(res.get("gsStippleYStride", res.get("gsStippleStride", 1)))
    stride_x = int(res.get("gsStippleXStride", res.get("gsStippleStride", 1)))

    mask_s = _v026_subsample_2d(mask, stride_y=stride_y, stride_x=stride_x)
    lon_s = _v026_subsample_2d(lon2d, stride_y=stride_y, stride_x=stride_x)
    lat_s = _v026_subsample_2d(lat2d, stride_y=stride_y, stride_x=stride_x)

    marker_res = {
        "gsMarkerIndex": res.get("gsStippleMarkerIndex", res.get("gsMarkerIndex", ".")),
        "gsMarkerColor": res.get("gsStippleColor", res.get("gsMarkerColor", "black")),
        "gsMarkerSizeF": res.get("gsStippleMarkerSizeF", res.get("gsMarkerSizeF", 8)),
        "gsMarkerAlphaF": res.get("gsStippleAlphaF", res.get("gsMarkerAlphaF", 0.8)),
        "gsMarkerLineThicknessF": res.get("gsStippleLineThicknessF", 0.0),
        "gsMarkerZOrder": res.get("gsStippleZOrder", res.get("gsMarkerZOrder", 25)),
        "gsCoordinateMode": res.get("gsCoordinateMode", "data"),
    }

    return overlay_markers(
        ax,
        lon_s[mask_s],
        lat_s[mask_s],
        res=marker_res,
    )


def overlay_text(ax, x, y, text, res=None):
    """Overlay text with NCL-style tx resources."""
    res = dict(res or {})

    ha, va = _tx_just_to_align(res.get("txJust", res.get("gsTextJust", "CenterCenter")))

    bbox = None

    if bool_resource(res, "txPerimOn", "txBackgroundFillColor" in res):
        bbox = {
            "facecolor": res.get("txBackgroundFillColor", "white"),
            "edgecolor": res.get("txPerimColor", "0.3"),
            "linewidth": float(res.get("txPerimThicknessF", 0.6)),
            "alpha": float(res.get("txBackgroundAlphaF", 0.85)),
            "pad": float(res.get("txBackgroundPadF", 0.2)),
        }

    transform = _v026_transform(ax, res)

    txt = ax.text(
        x,
        y,
        text,
        ha=ha,
        va=va,
        color=res.get("txFontColor", res.get("gsTextColor", "black")),
        fontsize=float(res.get("txFontHeightF", res.get("gsTextFontHeightF", 10))),
        fontweight=res.get("txFontWeight", "normal"),
        rotation=float(res.get("txAngleF", 0.0)),
        bbox=bbox,
        transform=transform,
        zorder=float(res.get("txZOrder", res.get("gsTextZOrder", 30))),
        clip_on=bool_resource(res, "txClipOn", False),
    )

    return txt


def overlay_polyline(ax, x, y, res=None):
    """Overlay a polyline with NCL-style line resources."""
    res = dict(res or {})

    transform = _v026_transform(ax, res)

    line = ax.plot(
        x,
        y,
        color=res.get("gsLineColor", "black"),
        linewidth=float(res.get("gsLineThicknessF", 1.2)),
        linestyle=_map_dash(res.get("gsLineDashPattern", "solid")),
        alpha=float(res.get("gsLineAlphaF", 1.0)),
        marker=res.get("gsLineMarker", None),
        markersize=float(res.get("gsLineMarkerSizeF", 4.0)),
        transform=transform,
        zorder=float(res.get("gsLineZOrder", res.get("gsZOrder", 22))),
        clip_on=bool_resource(res, "gsLineClipOn", True),
    )

    return line


def overlay_polygon(ax, xy, res=None):
    """Overlay a polygon in lon/lat or axes coordinates."""
    res = dict(res or {})

    transform = _v026_transform(ax, res)

    patch = mpatches.Polygon(
        xy,
        closed=bool_resource(res, "gsPolygonClosed", True),
        facecolor=res.get("gsFillColor", res.get("gsPolygonFillColor", "none")),
        edgecolor=res.get("gsEdgeColor", res.get("gsLineColor", "black")),
        linewidth=float(res.get("gsLineThicknessF", 1.2)),
        linestyle=_map_dash(res.get("gsLineDashPattern", "solid")),
        alpha=float(res.get("gsFillOpacityF", res.get("gsFillAlphaF", 1.0))),
        transform=transform,
        zorder=float(res.get("gsPolygonZOrder", res.get("gsZOrder", 23))),
        clip_on=bool_resource(res, "gsPolygonClipOn", True),
    )

    ax.add_patch(patch)

    return patch


def overlay_rectangle(ax, x0, y0, x1, y1, res=None):
    """Overlay a rectangle using lower-left and upper-right coordinates."""
    res = dict(res or {})

    transform = _v026_transform(ax, res)

    width = x1 - x0
    height = y1 - y0

    patch = mpatches.Rectangle(
        (x0, y0),
        width,
        height,
        facecolor=res.get("gsFillColor", res.get("gsRectangleFillColor", "none")),
        edgecolor=res.get("gsEdgeColor", res.get("gsLineColor", "black")),
        linewidth=float(res.get("gsLineThicknessF", 1.2)),
        linestyle=_map_dash(res.get("gsLineDashPattern", "solid")),
        alpha=float(res.get("gsFillOpacityF", res.get("gsFillAlphaF", 1.0))),
        transform=transform,
        zorder=float(res.get("gsRectangleZOrder", res.get("gsZOrder", 24))),
        clip_on=bool_resource(res, "gsRectangleClipOn", True),
    )

    ax.add_patch(patch)

    return patch


def overlay_box(ax, lon_min, lon_max, lat_min, lat_max, res=None):
    """Convenience wrapper for map region boxes."""
    return overlay_rectangle(ax, lon_min, lat_min, lon_max, lat_max, res=res)


def overlay_vectors(ax, u, v, lon=None, lat=None, res=None):
    """Overlay vectors using quiver or barbs."""
    res = dict(res or {})

    u, lon, lat = to_numpy_data_lon_lat(u, lon=lon, lat=lat)
    v = np.asarray(v.values if hasattr(v, "values") else v)

    if lon.ndim == 1 and lat.ndim == 1:
        lon2d, lat2d = np.meshgrid(lon, lat)
    else:
        lon2d, lat2d = lon, lat

    stride = int(res.get("vcMinDistanceF", res.get("vcVectorStride", 1)))

    if stride < 1:
        stride = 1

    lon_s = lon2d[::stride, ::stride]
    lat_s = lat2d[::stride, ::stride]
    u_s = u[::stride, ::stride]
    v_s = v[::stride, ::stride]

    color = res.get("vcVectorColor", res.get("vcLineColor", "black"))
    zorder = float(res.get("vcZOrder", res.get("vcVectorZOrder", 28)))
    alpha = float(res.get("vcVectorAlphaF", 1.0))
    transform = ccrs.PlateCarree() if hasattr(ax, "projection") else ax.transData

    glyph = str(res.get("vcGlyphStyle", "LineArrow")).replace("_", "").replace("-", "").lower()

    if glyph in ["barb", "barbs", "windbarb", "windbarbs"]:
        barb = ax.barbs(
            lon_s,
            lat_s,
            u_s,
            v_s,
            color=color,
            length=float(res.get("vcBarbLengthF", 5.5)),
            linewidth=float(res.get("vcLineArrowThicknessF", 0.6)),
            alpha=alpha,
            transform=transform,
            zorder=zorder,
        )

        return {
            "barbs": barb,
            "quiver": None,
            "quiverkey": None,
        }

    q = ax.quiver(
        lon_s,
        lat_s,
        u_s,
        v_s,
        color=color,
        scale=res.get("vcVectorScaleF", None),
        scale_units=res.get("vcVectorScaleUnits", None),
        width=float(res.get("vcLineArrowThicknessF", 0.0025)),
        headwidth=float(res.get("vcArrowHeadWidthF", 3.0)),
        headlength=float(res.get("vcArrowHeadLengthF", 5.0)),
        headaxislength=float(res.get("vcArrowHeadAxisLengthF", 4.5)),
        alpha=alpha,
        transform=transform,
        zorder=zorder,
    )

    qk = None

    if bool_resource(res, "vcRefAnnoOn", False):
        ref = float(res.get("vcRefMagnitudeF", 1.0))
        label = res.get("vcRefAnnoString", f"{ref:g}")

        qk = ax.quiverkey(
            q,
            float(res.get("vcRefAnnoXF", 0.88)),
            float(res.get("vcRefAnnoYF", -0.08)),
            ref,
            label,
            labelpos=res.get("vcRefAnnoLabelPos", "E"),
            coordinates=res.get("vcRefAnnoCoordinateMode", "axes"),
            fontproperties={
                "size": float(res.get("vcRefAnnoFontHeightF", 9)),
            },
            color=color,
        )

    return {
        "quiver": q,
        "quiverkey": qk,
    }


add_contour_overlay = overlay_contour
add_filled_contour_overlay = overlay_filled_contour
add_marker_overlay = overlay_markers
add_markers = overlay_markers
add_stipple_overlay = overlay_stipple
add_stipple = overlay_stipple
add_stippling = overlay_stipple
overlay_stippling = overlay_stipple
add_text_overlay = overlay_text
add_text = overlay_text
add_vector_overlay = overlay_vectors
add_vectors = overlay_vectors
overlay_quiver = overlay_vectors
add_polyline = overlay_polyline
add_polygon = overlay_polygon
add_rectangle = overlay_rectangle
add_box = overlay_box
add_region_box = overlay_box

# climara v0.2.6 overlay resource override end


# Primitive / overlay management
# This section is backend independent except for functions ending with _mpl.

def get_plot_primitives(plotid):
    """Return the primitive list attached to a plot-like object."""
    if isinstance(plotid, dict):
        return plotid.setdefault("primitives", [])

    if not hasattr(plotid, "primitives"):
        plotid.primitives = []

    return plotid.primitives


def add_plot_primitive(plotid, primitive):
    """Attach a primitive to a plot-like object."""
    primitives = get_plot_primitives(plotid)
    primitives.append(primitive)
    return primitive


def get_plot_primitive_artists(plotid):
    """Return temporary Matplotlib artists for primitives."""
    if isinstance(plotid, dict):
        return plotid.setdefault("_primitive_artists", [])

    if not hasattr(plotid, "_primitive_artists"):
        plotid._primitive_artists = []

    return plotid._primitive_artists


def clear_plot_primitive_artists_mpl(plotid):
    """Remove temporary Matplotlib primitive artists."""
    artists = get_plot_primitive_artists(plotid)

    for artist in list(artists):
        try:
            if artist is not None:
                artist.remove()
        except Exception:
            pass

    artists.clear()


def get_plot_axes(plotid):
    """Return the temporary Matplotlib axes from a plot-like object."""
    if hasattr(plotid, "plot"):
        return plotid

    if isinstance(plotid, dict):
        return plotid.get("ax", None)

    return getattr(plotid, "ax", None)


def _draw_order_value(primitive):
    order = str(getattr(primitive, "draw_order", "draw")).lower()

    mapping = {
        "predraw": 0,
        "pre": 0,
        "background": 0,
        "draw": 10,
        "duringdraw": 10,
        "postdraw": 20,
        "post": 20,
        "foreground": 20,
    }

    return mapping.get(order, 10)


def render_plot_overlays_mpl(plotid, clear_existing=True):
    """Render stored plot primitives on a temporary Matplotlib axes.

    The primitive list is the authoritative state. Matplotlib artists are only
    the current backend bridge.
    """
    ax = get_plot_axes(plotid)

    if ax is None:
        return []

    if clear_existing:
        clear_plot_primitive_artists_mpl(plotid)

    primitives = sorted(get_plot_primitives(plotid), key=_draw_order_value)

    artists = []

    for primitive in primitives:
        if getattr(primitive, "coord_system", "data") != "data":
            continue

        name = primitive.__class__.__name__.lower()

        if "polyline" in name:
            from ._polyline import draw_polyline_data_mpl
            artist = draw_polyline_data_mpl(ax, primitive)
        elif "marker" in name:
            from ._polymarker import draw_marker_data_mpl
            artist = draw_marker_data_mpl(ax, primitive)
        elif "polygon" in name:
            from ._render_mpl import draw_polygon_data_mpl
            artist = draw_polygon_data_mpl(ax, primitive)
        else:
            continue

        primitive.resources["_mpl_artist"] = artist
        artists.append(artist)

    get_plot_primitive_artists(plotid).extend(artists)

    return artists


def redraw_plot_overlays_mpl(plotid):
    """Redraw all temporary Matplotlib overlay artists for a plot."""
    return render_plot_overlays_mpl(plotid, clear_existing=True)

