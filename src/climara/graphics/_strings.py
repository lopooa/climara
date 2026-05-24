from __future__ import annotations

from ._text_item import HluTextItem


def _get_font_height(res, key, default=10.0):
    value = res.get(key, None)

    if value is None:
        return float(default)

    return float(value)


def _font_height_to_mpl_points(value):
    value = float(value)

    if 0.0 < value < 1.0:
        return value * 1000.0

    return value


def _normalize_just(just):
    text = str(just).replace("-", "_").replace(" ", "_").lower()

    aliases = {
        "center": "center_center",
        "left": "center_left",
        "right": "center_right",
        "topleft": "top_left",
        "topright": "top_right",
        "bottomleft": "bottom_left",
        "bottomright": "bottom_right",
        "centerleft": "center_left",
        "centerright": "center_right",
        "topcenter": "top_center",
        "bottomcenter": "bottom_center",
    }

    return aliases.get(text, text)


def _just_to_mpl(just):
    just = _normalize_just(just)

    if "left" in just:
        ha = "left"
    elif "right" in just:
        ha = "right"
    else:
        ha = "center"

    if "top" in just:
        va = "top"
    elif "bottom" in just:
        va = "bottom"
    else:
        va = "center"

    return ha, va


def _make_text_item(
    text,
    x,
    y,
    just,
    font_height,
    color,
    angle=0.0,
    coord_system="viewport",
    name=None,
    resources=None,
):
    return HluTextItem(
        txString=str(text),
        txPosXF=float(x),
        txPosYF=float(y),
        txJust=_normalize_just(just),
        txFontHeightF=float(font_height),
        txFontColor=color,
        txAngleF=float(angle),
        coord_system=coord_system,
        name=name,
        resources=dict(resources or {}),
    )


def create_gsn_string_items(gsnres: dict | None = None):
    """Create HLU TextItem objects for gsnLeft/Center/RightString.

    This is layout/object creation only. It does not draw.
    """

    if gsnres is None:
        return []

    base_height = _get_font_height(gsnres, "gsnStringFontHeightF", 10.0)
    base_color = gsnres.get("gsnStringFontColor", "black")
    y = float(gsnres.get("gsnStringYF", 1.03))

    items = []

    if "gsnLeftString" in gsnres:
        items.append(
            _make_text_item(
                gsnres["gsnLeftString"],
                0.0,
                y,
                "bottom_left",
                _get_font_height(gsnres, "gsnLeftStringFontHeightF", base_height),
                gsnres.get("gsnLeftStringFontColor", base_color),
                coord_system="viewport",
                name="gsnLeftString",
                resources=gsnres,
            )
        )

    if "gsnCenterString" in gsnres:
        items.append(
            _make_text_item(
                gsnres["gsnCenterString"],
                0.5,
                y,
                "bottom_center",
                _get_font_height(gsnres, "gsnCenterStringFontHeightF", base_height),
                gsnres.get("gsnCenterStringFontColor", base_color),
                coord_system="viewport",
                name="gsnCenterString",
                resources=gsnres,
            )
        )

    if "gsnRightString" in gsnres:
        items.append(
            _make_text_item(
                gsnres["gsnRightString"],
                1.0,
                y,
                "bottom_right",
                _get_font_height(gsnres, "gsnRightStringFontHeightF", base_height),
                gsnres.get("gsnRightStringFontColor", base_color),
                coord_system="viewport",
                name="gsnRightString",
                resources=gsnres,
            )
        )

    return items


def create_ti_main_text_item(tires: dict | None = None, gsnres: dict | None = None):
    """Create a TextItem for tiMainString.

    This replaces the layout role of ax.set_title().
    """

    tires = dict(tires or {})
    gsnres = dict(gsnres or {})

    if "tiMainString" not in tires:
        return None

    has_gsn_strings = any(
        key in gsnres
        for key in ["gsnLeftString", "gsnCenterString", "gsnRightString"]
    )

    if "tiMainYF" in tires:
        y = float(tires["tiMainYF"])
    elif has_gsn_strings:
        y = 1.12
    else:
        y = 1.03

    return _make_text_item(
        tires["tiMainString"],
        0.5,
        y,
        "bottom_center",
        _get_font_height(tires, "tiMainFontHeightF", 11.0),
        tires.get("tiMainFontColor", "black"),
        angle=float(tires.get("tiMainAngleF", 0.0)),
        coord_system="viewport",
        name="tiMainString",
        resources={**gsnres, **tires},
    )


def draw_text_item_mpl(ax, item: HluTextItem):
    """Temporary Matplotlib bridge for a viewport TextItem."""

    if item is None:
        return None

    if item.coord_system != "viewport":
        raise ValueError("draw_text_item_mpl expects coord_system='viewport'")

    ha, va = _just_to_mpl(item.txJust)

    return ax.text(
        item.txPosXF,
        item.txPosYF,
        item.txString,
        transform=ax.transAxes,
        ha=ha,
        va=va,
        fontsize=_font_height_to_mpl_points(item.txFontHeightF),
        color=item.txFontColor,
        rotation=item.txAngleF,
        fontweight=item.resources.get("gsnStringFontWeight", "normal"),
        clip_on=False,
    )


def draw_text_item_ndc_mpl(fig, item: HluTextItem):
    """Temporary Matplotlib bridge for an NDC TextItem."""

    if item is None:
        return None

    if item.coord_system != "ndc":
        raise ValueError("draw_text_item_ndc_mpl expects coord_system='ndc'")

    ha, va = _just_to_mpl(item.txJust)

    return fig.text(
        item.txPosXF,
        item.txPosYF,
        item.txString,
        ha=ha,
        va=va,
        fontsize=_font_height_to_mpl_points(item.txFontHeightF),
        color=item.txFontColor,
        rotation=item.txAngleF,
        fontweight=item.resources.get("txFontWeight", "normal"),
    )


def add_gsn_strings(ax, gsnres: dict | None = None, return_items=False):
    """Add NCL-style gsnLeftString / gsnCenterString / gsnRightString.

    The authoritative objects are HluTextItem instances.
    Matplotlib drawing here is only a temporary renderer bridge.
    """

    items = create_gsn_string_items(gsnres)
    artists = [draw_text_item_mpl(ax, item) for item in items]

    if return_items:
        return artists, items

    return artists
