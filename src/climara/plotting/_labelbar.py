from __future__ import annotations

import numpy as np

from ._resources import bool_resource


def _merge_labelbar_resources(lbres, pmres=None):
    out = dict(lbres or {})

    if pmres:
        for key, value in pmres.items():
            out[key] = value

    return out


def _normalize_orientation(lbres):
    if "lbOrientation" in lbres:
        orientation = str(lbres["lbOrientation"]).lower()
    else:
        side = str(lbres.get("pmLabelBarSide", "")).lower()

        if side in ["left", "right"]:
            orientation = "vertical"
        else:
            orientation = "horizontal"

    if orientation in ["vertical", "v"]:
        return "vertical"

    return "horizontal"


def _normalize_side(lbres, orientation):
    side = str(lbres.get("pmLabelBarSide", "")).lower()

    if side in ["top", "bottom", "left", "right"]:
        return side

    if orientation == "horizontal":
        return "bottom"

    return "right"


def _manual_cax_from_pm(fig, ax, lbres):
    orientation = _normalize_orientation(lbres)

    if all(k in lbres for k in ["lbLeft", "lbBottom", "lbWidth", "lbHeight"]):
        return fig.add_axes(
            [
                float(lbres["lbLeft"]),
                float(lbres["lbBottom"]),
                float(lbres["lbWidth"]),
                float(lbres["lbHeight"]),
            ]
        )

    if not any(
        k in lbres
        for k in [
            "pmLabelBarWidthF",
            "pmLabelBarHeightF",
            "pmLabelBarOrthogonalPosF",
            "pmLabelBarParallelPosF",
            "pmLabelBarSide",
        ]
    ):
        return None

    pos = ax.get_position()
    side = _normalize_side(lbres, orientation)

    if orientation == "horizontal":
        width = float(lbres.get("pmLabelBarWidthF", pos.width * 0.85))
        height = float(lbres.get("pmLabelBarHeightF", 0.025))
        parallel = float(lbres.get("pmLabelBarParallelPosF", 0.0))
        orthogonal = float(lbres.get("pmLabelBarOrthogonalPosF", 0.08))

        left = pos.x0 + (pos.width - width) / 2 + parallel

        if side == "top":
            bottom = pos.y1 + orthogonal
        else:
            bottom = pos.y0 - orthogonal

        return fig.add_axes([left, bottom, width, height])

    width = float(lbres.get("pmLabelBarWidthF", 0.025))
    height = float(lbres.get("pmLabelBarHeightF", pos.height * 0.85))
    parallel = float(lbres.get("pmLabelBarParallelPosF", 0.0))
    orthogonal = float(lbres.get("pmLabelBarOrthogonalPosF", 0.05))

    if side == "left":
        left = pos.x0 - orthogonal - width
    else:
        left = pos.x1 + orthogonal

    bottom = pos.y0 + (pos.height - height) / 2 + parallel

    return fig.add_axes([left, bottom, width, height])


def _apply_labelbar_ticks(cbar, lbres):
    positions = lbres.get("lbLabelPositions", None)
    labels = lbres.get("lbLabelStrings", None)

    stride = int(lbres.get("lbLabelStride", 1))

    if stride < 1:
        stride = 1

    auto_stride = bool_resource(lbres, "lbLabelAutoStride", False)
    max_labels = int(lbres.get("lbLabelMaxCount", 7))

    if positions is not None:
        ticks = np.asarray(positions, dtype=float)
        cbar.set_ticks(ticks)
    else:
        ticks = np.asarray(cbar.get_ticks())

        if auto_stride and ticks.size > max_labels:
            stride = int(np.ceil(ticks.size / max_labels))

        if stride > 1 and ticks.size > 0:
            ticks = ticks[::stride]
            cbar.set_ticks(ticks)

    if labels is not None:
        labels = list(labels)

        if len(labels) == len(ticks):
            cbar.set_ticklabels(labels)

    label_size = lbres.get("lbLabelFontHeightF", None)
    label_color = lbres.get("lbLabelFontColor", None)
    tick_length = lbres.get("lbTickLengthF", None)
    tick_width = lbres.get("lbTickThicknessF", None)

    tick_kwargs = {}

    if label_size is not None:
        tick_kwargs["labelsize"] = float(label_size)

    if label_color is not None:
        tick_kwargs["labelcolor"] = label_color
        tick_kwargs["colors"] = label_color

    if tick_length is not None:
        tick_kwargs["length"] = float(tick_length)

    if tick_width is not None:
        tick_kwargs["width"] = float(tick_width)

    if tick_kwargs:
        cbar.ax.tick_params(**tick_kwargs)

    if not bool_resource(lbres, "lbTickMarksOn", True):
        cbar.ax.tick_params(length=0)

    angle = float(lbres.get("lbLabelAngleF", 0.0))
    weight = lbres.get("lbLabelFontWeight", None)

    tick_texts = cbar.ax.get_xticklabels() + cbar.ax.get_yticklabels()

    for text in tick_texts:
        text.set_rotation(angle)

        if weight is not None:
            text.set_fontweight(weight)

        if label_color is not None:
            text.set_color(label_color)

    return cbar


