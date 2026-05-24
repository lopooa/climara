from __future__ import annotations

try:
    import cartopy.crs as ccrs
except Exception:
    ccrs = None

import matplotlib.lines as mlines

from ._units import ncl_thickness_to_mpl

from ._primitive import HluPolyline
from ._overlay import add_plot_primitive, render_plot_overlays_mpl
from ._resources import bool_resource

try:
    from ._colors import ncl_color_to_mpl
except Exception:
    def ncl_color_to_mpl(value):
        return value


def _line_color(res):
    return ncl_color_to_mpl(
        res.get(
            "gsLineColor",
            res.get(
                "lineColor",
                res.get("polylineColor", "black"),
            ),
        )
    )


def _line_thickness(res):
    return float(
        res.get(
            "gsLineThicknessF",
            res.get(
                "lineThickness",
                res.get("linewidth", 1.0),
            ),
        )
    )


def _line_dash(res):
    value = res.get(
        "gsLineDashPattern",
        res.get("lineDashPattern", res.get("linestyle", 0)),
    )

    if isinstance(value, str):
        text = value.lower()

        if text in {"solid", "-", "0"}:
            return "-"

        if text in {"dash", "dashed", "--", "1"}:
            return "--"

        if text in {"dot", "dotted", ":", "2"}:
            return ":"

        if text in {"dashdot", "-.", "3"}:
            return "-."

        return value

    try:
        value = int(value)
    except Exception:
        return "-"

    if value == 1:
        return "--"

    if value == 2:
        return ":"

    if value == 3:
        return "-."

    return "-"


def _line_alpha(res):
    return float(
        res.get(
            "gsLineOpacityF",
            res.get("lineOpacity", 1.0),
        )
    )


def _make_polyline(x, y, res=None, coord_system="data", name=None):
    return HluPolyline(
        x=list(x),
        y=list(y),
        coord_system=coord_system,
        draw_order=str(dict(res or {}).get("tfPolyDrawOrder", "draw")),
        resources=dict(res or {}),
        name=name,
    )


def _store_primitive_on_plot(plotid, primitive):
    add_plot_primitive(plotid, primitive)


def _get_plot_axes(plotid):
    if hasattr(plotid, "plot"):
        return plotid

    if isinstance(plotid, dict):
        return plotid.get("ax", None)

    return getattr(plotid, "ax", None)


def draw_polyline_data_mpl(ax, primitive, transform=None):
    """Temporary Matplotlib bridge for a data-coordinate polyline."""

    if ax is None:
        return None

    res = primitive.resources

    kwargs = {
        "color": _line_color(res),
        "linewidth": ncl_thickness_to_mpl(_line_thickness(res)),
        "linestyle": _line_dash(res),
        "alpha": _line_alpha(res),
        "clip_on": bool_resource(res, "gsClipOn", True),
        "zorder": float(res.get("gsLineZOrder", 12.0)),
    }

    if transform is not None:
        kwargs["transform"] = transform
    elif ccrs is not None and hasattr(ax, "projection"):
        kwargs["transform"] = ccrs.PlateCarree()

    artists = ax.plot(primitive.x, primitive.y, **kwargs)

    if len(artists) == 1:
        return artists[0]

    return artists


def draw_polyline_ndc_mpl(fig, primitive):
    """Temporary Matplotlib bridge for a workstation NDC polyline."""

    if fig is None:
        return None

    res = primitive.resources

    artist = mlines.Line2D(
        primitive.x,
        primitive.y,
        transform=fig.transFigure,
        color=_line_color(res),
        linewidth=ncl_thickness_to_mpl(_line_thickness(res)),
        linestyle=_line_dash(res),
        alpha=_line_alpha(res),
        clip_on=False,
        zorder=float(res.get("gsLineZOrder", 100.0)),
    )

    fig.add_artist(artist)

    return artist


def gsn_add_polyline(wks, plotid, x, y, res=None):
    """NCL-style gsn_add_polyline.

    The authoritative result is an HluPolyline primitive attached to plotid.
    The Matplotlib drawing path is only a temporary renderer bridge.
    """

    res = dict(res or {})
    primitive = _make_polyline(
        x,
        y,
        res=res,
        coord_system="data",
        name=res.get("gsName", "gsn_add_polyline"),
    )

    _store_primitive_on_plot(plotid, primitive)

    artist = None

    if bool_resource(res, "gsnDraw", True):
        artists = render_plot_overlays_mpl(plotid, clear_existing=True)
        if artists:
            artist = artists[-1]

    primitive.resources["_mpl_artist"] = artist

    return primitive


def gsn_polyline_ndc(wks, x, y, res=None):
    """NCL-style gsn_polyline_ndc.

    The polyline is stored as a workstation-level primitive.
    """

    res = dict(res or {})
    primitive = _make_polyline(
        x,
        y,
        res=res,
        coord_system="ndc",
        name=res.get("gsName", "gsn_polyline_ndc"),
    )

    if hasattr(wks, "add_primitive"):
        wks.add_primitive(primitive)

    artist = None

    if bool_resource(res, "gsnDraw", True) and hasattr(wks, "draw_ndc_polyline"):
        artist = wks.draw_ndc_polyline(primitive)

    primitive.resources["_mpl_artist"] = artist

    return primitive


def _primitive_artist_list(plotid):
    if isinstance(plotid, dict):
        return plotid.setdefault("_primitive_artists", [])

    if not hasattr(plotid, "_primitive_artists"):
        plotid._primitive_artists = []

    return plotid._primitive_artists


def _plot_primitive_list(plotid):
    if isinstance(plotid, dict):
        return plotid.setdefault("primitives", [])

    if not hasattr(plotid, "primitives"):
        plotid.primitives = []

    return plotid.primitives


def clear_plot_primitive_artists_mpl(plotid):
    """Remove previously drawn primitive artists from a plot."""
    artists = _primitive_artist_list(plotid)

    for artist in artists:
        try:
            if artist is None:
                continue
            artist.remove()
        except Exception:
            pass

    artists.clear()


def render_plot_primitives_mpl(plotid, clear_existing=True):
    """Render stored plot primitives on the current Matplotlib axes.

    This is a temporary renderer bridge. The authoritative state is the
    primitive list attached to plotid.
    """
    ax = _get_plot_axes(plotid)

    if ax is None:
        return []

    primitives = _plot_primitive_list(plotid)

    if clear_existing:
        clear_plot_primitive_artists_mpl(plotid)

    artists = []

    # very simple draw-order pass for now
    order_map = {
        "predraw": 5,
        "draw": 10,
        "postdraw": 15,
    }

    def _sort_key(primitive):
        draw_order = str(getattr(primitive, "draw_order", "draw")).lower()
        return order_map.get(draw_order, 10)

    for primitive in sorted(primitives, key=_sort_key):
        if getattr(primitive, "coord_system", None) != "data":
            continue

        artist = draw_polyline_data_mpl(ax, primitive)
        primitive.resources["_mpl_artist"] = artist
        artists.append(artist)

    _primitive_artist_list(plotid).extend(artists)

    return artists


def redraw_plot_primitives_mpl(plotid):
    """Convenience wrapper to fully redraw plot primitives."""
    return render_plot_primitives_mpl(plotid, clear_existing=True)

