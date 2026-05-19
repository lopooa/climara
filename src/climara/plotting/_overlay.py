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