def _apply_labelbar_title(cbar, lbres):
    title = lbres.get("lbTitleString", None)

    if title is None:
        return cbar

    orientation = _normalize_orientation(lbres)
    position = str(lbres.get("lbTitlePosition", "bottom")).lower()
    size = float(lbres.get("lbTitleFontHeightF", 10))
    color = lbres.get("lbTitleFontColor", "black")
    weight = lbres.get("lbTitleFontWeight", "normal")
    pad = float(lbres.get("lbTitleOffsetF", 4))

    if orientation == "horizontal":
        if position in ["top", "above"]:
            cbar.ax.set_title(
                title,
                fontsize=size,
                color=color,
                fontweight=weight,
                pad=pad,
            )
        else:
            cbar.ax.set_xlabel(
                title,
                fontsize=size,
                color=color,
                fontweight=weight,
                labelpad=pad,
            )
    else:
        cbar.ax.set_ylabel(
            title,
            fontsize=size,
            color=color,
            fontweight=weight,
            labelpad=pad,
        )

        if position in ["left"]:
            cbar.ax.yaxis.set_label_position("left")
            cbar.ax.yaxis.tick_left()
        else:
            cbar.ax.yaxis.set_label_position("right")
            cbar.ax.yaxis.tick_right()

    return cbar


def _apply_labelbar_box(cbar, lbres):
    box_lines_on = bool_resource(lbres, "lbBoxLinesOn", True)

    if not box_lines_on:
        cbar.outline.set_visible(False)

        if hasattr(cbar, "solids") and cbar.solids is not None:
            try:
                cbar.solids.set_edgecolor("face")
                cbar.solids.set_linewidth(0.0)
            except Exception:
                pass

        return cbar

    color = lbres.get("lbBoxLineColor", "0.2")
    linewidth = float(lbres.get("lbBoxLineThicknessF", 0.8))

    cbar.outline.set_visible(True)
    cbar.outline.set_edgecolor(color)
    cbar.outline.set_linewidth(linewidth)

    if hasattr(cbar, "solids") and cbar.solids is not None:
        try:
            cbar.solids.set_edgecolor(color)
            cbar.solids.set_linewidth(float(lbres.get("lbBoxSeparatorLineThicknessF", 0.0)))
        except Exception:
            pass

    return cbar


def _apply_labelbar_axis(cbar, lbres):
    orientation = _normalize_orientation(lbres)

    if orientation == "horizontal":
        if str(lbres.get("lbLabelPosition", "bottom")).lower() == "top":
            cbar.ax.xaxis.set_ticks_position("top")
            cbar.ax.xaxis.set_label_position("top")
        else:
            cbar.ax.xaxis.set_ticks_position("bottom")
            cbar.ax.xaxis.set_label_position("bottom")
    else:
        if str(lbres.get("lbLabelPosition", "right")).lower() == "left":
            cbar.ax.yaxis.set_ticks_position("left")
        else:
            cbar.ax.yaxis.set_ticks_position("right")

    return cbar


def add_labelbar(fig, ax, mappable, lbres: dict | None = None, cax=None, pmres=None):
    """
    Add an NCL-style labelbar.

    Supported resources
    -------------------
    lbLabelBarOn
    lbOrientation
    lbTitleString
    lbTitlePosition
    lbTitleFontHeightF
    lbTitleFontColor
    lbTitleFontWeight
    lbTitleOffsetF

    lbLabelStrings
    lbLabelPositions
    lbLabelStride
    lbLabelAutoStride
    lbLabelMaxCount
    lbLabelFontHeightF
    lbLabelFontColor
    lbLabelAngleF
    lbLabelFontWeight
    lbLabelPosition

    lbBoxLinesOn
    lbBoxLineColor
    lbBoxLineThicknessF
    lbBoxSeparatorLineThicknessF

    lbTickMarksOn
    lbTickLengthF
    lbTickThicknessF

    lbLeft
    lbBottom
    lbWidth
    lbHeight

    pmLabelBarDisplayMode
    pmLabelBarSide
    pmLabelBarWidthF
    pmLabelBarHeightF
    pmLabelBarOrthogonalPosF
    pmLabelBarParallelPosF
    """
    lbres = _merge_labelbar_resources(lbres, pmres)

    if not bool_resource(lbres, "lbLabelBarOn", True):
        return None

    display_mode = str(lbres.get("pmLabelBarDisplayMode", "Always")).lower()

    if display_mode in ["never", "no", "false", "none"]:
        return None

    orientation = _normalize_orientation(lbres)

    if cax is None:
        cax = _manual_cax_from_pm(fig, ax, lbres)

    drawedges = bool_resource(lbres, "lbBoxLinesOn", True)

    if cax is not None:
        cbar = fig.colorbar(
            mappable,
            cax=cax,
            orientation=orientation,
            drawedges=drawedges,
        )
    else:
        cbar = fig.colorbar(
            mappable,
            ax=ax,
            orientation=orientation,
            shrink=float(lbres.get("lbShrinkF", 0.82)),
            pad=float(lbres.get("lbPadF", 0.06)),
            aspect=float(lbres.get("lbAspectF", 28)),
            drawedges=drawedges,
        )

    _apply_labelbar_axis(cbar, lbres)
    _apply_labelbar_ticks(cbar, lbres)
    _apply_labelbar_title(cbar, lbres)
    _apply_labelbar_box(cbar, lbres)

    return cbar


def gsn_labelbar(fig, mappable, res=None, ax=None, cax=None):
    if res is None:
        res = {}

    if ax is None and cax is None and not all(k in res for k in ["lbLeft", "lbBottom", "lbWidth", "lbHeight"]):
        raise ValueError("ax or cax must be given when no manual labelbar position is used")

    return add_labelbar(fig, ax, mappable, res, cax=cax)
