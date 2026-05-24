from __future__ import annotations

import numpy as np

from ._resources import bool_resource
from ._colors import ncl_color_to_mpl


def _normalize_labelbar_color_resources(lbres):
    """Normalize NCL-style labelbar color resources."""
    lbres = dict(lbres or {})

    for key, value in list(lbres.items()):
        if key.endswith("Color") or "Color" in key:
            lbres[key] = ncl_color_to_mpl(value)

    return lbres


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
    lbres = _normalize_labelbar_color_resources(lbres)

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

# climara v0.2.5 labelbar resource override begin

def _v025_parse_sequence(value):
    if value is None:
        return None

    if isinstance(value, str):
        text = value.strip()

        if not text:
            return []

        if "|" in text:
            return [item.strip() for item in text.split("|")]

        if "," in text:
            return [item.strip() for item in text.split(",")]

        return text.split()

    try:
        return list(value)
    except TypeError:
        return [value]


def _v025_parse_float_sequence(value):
    items = _v025_parse_sequence(value)

    if items is None:
        return None

    return [float(item) for item in items]


def _v025_get_boundaries_from_mappable(mappable):
    norm = getattr(mappable, "norm", None)

    boundaries = getattr(norm, "boundaries", None)

    if boundaries is None:
        boundaries = getattr(mappable, "boundaries", None)

    if boundaries is None:
        return None

    boundaries = np.asarray(boundaries, dtype=float)

    if boundaries.ndim != 1 or boundaries.size < 2:
        return None

    return boundaries


def _v025_get_ticks_from_alignment(cbar, mappable, lbres):
    explicit = _v025_parse_float_sequence(lbres.get("lbLabelPositions", None))

    if explicit is not None:
        return np.asarray(explicit, dtype=float)

    boundaries = _v025_get_boundaries_from_mappable(mappable)
    alignment = str(lbres.get("lbLabelAlignment", "")).replace("_", "").replace("-", "").lower()

    if boundaries is None:
        return np.asarray(cbar.get_ticks(), dtype=float)

    if alignment in ["boxcenters", "center", "centers", "midpoints"]:
        return 0.5 * (boundaries[:-1] + boundaries[1:])

    if alignment in ["interioredges", "internaledges", "inneredges"]:
        if boundaries.size > 2:
            return boundaries[1:-1]

        return boundaries

    if alignment in ["externaledges", "outeredges", "edges", "boundaries"]:
        return boundaries

    return np.asarray(cbar.get_ticks(), dtype=float)


def _v025_format_tick(value, fmt):
    if fmt is None:
        return None

    if callable(fmt):
        return fmt(value)

    fmt = str(fmt)

    try:
        if "{" in fmt:
            return fmt.format(value)
    except Exception:
        pass

    try:
        return fmt % value
    except Exception:
        pass

    try:
        return format(value, fmt)
    except Exception:
        return str(value)


def _v025_apply_labelbar_axis(cbar, lbres):
    orientation = _normalize_orientation(lbres)

    if orientation == "horizontal":
        position = str(lbres.get("lbLabelPosition", "bottom")).lower()

        if position in ["top", "above"]:
            cbar.ax.xaxis.set_ticks_position("top")
            cbar.ax.xaxis.set_label_position("top")
        else:
            cbar.ax.xaxis.set_ticks_position("bottom")
            cbar.ax.xaxis.set_label_position("bottom")
    else:
        position = str(lbres.get("lbLabelPosition", "right")).lower()

        if position in ["left"]:
            cbar.ax.yaxis.set_ticks_position("left")
            cbar.ax.yaxis.set_label_position("left")
        else:
            cbar.ax.yaxis.set_ticks_position("right")
            cbar.ax.yaxis.set_label_position("right")

    return cbar


