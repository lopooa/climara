from __future__ import annotations

try:
    import cartopy.crs as ccrs
except Exception:
    ccrs = None

import matplotlib.lines as mlines

from ._units import ncl_thickness_to_mpl

from ._overlay import add_plot_primitive, render_plot_overlays_mpl
from ._primitive import HluMarker
from ._resources import bool_resource

try:
    from ._colors import ncl_color_to_mpl
except Exception:
    def ncl_color_to_mpl(value):
        return value


def _marker_color(res):
    return ncl_color_to_mpl(
        res.get(
            "gsMarkerColor",
            res.get(
                "markerColor",
                res.get("color", "black"),
            ),
        )
    )


def _marker_size(res):
    value = res.get(
        "gsMarkerSizeF",
        res.get(
            "markerSize",
            res.get("markersize", 0.008),
        ),
    )

    value = float(value)

    # NCL marker size is usually in NDC-like units.
    # Matplotlib scatter size is area-like, so keep this bridge conservative.
    if 0.0 < value < 1.0:
        return value * 1000.0

    return value


def _marker_thickness(res):
    return float(
        res.get(
            "gsMarkerThicknessF",
            res.get("markerThickness", 1.0),
        )
    )


def _marker_symbol(res):
    value = res.get(
        "gsMarkerIndex",
        res.get(
            "markerIndex",
            res.get("marker", 16),
        ),
    )

    if isinstance(value, str):
        text = value.lower()

        aliases = {
            "dot": ".",
            "point": ".",
            "circle": "o",
            "filledcircle": "o",
            "open_circle": "o",
            "cross": "x",
            "x": "x",
            "plus": "+",
            "triangle": "^",
            "square": "s",
            "diamond": "D",
        }

        return aliases.get(text, value)

    try:
        value = int(value)
    except Exception:
        return "o"

    # Small practical subset of common NCL marker indices.
    mapping = {
        1: ".",
        2: "+",
        3: "*",
        4: "o",
        5: "x",
        6: "^",
        7: "s",
        8: "D",
        16: "o",
    }

    return mapping.get(value, "o")


def _make_marker(x, y, res=None, coord_system="data", name=None):
    return HluMarker(
        x=list(x),
        y=list(y),
        coord_system=coord_system,
        draw_order=str(dict(res or {}).get("tfPolyDrawOrder", "draw")),
        resources=dict(res or {}),
        name=name,
    )


def draw_marker_data_mpl(ax, primitive, transform=None):
    """Temporary Matplotlib bridge for a data-coordinate marker primitive."""

    if ax is None:
        return None

    res = primitive.resources

    kwargs = {
        "s": _marker_size(res),
        "marker": _marker_symbol(res),
        "c": _marker_color(res),
        "linewidths": ncl_thickness_to_mpl(_marker_thickness(res)),
        "alpha": float(res.get("gsMarkerOpacityF", res.get("markerOpacity", 1.0))),
        "clip_on": bool_resource(res, "gsClipOn", True),
        "zorder": float(res.get("gsMarkerZOrder", 13.0)),
    }

    if transform is not None:
        kwargs["transform"] = transform
    elif ccrs is not None and hasattr(ax, "projection"):
        kwargs["transform"] = ccrs.PlateCarree()

    return ax.scatter(primitive.x, primitive.y, **kwargs)


def draw_marker_ndc_mpl(fig, primitive):
    """Temporary Matplotlib bridge for a workstation NDC marker primitive."""

    if fig is None:
        return None

    res = primitive.resources
    artists = []

    for x, y in zip(primitive.x, primitive.y):
        artist = mlines.Line2D(
            [x],
            [y],
            transform=fig.transFigure,
            marker=_marker_symbol(res),
            markersize=max(_marker_size(res), 1.0),
            markeredgewidth=ncl_thickness_to_mpl(_marker_thickness(res)),
            markeredgecolor=_marker_color(res),
            markerfacecolor=_marker_color(res),
            linestyle="None",
            alpha=float(res.get("gsMarkerOpacityF", res.get("markerOpacity", 1.0))),
            clip_on=False,
            zorder=float(res.get("gsMarkerZOrder", 100.0)),
        )
        fig.add_artist(artist)
        artists.append(artist)

    return artists


def gsn_add_polymarker(wks, plotid, x, y, res=None):
    """NCL-style gsn_add_polymarker.

    The authoritative result is an HluMarker primitive attached to plotid.
    """

    res = dict(res or {})
    primitive = _make_marker(
        x,
        y,
        res=res,
        coord_system="data",
        name=res.get("gsName", "gsn_add_polymarker"),
    )

    add_plot_primitive(plotid, primitive)

    artist = None

    if bool_resource(res, "gsnDraw", True):
        artists = render_plot_overlays_mpl(plotid, clear_existing=True)
        if artists:
            artist = artists[-1]

    primitive.resources["_mpl_artist"] = artist

    return primitive


def gsn_polymarker_ndc(wks, x, y, res=None):
    """NCL-style gsn_polymarker_ndc."""

    res = dict(res or {})
    primitive = _make_marker(
        x,
        y,
        res=res,
        coord_system="ndc",
        name=res.get("gsName", "gsn_polymarker_ndc"),
    )

    if hasattr(wks, "add_primitive"):
        wks.add_primitive(primitive)

    artist = None

    if bool_resource(res, "gsnDraw", True) and hasattr(wks, "draw_ndc_marker"):
        artist = wks.draw_ndc_marker(primitive)

    primitive.resources["_mpl_artist"] = artist

    return primitive
