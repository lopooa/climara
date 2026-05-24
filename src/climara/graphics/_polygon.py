from __future__ import annotations

from ._overlay import add_plot_primitive, render_plot_overlays_mpl
from ._primitive import HluPolygon
from ._resources import bool_resource


def _make_polygon(x, y, res=None, coord_system="data", name=None):
    res = dict(res or {})

    return HluPolygon(
        x=list(x),
        y=list(y),
        coord_system=coord_system,
        draw_order=str(res.get("tfPolyDrawOrder", "draw")),
        resources=res,
        name=name,
    )


def gsn_add_polygon(wks, plotid, x, y, res=None):
    """NCL-style gsn_add_polygon.

    The authoritative result is an HLU-style polygon primitive attached to
    the plot. Rendering is delegated to the active backend.
    """
    res = dict(res or {})

    primitive = _make_polygon(
        x,
        y,
        res=res,
        coord_system="data",
        name=res.get("gsName", "gsn_add_polygon"),
    )

    add_plot_primitive(plotid, primitive)

    artist = None

    if bool_resource(res, "gsnDraw", True):
        artists = render_plot_overlays_mpl(plotid, clear_existing=True)

        if artists:
            artist = artists[-1]

    primitive.resources["_mpl_artist"] = artist

    return primitive


def gsn_polygon_ndc(wks, x, y, res=None):
    """NCL-style gsn_polygon_ndc.

    The polygon is stored as a workstation/page-level primitive.
    """
    res = dict(res or {})

    primitive = _make_polygon(
        x,
        y,
        res=res,
        coord_system="ndc",
        name=res.get("gsName", "gsn_polygon_ndc"),
    )

    if hasattr(wks, "add_primitive"):
        wks.add_primitive(primitive)

    artist = None

    if bool_resource(res, "gsnDraw", True) and hasattr(wks, "draw_ndc_polygon"):
        artist = wks.draw_ndc_polygon(primitive)

    primitive.resources["_mpl_artist"] = artist

    return primitive
