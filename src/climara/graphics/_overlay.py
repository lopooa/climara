from __future__ import annotations


def get_plot_primitives(plotid):
    if isinstance(plotid, dict):
        return plotid.setdefault("primitives", [])

    if not hasattr(plotid, "primitives"):
        plotid.primitives = []

    return plotid.primitives


def add_plot_primitive(plotid, primitive):
    primitives = get_plot_primitives(plotid)
    primitives.append(primitive)
    return primitive


def get_plot_primitive_artists(plotid):
    return []


def clear_plot_primitive_artists_mpl(plotid):
    return None


def render_plot_overlays_mpl(plotid, clear_existing=True):
    raise RuntimeError("Legacy overlay rendering has been removed from climara.")


def redraw_plot_overlays_mpl(plotid):
    raise RuntimeError("Legacy overlay rendering has been removed from climara.")
