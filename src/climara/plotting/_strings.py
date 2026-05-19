from __future__ import annotations


def _get_font_size(gsnres, key, default=10):
    value = gsnres.get(key, None)

    if value is None:
        return default

    return float(value)


def _get_just(just):
    just = str(just).lower()

    if just in ["left", "centerleft"]:
        return "left"

    if just in ["right", "centerright"]:
        return "right"

    return "center"


def add_gsn_strings(ax, gsnres: dict | None = None):
    """
    Add NCL-style gsnLeftString / gsnCenterString / gsnRightString.

    Supported resources
    -------------------
    gsnLeftString
    gsnCenterString
    gsnRightString
    gsnLeftStringFontHeightF
    gsnCenterStringFontHeightF
    gsnRightStringFontHeightF
    gsnStringFontHeightF
    gsnStringFontColor
    gsnLeftStringFontColor
    gsnCenterStringFontColor
    gsnRightStringFontColor
    gsnStringYF
    gsnStringFontWeight
    """
    if gsnres is None:
        return []

    base_size = _get_font_size(gsnres, "gsnStringFontHeightF", 10)
    base_color = gsnres.get("gsnStringFontColor", "black")
    weight = gsnres.get("gsnStringFontWeight", "normal")
    y = float(gsnres.get("gsnStringYF", 1.03))

    texts = []

    if "gsnLeftString" in gsnres:
        txt = ax.text(
            0.0,
            y,
            str(gsnres["gsnLeftString"]),
            transform=ax.transAxes,
            ha="left",
            va="bottom",
            fontsize=_get_font_size(gsnres, "gsnLeftStringFontHeightF", base_size),
            color=gsnres.get("gsnLeftStringFontColor", base_color),
            fontweight=weight,
            clip_on=False,
        )
        texts.append(txt)

    if "gsnCenterString" in gsnres:
        txt = ax.text(
            0.5,
            y,
            str(gsnres["gsnCenterString"]),
            transform=ax.transAxes,
            ha="center",
            va="bottom",
            fontsize=_get_font_size(gsnres, "gsnCenterStringFontHeightF", base_size),
            color=gsnres.get("gsnCenterStringFontColor", base_color),
            fontweight=weight,
            clip_on=False,
        )
        texts.append(txt)

    if "gsnRightString" in gsnres:
        txt = ax.text(
            1.0,
            y,
            str(gsnres["gsnRightString"]),
            transform=ax.transAxes,
            ha="right",
            va="bottom",
            fontsize=_get_font_size(gsnres, "gsnRightStringFontHeightF", base_size),
            color=gsnres.get("gsnRightStringFontColor", base_color),
            fontweight=weight,
            clip_on=False,
        )
        texts.append(txt)

    return texts