def _v025_apply_labelbar_ticks(cbar, mappable, lbres):
    ticks = _v025_get_ticks_from_alignment(cbar, mappable, lbres)

    if ticks is None:
        ticks = np.asarray(cbar.get_ticks(), dtype=float)

    ticks = np.asarray(ticks, dtype=float)

    stride = int(lbres.get("lbLabelStride", 1))

    if stride < 1:
        stride = 1

    auto_stride = bool_resource(lbres, "lbLabelAutoStride", False)
    max_labels = int(lbres.get("lbLabelMaxCount", 9))

    if auto_stride and ticks.size > max_labels:
        stride = int(np.ceil(ticks.size / max_labels))

    if stride > 1 and ticks.size > 0:
        ticks = ticks[::stride]

    if ticks.size > 0:
        cbar.set_ticks(ticks)

    labels = _v025_parse_sequence(lbres.get("lbLabelStrings", None))

    if labels is not None:
        labels = [str(item) for item in labels]

        if len(labels) != len(ticks):
            # 如果用户给的是每个 box 的标签，但 stride 后 ticks 少了，也同步 stride。
            if stride > 1 and len(labels) > len(ticks):
                labels = labels[::stride]

        if len(labels) == len(ticks):
            cbar.set_ticklabels(labels)
    else:
        fmt = lbres.get("lbLabelFormat", None)

        if fmt is not None and ticks.size > 0:
            cbar.set_ticklabels([_v025_format_tick(v, fmt) for v in ticks])

    label_size = lbres.get("lbLabelFontHeightF", None)
    label_color = lbres.get("lbLabelFontColor", None)
    tick_color = lbres.get("lbTickMarkColor", label_color)
    tick_length = lbres.get("lbTickLengthF", None)
    tick_width = lbres.get("lbTickThicknessF", None)

    tick_kwargs = {}

    if label_size is not None:
        tick_kwargs["labelsize"] = float(label_size)

    if label_color is not None:
        tick_kwargs["labelcolor"] = label_color

    if tick_color is not None:
        tick_kwargs["colors"] = tick_color

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

    orientation = _normalize_orientation(lbres)

    if orientation == "horizontal":
        texts = cbar.ax.get_xticklabels()
    else:
        texts = cbar.ax.get_yticklabels()

    for text in texts:
        text.set_rotation(angle)

        if weight is not None:
            text.set_fontweight(weight)

        if label_color is not None:
            text.set_color(label_color)

    return cbar


