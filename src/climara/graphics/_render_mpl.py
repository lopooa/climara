from __future__ import annotations

import matplotlib.patches as mpatches

from ._units import ncl_thickness_to_mpl

try:
    import cartopy.crs as ccrs
except Exception:
    ccrs = None

from ._polyline import draw_polyline_ndc_mpl
from ._strings import draw_text_item_ndc_mpl

try:
    from ._colors import ncl_color_to_mpl
except Exception:
    def ncl_color_to_mpl(value):
        return value


def _font_height_to_points(value):
    value = float(value)

    if 0.0 < value < 1.0:
        return value * 1000.0

    return value



def _polygon_fill_color(res):
    return ncl_color_to_mpl(
        res.get(
            "gsFillColor",
            res.get("fill_color", res.get("fillColor", "none")),
        )
    )


def _polygon_edge_color(res):
    return ncl_color_to_mpl(
        res.get(
            "gsEdgeColor",
            res.get(
                "gsLineColor",
                res.get("edge_color", res.get("line_color", "black")),
            ),
        )
    )


def _polygon_line_thickness(res):
    return float(
        res.get(
            "gsLineThicknessF",
            res.get(
                "gsEdgeThicknessF",
                res.get("line_thickness", res.get("edge_thickness", 0.6)),
            ),
        )
    )


def _polygon_edges_on(res):
    value = res.get("gsEdgesOn", res.get("edges_on", True))

    if isinstance(value, str):
        return value.strip().lower() in {"true", "t", "yes", "y", "on", "1"}

    return bool(value)


def draw_polygon_ndc_mpl(fig, primitive):
    fill_color = primitive.resources.get("fill_color", "none")
    line_color = primitive.resources.get("line_color", "black")
    line_thickness = float(primitive.resources.get("line_thickness", 0.6))

    patch = mpatches.Polygon(
        list(zip(primitive.x, primitive.y)),
        closed=True,
        transform=fig.transFigure,
        facecolor=ncl_color_to_mpl(fill_color),
        edgecolor=ncl_color_to_mpl(line_color),
        linewidth=ncl_thickness_to_mpl(line_thickness),
        clip_on=False,
        joinstyle="miter",
    )

    fig.add_artist(patch)

    return patch



def draw_polygon_data_mpl(ax, primitive, transform=None):
    """Temporary Matplotlib bridge for a data-coordinate polygon."""
    if ax is None:
        return None

    res = primitive.resources

    edge_color = _polygon_edge_color(res) if _polygon_edges_on(res) else "none"

    patch = mpatches.Polygon(
        list(zip(primitive.x, primitive.y)),
        closed=True,
        transform=transform if transform is not None else (
            ccrs.PlateCarree() if ccrs is not None and hasattr(ax, "projection") else ax.transData
        ),
        facecolor=_polygon_fill_color(res),
        edgecolor=edge_color,
        linewidth=_polygon_line_thickness(res),
        alpha=float(res.get("gsFillOpacityF", res.get("fill_opacity", 1.0))),
        clip_on=True,
        joinstyle="miter",
        zorder=float(res.get("gsPolygonZOrder", 11.0)),
    )

    ax.add_patch(patch)

    return patch

def render_ndc_primitives_mpl(fig, primitives):
    artists = []

    for primitive in primitives:
        name = primitive.__class__.__name__.lower()

        if "textitem" in name:
            artist = draw_text_item_ndc_mpl(fig, primitive)
        elif "polyline" in name:
            artist = draw_polyline_ndc_mpl(fig, primitive)
        elif "polygon" in name:
            artist = draw_polygon_ndc_mpl(fig, primitive)
        elif "marker" in name:
            from ._polymarker import draw_marker_ndc_mpl
            artist = draw_marker_ndc_mpl(fig, primitive)
        else:
            artist = None

        if artist is not None:
            artists.append(artist)

    return artists