def _v025_apply_labelbar_title(cbar, lbres):
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
                str(title),
                fontsize=size,
                color=color,
                fontweight=weight,
                pad=pad,
            )
        else:
            cbar.ax.set_xlabel(
                str(title),
                fontsize=size,
                color=color,
                fontweight=weight,
                labelpad=pad,
            )
    else:
        cbar.ax.set_ylabel(
            str(title),
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


def _v025_apply_labelbar_box(cbar, lbres):
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
    separator_width = float(lbres.get("lbBoxSeparatorLineThicknessF", linewidth))

    cbar.outline.set_visible(True)
    cbar.outline.set_edgecolor(color)
    cbar.outline.set_linewidth(linewidth)

    if hasattr(cbar, "solids") and cbar.solids is not None:
        try:
            cbar.solids.set_edgecolor(color)
            cbar.solids.set_linewidth(separator_width)
        except Exception:
            pass

    return cbar


try:
    _climara_v025_base_add_labelbar
except NameError:
    _climara_v025_base_add_labelbar = add_labelbar


def add_labelbar(fig, ax, mappable, lbres: dict | None = None, cax=None, pmres=None):
    """Add an NCL-style labelbar with stronger resource handling."""
    lbres = _merge_labelbar_resources(lbres, pmres)
    lbres = _normalize_labelbar_color_resources(lbres)

    if not bool_resource(lbres, "lbLabelBarOn", True):
        return None

    display_mode = str(lbres.get("pmLabelBarDisplayMode", "Always")).lower()

    if display_mode in ["never", "no", "false", "none", "off"]:
        return None

    orientation = _normalize_orientation(lbres)

    if cax is None:
        cax = _manual_cax_from_pm(fig, ax, lbres)

    drawedges = bool_resource(lbres, "lbBoxLinesOn", True)

    extend = lbres.get("lbExtend", None)

    colorbar_kwargs = {
        "orientation": orientation,
        "drawedges": drawedges,
    }

    if extend is not None:
        colorbar_kwargs["extend"] = extend

    if cax is not None:
        cbar = fig.colorbar(
            mappable,
            cax=cax,
            **colorbar_kwargs,
        )
    else:
        cbar = fig.colorbar(
            mappable,
            ax=ax,
            shrink=float(lbres.get("lbShrinkF", 0.82)),
            pad=float(lbres.get("lbPadF", 0.06)),
            aspect=float(lbres.get("lbAspectF", 28)),
            **colorbar_kwargs,
        )

    _v025_apply_labelbar_axis(cbar, lbres)
    _v025_apply_labelbar_ticks(cbar, mappable, lbres)
    _v025_apply_labelbar_title(cbar, lbres)
    _v025_apply_labelbar_box(cbar, lbres)

    return cbar

# climara v0.2.5 labelbar resource override end

# climara v0.2.5b labelbar string fix begin

def _v025_select_indices(n, stride=1, auto_stride=False, max_count=9):
    if n <= 0:
        return np.asarray([], dtype=int)

    stride = max(1, int(stride))

    if auto_stride and n > max_count:
        idx = np.linspace(0, n - 1, int(max_count))
        idx = np.unique(np.round(idx).astype(int))
        return idx

    if stride > 1:
        return np.arange(0, n, stride, dtype=int)

    return np.arange(0, n, dtype=int)


def _v025_ticks_for_label_strings(cbar, mappable, lbres, labels):
    explicit = _v025_parse_float_sequence(lbres.get("lbLabelPositions", None))

    if explicit is not None and len(explicit) == len(labels):
        return np.asarray(explicit, dtype=float)

    boundaries = _v025_get_boundaries_from_mappable(mappable)

    if boundaries is not None:
        alignment = str(lbres.get("lbLabelAlignment", "BoxCenters"))
        alignment = alignment.replace("_", "").replace("-", "").lower()

        centers = 0.5 * (boundaries[:-1] + boundaries[1:])

        if alignment in ["externaledges", "outeredges", "edges", "boundaries"]:
            base = boundaries
        elif alignment in ["interioredges", "internaledges", "inneredges"]:
            base = boundaries[1:-1] if boundaries.size > 2 else boundaries
        else:
            base = centers

        base = np.asarray(base, dtype=float)

        if base.size == len(labels):
            return base

        if base.size >= 2:
            return np.linspace(float(base[0]), float(base[-1]), len(labels))

    ticks = np.asarray(cbar.get_ticks(), dtype=float)

    if ticks.size == len(labels):
        return ticks

    if ticks.size >= 2:
        return np.linspace(float(ticks[0]), float(ticks[-1]), len(labels))

    return np.arange(len(labels), dtype=float)


def _v025_apply_labelbar_ticks(cbar, mappable, lbres):
    labels = _v025_parse_sequence(lbres.get("lbLabelStrings", None))

    stride = int(lbres.get("lbLabelStride", 1))

    if stride < 1:
        stride = 1

    auto_stride = bool_resource(lbres, "lbLabelAutoStride", False)
    max_labels = int(lbres.get("lbLabelMaxCount", 9))

    if labels is not None:
        labels = [str(item) for item in labels]
        ticks = _v025_ticks_for_label_strings(cbar, mappable, lbres, labels)

        idx = _v025_select_indices(
            len(labels),
            stride=stride,
            auto_stride=auto_stride,
            max_count=max_labels,
        )

        labels = [labels[i] for i in idx]
        ticks = np.asarray(ticks, dtype=float)[idx]

        cbar.set_ticks(ticks)
        cbar.set_ticklabels(labels)

    else:
        ticks = _v025_get_ticks_from_alignment(cbar, mappable, lbres)

        if ticks is None:
            ticks = np.asarray(cbar.get_ticks(), dtype=float)

        ticks = np.asarray(ticks, dtype=float)

        if auto_stride and ticks.size > max_labels:
            stride = int(np.ceil(ticks.size / max_labels))

        if stride > 1 and ticks.size > 0:
            ticks = ticks[::stride]

        if ticks.size > 0:
            cbar.set_ticks(ticks)

        fmt = lbres.get("lbLabelFormat", None)

        if fmt is not None and ticks.size > 0:
            cbar.set_ticklabels([_v025_format_tick(v, fmt) for v in ticks])

    label_size = lbres.get("lbLabelFontHeightF", None)
    label_color = lbres.get("lbLabelFontColor", None)
    tick_color = lbres.get("lbTickMarkColor", label_color)
    tick_length = lbres.get("lbTickLengthF", None)
    tick_width = lbres.get("lbTickThicknessF", None)

    tick_kwargs = {}

    if label_size is not None:
        tick_kwargs["labelsize"] = float(label_size)

    if label_color is not None:
        tick_kwargs["labelcolor"] = label_color

    if tick_color is not None:
        tick_kwargs["colors"] = tick_color

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

    orientation = _normalize_orientation(lbres)

    if orientation == "horizontal":
        texts = cbar.ax.get_xticklabels()
    else:
        texts = cbar.ax.get_yticklabels()

    for text in texts:
        text.set_rotation(angle)

        if weight is not None:
            text.set_fontweight(weight)

        if label_color is not None:
            text.set_color(label_color)

    return cbar

# climara v0.2.5b labelbar string fix end

# climara v0.2.6b labelbar map-spacing fix begin

def _v026b_needs_extra_bottom_space(lbres):
    """Return True when map tick labels need extra room above horizontal labelbar."""
    orientation = _normalize_orientation(lbres)

    if orientation != "horizontal":
        return False

    if not bool_resource(lbres, "gsnAutoLabelBarSpacingOn", True):
        return False

    if bool_resource(lbres, "mpGridLabelsOn", False):
        return True

    if bool_resource(lbres, "tmXBLabelsOn", False):
        return True

    return False


try:
    _climara_v026b_base_manual_cax_from_pm
except NameError:
    _climara_v026b_base_manual_cax_from_pm = _manual_cax_from_pm


def _manual_cax_from_pm(fig, ax, lbres):
    """Manual colorbar axes with safer map-label spacing."""
    orientation = _normalize_orientation(lbres)
    lbres = dict(lbres or {})

    if (
        orientation == "horizontal"
        and "pmLabelBarOrthogonalPosF" not in lbres
        and _v026b_needs_extra_bottom_space(lbres)
    ):
        lbres["pmLabelBarOrthogonalPosF"] = 0.13

    return _climara_v026b_base_manual_cax_from_pm(fig, ax, lbres)

# climara v0.2.6b labelbar map-spacing fix end


# climara v0.3.0 NCL-style labelbar polish begin

def _ncl_labelbar_font_height_to_points(value):
    """Convert NCL-style lb*FontHeightF to Matplotlib point size.

    In NCL, values such as 0.010 are common normalized font heights.
    Matplotlib interprets fontsize as points, so 0.010 would be invisible.
    """
    value = float(value)

    if 0.0 < value < 1.0:
        return value * 1000.0

    return value


def _ncl_labelbar_extend_from_style(lbres):
    style = str(lbres.get("lbBoxEndCapStyle", "")).lower()

    if "triangleboth" in style or "both" in style:
        return "both"

    if "trianglelow" in style or "min" in style or "low" in style:
        return "min"

    if "trianglehigh" in style or "max" in style or "high" in style:
        return "max"

    return lbres.get("lbExtend", None)


def _v030_apply_labelbar_ticks(cbar, mappable, lbres):
    labels = _v025_parse_sequence(lbres.get("lbLabelStrings", None))

    stride = int(lbres.get("lbLabelStride", 1))

    if stride < 1:
        stride = 1

    auto_stride = bool_resource(lbres, "lbLabelAutoStride", False)
    max_labels = int(lbres.get("lbLabelMaxCount", 99))

    # For NCL-like explicit-level labelbars, edge labels are usually desired.
    if (
        "lbLabelAlignment" not in lbres
        and _v025_get_boundaries_from_mappable(mappable) is not None
    ):
        lbres = dict(lbres)
        lbres["lbLabelAlignment"] = "ExternalEdges"

    if labels is not None:
        labels = [str(item) for item in labels]
        ticks = _v025_ticks_for_label_strings(cbar, mappable, lbres, labels)

        idx = _v025_select_indices(
            len(labels),
            stride=stride,
            auto_stride=auto_stride,
            max_count=max_labels,
        )

        labels = [labels[i] for i in idx]
        ticks = np.asarray(ticks, dtype=float)[idx]

        cbar.set_ticks(ticks)
        cbar.set_ticklabels(labels)
    else:
        ticks = _v025_get_ticks_from_alignment(cbar, mappable, lbres)

        if ticks is None:
            ticks = np.asarray(cbar.get_ticks(), dtype=float)

        ticks = np.asarray(ticks, dtype=float)

        if auto_stride and ticks.size > max_labels:
            stride = int(np.ceil(ticks.size / max_labels))

        if stride > 1 and ticks.size > 0:
            ticks = ticks[::stride]

        if ticks.size > 0:
            cbar.set_ticks(ticks)

        fmt = lbres.get("lbLabelFormat", None)

        if fmt is not None and ticks.size > 0:
            cbar.set_ticklabels([_v025_format_tick(v, fmt) for v in ticks])

    label_size = lbres.get("lbLabelFontHeightF", None)
    label_color = lbres.get("lbLabelFontColor", None)
    tick_color = lbres.get("lbTickMarkColor", label_color)
    tick_length = lbres.get("lbTickLengthF", 3.0)
    tick_width = lbres.get("lbTickThicknessF", 0.6)

    tick_kwargs = {
        "length": float(tick_length),
        "width": float(tick_width),
        "pad": float(lbres.get("lbLabelOffsetF", 2.0)),
    }

    if label_size is not None:
        tick_kwargs["labelsize"] = _ncl_labelbar_font_height_to_points(label_size)

    if label_color is not None:
        tick_kwargs["labelcolor"] = label_color

    if tick_color is not None:
        tick_kwargs["colors"] = tick_color

    cbar.ax.tick_params(**tick_kwargs)

    if not bool_resource(lbres, "lbTickMarksOn", True):
        cbar.ax.tick_params(length=0)

    angle = float(lbres.get("lbLabelAngleF", 0.0))
    weight = lbres.get("lbLabelFontWeight", None)

    orientation = _normalize_orientation(lbres)

    if orientation == "horizontal":
        texts = cbar.ax.get_xticklabels()
    else:
        texts = cbar.ax.get_yticklabels()

    for text in texts:
        text.set_rotation(angle)

        if weight is not None:
            text.set_fontweight(weight)

        if label_color is not None:
            text.set_color(label_color)

    return cbar


def _v030_apply_labelbar_title(cbar, lbres):
    title = lbres.get("lbTitleString", None)

    if title is None:
        return cbar

    orientation = _normalize_orientation(lbres)
    position = str(lbres.get("lbTitlePosition", "bottom")).lower()
    size = _ncl_labelbar_font_height_to_points(
        lbres.get("lbTitleFontHeightF", 10)
    )
    color = lbres.get("lbTitleFontColor", "black")
    weight = lbres.get("lbTitleFontWeight", "normal")
    pad = float(lbres.get("lbTitleOffsetF", 2.0))

    if orientation == "horizontal":
        if position in ["top", "above"]:
            cbar.ax.set_title(
                str(title),
                fontsize=size,
                color=color,
                fontweight=weight,
                pad=pad,
            )
        else:
            cbar.ax.set_xlabel(
                str(title),
                fontsize=size,
                color=color,
                fontweight=weight,
                labelpad=pad,
            )
    else:
        cbar.ax.set_ylabel(
            str(title),
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


try:
    _climara_v030_base_add_labelbar
except NameError:
    _climara_v030_base_add_labelbar = add_labelbar


def add_labelbar(fig, ax, mappable, lbres: dict | None = None, cax=None, pmres=None):
    """Add an NCL-style labelbar with NCL font-height semantics."""
    lbres = _merge_labelbar_resources(lbres, pmres)
    lbres = _normalize_labelbar_color_resources(lbres)

    if not bool_resource(lbres, "lbLabelBarOn", True):
        return None

    display_mode = str(lbres.get("pmLabelBarDisplayMode", "Always")).lower()

    if display_mode in ["never", "no", "false", "none", "off"]:
        return None

    orientation = _normalize_orientation(lbres)

    if cax is None:
        cax = _manual_cax_from_pm(fig, ax, lbres)

    drawedges = bool_resource(lbres, "lbBoxLinesOn", True)

    extend = _ncl_labelbar_extend_from_style(lbres)

    colorbar_kwargs = {
        "orientation": orientation,
        "drawedges": drawedges,
    }

    if extend is not None:
        colorbar_kwargs["extend"] = extend

    if cax is not None:
        cbar = fig.colorbar(
            mappable,
            cax=cax,
            **colorbar_kwargs,
        )
    else:
        cbar = fig.colorbar(
            mappable,
            ax=ax,
            shrink=float(lbres.get("lbShrinkF", 0.82)),
            pad=float(lbres.get("lbPadF", 0.06)),
            aspect=float(lbres.get("lbAspectF", 28)),
            **colorbar_kwargs,
        )

    _v025_apply_labelbar_axis(cbar, lbres)
    _v030_apply_labelbar_ticks(cbar, mappable, lbres)
    _v030_apply_labelbar_title(cbar, lbres)
    _v025_apply_labelbar_box(cbar, lbres)

    # Match NCL-like compact horizontal labelbar appearance.
    if orientation == "horizontal":
        cbar.ax.xaxis.set_ticks_position(
            "top" if str(lbres.get("lbLabelPosition", "bottom")).lower() == "top" else "bottom"
        )

    return cbar

# climara v0.3.0 NCL-style labelbar polish end
