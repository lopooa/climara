"""
GSN/HLU-style panel helpers.

The first-order layout follows gsn_panel_return in NCL gsn_code.ncl:
dims, row spec, panel bounds, main-string top reservation, whitespace,
scale, and viewport assignment.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import ceil, sqrt
from typing import Any, Mapping, Sequence

from ._labelbar_object import build_hlu_labelbar
from ._objects import HluPanel, as_resources
from ._text_item import HluTextItem

def _labelbar_bottom_rect_to_view_rect(rect):
    if rect is None:
        return None

    x, bottom, width, height = rect
    return (x, bottom + height, width, height)


@dataclass
class HluPanelItem:
    """A plot item placed inside a panel."""

    plot: Any
    index: int
    rect: tuple[float, float, float, float]
    resources: dict[str, Any] = field(default_factory=dict)


@dataclass
class HluPanelLayout:
    """Panel layout in normalized device coordinates."""

    nplots: int
    nrows: int
    ncols: int
    rects: list[tuple[float, float, float, float]]
    resources: dict[str, Any] = field(default_factory=dict)
    row_spec: list[int] = field(default_factory=list)
    scale: float = 1.0
    bounds: tuple[float, float, float, float] = (0.0, 1.0, 0.0, 1.0)
    whitespace: tuple[float, float] = (0.0, 0.0)
    labelbar_rect: tuple[float, float, float, float] | None = None


def _as_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, str):
        return value.strip().lower() in {"true", "t", "yes", "y", "1", "on"}
    return bool(value)


def _as_float(resources: Mapping[str, Any], key: str, default: float) -> float:
    try:
        return float(resources.get(key, default))
    except (TypeError, ValueError):
        return default


def _as_int(resources: Mapping[str, Any], key: str, default: int) -> int:
    try:
        return int(resources.get(key, default))
    except (TypeError, ValueError):
        return default


def _as_list_value(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    try:
        return list(value)
    except TypeError:
        return [value]


def _normalize_resources(
    dims: Any = None,
    resources: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> tuple[Any, dict[str, Any]]:
    if isinstance(dims, Mapping) and resources is None:
        resources = dims
        dims = None

    res = as_resources(resources, **kwargs)
    return dims, res


def _panel_shape(
    nplots: int,
    dims: Any,
    resources: Mapping[str, Any],
) -> tuple[int, int, list[int]]:
    if nplots <= 0:
        return 0, 0, []

    row_spec_on = _as_bool(resources.get("gsnPanelRowSpec"), False)

    if dims is None:
        if "gsnPanelRows" in resources or "gsnPanelColumns" in resources:
            nrows = max(1, _as_int(resources, "gsnPanelRows", 1))
            ncols = max(1, _as_int(resources, "gsnPanelColumns", nplots))
            return nrows, ncols, [ncols for _ in range(nrows)]

        ncols = max(1, ceil(sqrt(nplots)))
        nrows = max(1, ceil(nplots / ncols))
        return nrows, ncols, [ncols for _ in range(nrows)]

    dims_list = [int(item) for item in _as_list_value(dims)]

    if row_spec_on:
        row_spec = [max(0, item) for item in dims_list]
        nrows = len(row_spec)
        ncols = max(row_spec) if row_spec else 0
        return nrows, ncols, row_spec

    if len(dims_list) != 2:
        raise ValueError(
            "NCL gsn_panel dims must be (nrows, ncols), unless gsnPanelRowSpec is True."
        )

    nrows = max(1, dims_list[0])
    ncols = max(1, dims_list[1])
    return nrows, ncols, [ncols for _ in range(nrows)]


def _main_string_value(resources: Mapping[str, Any]) -> Any:
    return resources.get("gsnPanelMainString", resources.get("txString", ""))


def _panel_main_font_height(resources: Mapping[str, Any]) -> float:
    return float(
        resources.get(
            "gsnPanelMainFontHeightF",
            resources.get("txFontHeightF", 0.02),
        )
    )


def _panel_bounds(resources: Mapping[str, Any]) -> tuple[float, float, float, float]:
    x_left = _as_float(resources, "gsnPanelLeft", 0.0)
    x_right = _as_float(resources, "gsnPanelRight", 1.0)
    y_bottom = _as_float(resources, "gsnPanelBottom", 0.0)
    y_top = _as_float(resources, "gsnPanelTop", 1.0)

    main_string = _main_string_value(resources)
    top_given = "gsnPanelTop" in resources

    if main_string not in (None, "") and not top_given:
        main_font_height = _panel_main_font_height(resources)

        if "gsnPanelMainPosYF" in resources:
            y_top = min(1.0, float(resources["gsnPanelMainPosYF"]) - 0.03)
        elif "txPosYF" in resources:
            y_top = min(1.0, float(resources["txPosYF"]) - 0.03)
        else:
            y_top = min(1.0, 0.96 - main_font_height)

    x_left = max(0.0, min(1.0, x_left))
    x_right = max(0.0, min(1.0, x_right))
    y_bottom = max(0.0, min(1.0, y_bottom))
    y_top = max(0.0, min(1.0, y_top))

    if x_right <= x_left:
        raise ValueError("gsnPanelRight must be greater than gsnPanelLeft.")
    if y_top <= y_bottom:
        raise ValueError("gsnPanelTop must be greater than gsnPanelBottom.")

    return x_left, x_right, y_bottom, y_top


def _panel_white_percent(resources: Mapping[str, Any], key: str) -> float:
    value = _as_float(resources, key, 1.0)
    if value < 0.0 or value >= 100.0:
        return 1.0
    return value


def _plot_old_viewport(plot: Any) -> tuple[float, float, float, float]:
    resources = getattr(plot, "resources", {})
    if not isinstance(resources, Mapping):
        resources = {}

    x = float(resources.get("vpXF", 0.10))
    y_top = float(resources.get("vpYF", 0.90))
    width = float(resources.get("vpWidthF", 0.80))
    height = float(resources.get("vpHeightF", 0.60))

    width = max(width, 1.0e-6)
    height = max(height, 1.0e-6)

    return x, y_top, width, height


def _scale_plot_index(
    nplots: int,
    resources: Mapping[str, Any],
) -> int:
    index = _as_int(resources, "gsnPanelScalePlotIndex", -1)
    if 0 <= index < nplots:
        return index
    return 0


def _labelbar_orientation(resources: Mapping[str, Any]) -> str:
    return str(resources.get("lbOrientation", "horizontal")).lower()


def _panel_labelbar_on(resources: Mapping[str, Any]) -> bool:
    return _as_bool(resources.get("gsnPanelLabelBar"), False)


def _first_plot_resource(plots: Sequence[Any], *names: str) -> Any:
    for plot in plots:
        resources = getattr(plot, "resources", None)
        if isinstance(resources, Mapping):
            for name in names:
                if name in resources:
                    return resources[name]
        for name in names:
            if hasattr(plot, name):
                value = getattr(plot, name)
                if value is not None:
                    return value
    return None


def _compute_labelbar_extent(
    nplots: int,
    nrows: int,
    ncols: int,
    plot_width: float,
    plot_height: float,
    total_width: float,
    total_height: float,
    xwsp: float,
    ywsp: float,
    resources: Mapping[str, Any],
) -> tuple[bool, float, float]:
    if not _panel_labelbar_on(resources):
        return True, 0.0, 0.0

    vertical = _labelbar_orientation(resources).startswith("v")

    if vertical:
        labelbar_width = 0.20 * plot_width + 2.0 * xwsp
        if nplots > 1 and nrows > 1:
            labelbar_height = (nrows - 1) * total_height
        else:
            labelbar_height = plot_height
        return False, labelbar_width, labelbar_height

    labelbar_height = 0.20 * plot_height + 2.0 * ywsp
    if nplots > 1 and ncols > 1:
        labelbar_width = (ncols - 1) * total_width
    else:
        labelbar_width = plot_width

    return True, labelbar_width, labelbar_height


def compute_panel_rects(
    nplots: int,
    resources: Mapping[str, Any] | None = None,
    dims: Any = None,
) -> HluPanelLayout:
    """Compute NCL-style panel plot viewports."""

    res = dict(resources or {})
    nrows, ncols, row_spec = _panel_shape(nplots, dims, res)

    if nplots <= 0:
        return HluPanelLayout(0, 0, 0, [], res, row_spec=row_spec)

    x_left, x_right, y_bottom, y_top = _panel_bounds(res)

    xwsp_percent = _panel_white_percent(res, "gsnPanelXWhiteSpacePercent")
    ywsp_percent = _panel_white_percent(res, "gsnPanelYWhiteSpacePercent")

    base_width = float(res.get("climaraBasePlotWidthF", 0.80))
    base_height = float(res.get("climaraBasePlotHeightF", 0.60))

    plot_width = max(base_width, 1.0e-6)
    plot_height = max(base_height, 1.0e-6)

    xwsp = xwsp_percent / 100.0 * plot_width
    ywsp = ywsp_percent / 100.0 * plot_height

    total_width = 2.0 * xwsp + plot_width
    total_height = 2.0 * ywsp + plot_height

    labelbar_horizontal, labelbar_width, labelbar_height = _compute_labelbar_extent(
        nplots,
        nrows,
        ncols,
        plot_width,
        plot_height,
        total_width,
        total_height,
        xwsp,
        ywsp,
        res,
    )

    xrange = x_right - x_left
    yrange = y_top - y_bottom

    if labelbar_horizontal:
        row_scale = yrange / max(nrows * total_height + labelbar_height, 1.0e-12)
        col_scale = xrange / max(ncols * total_width, 1.0e-12)
        scale = min(col_scale, row_scale)
        yrange_for_plots = yrange - scale * labelbar_height
        xrange_for_plots = xrange
    else:
        row_scale = yrange / max(nrows * total_height, 1.0e-12)
        col_scale = xrange / max(ncols * total_width + labelbar_width, 1.0e-12)
        scale = min(col_scale, row_scale)
        xrange_for_plots = xrange - scale * labelbar_width
        yrange_for_plots = yrange

    new_plot_width = scale * plot_width
    new_plot_height = scale * plot_height

    xwsp = xwsp_percent / 100.0 * new_plot_width
    ywsp = ywsp_percent / 100.0 * new_plot_height

    new_total_width = 2.0 * xwsp + new_plot_width
    new_total_height = 2.0 * ywsp + new_plot_height

    panel_center = _as_bool(res.get("gsnPanelCenter"), True)

    y_space = yrange_for_plots - new_total_height * nrows
    row_tops = [
        y_top - ywsp - (y_space / 2.0 + new_total_height * row)
        for row in range(nrows)
    ]

    rects: list[tuple[float, float, float, float]] = []

    nplot = 0
    for row in range(nrows):
        if nplot >= nplots:
            break

        new_ncols = min(nplots - nplot, row_spec[row] if row < len(row_spec) else ncols)

        if panel_center:
            x_space = xrange_for_plots - new_total_width * new_ncols
        else:
            x_space = xrange_for_plots - new_total_width * ncols

        x_positions = [
            x_left + xwsp + (x_space / 2.0 + new_total_width * col)
            for col in range(new_ncols)
        ]

        for col in range(new_ncols):
            if nplot >= nplots:
                break

            vpx = x_positions[col]
            vpy = row_tops[row]

            x_override = res.get("gsnPanelXF")
            if isinstance(x_override, Sequence) and not isinstance(x_override, str):
                if nplot < len(x_override):
                    value = float(x_override[nplot])
                    if 0.0 <= value <= 1.0:
                        vpx = value

            y_override = res.get("gsnPanelYF")
            if isinstance(y_override, Sequence) and not isinstance(y_override, str):
                if nplot < len(y_override):
                    value = float(y_override[nplot])
                    if 0.0 <= value <= 1.0:
                        vpy = value

            rects.append((vpx, vpy - new_plot_height, new_plot_width, new_plot_height))
            nplot += 1

    labelbar_rect = None
    if _panel_labelbar_on(res):
        scaled_labelbar_width = scale * labelbar_width
        scaled_labelbar_height = scale * labelbar_height

        if labelbar_horizontal:
            width = float(res.get("pmLabelBarWidthF", scaled_labelbar_width))
            height = float(res.get("pmLabelBarHeightF", scaled_labelbar_height))
            top = max(ywsp + height, y_bottom - ywsp)
            left = x_left + ((x_right - x_left) - width) / 2.0
            left += float(res.get("pmLabelBarParallelPosF", 0.0))
            top += float(res.get("pmLabelBarOrthogonalPosF", 0.0))
            labelbar_rect = (left, top - height, width, height)
        else:
            width = float(res.get("pmLabelBarWidthF", scaled_labelbar_width))
            height = float(res.get("pmLabelBarHeightF", scaled_labelbar_height))
            left = min(1.0 - (xwsp + width), x_left + xrange_for_plots + xwsp)
            top = y_top - ((y_top - y_bottom) - height) / 2.0
            left += float(res.get("pmLabelBarOrthogonalPosF", 0.0))
            top += float(res.get("pmLabelBarParallelPosF", 0.0))
            labelbar_rect = (left, top - height, width, height)

    layout_resources = dict(res)
    layout_resources["ncl_dims"] = dims
    layout_resources["ncl_row_spec"] = list(row_spec)
    layout_resources["ncl_scale"] = scale
    layout_resources["ncl_xwsp"] = xwsp
    layout_resources["ncl_ywsp"] = ywsp

    return HluPanelLayout(
        nplots=nplots,
        nrows=nrows,
        ncols=ncols,
        rects=rects,
        resources=layout_resources,
        row_spec=list(row_spec),
        scale=scale,
        bounds=(x_left, x_right, y_bottom, y_top),
        whitespace=(xwsp, ywsp),
        labelbar_rect=_labelbar_bottom_rect_to_view_rect(labelbar_rect),
    )


def compute_gsn_panel_layout(
    nplots: int,
    resources: Mapping[str, Any] | None = None,
    dims: Any = None,
) -> HluPanelLayout:
    """Compatibility wrapper for NCL-style panel layout."""

    return compute_panel_rects(nplots, resources, dims)


def _attach_panel_item(plot: Any, item: HluPanelItem) -> Any:
    if hasattr(plot, "resources") and isinstance(plot.resources, dict):
        plot.resources["vpXF"] = item.rect[0]
        plot.resources["vpYF"] = item.rect[1] + item.rect[3]
        plot.resources["vpWidthF"] = item.rect[2]
        plot.resources["vpHeightF"] = item.rect[3]
        plot.resources["gsnPanelIndex"] = item.index
    return plot


def _panel_main_tx_resource(
    resources: Mapping[str, Any],
    suffix: str,
    default: Any,
) -> Any:
    explicit_name = f"gsnPanelMain{suffix}"
    tx_name = f"tx{suffix}"
    return resources.get(explicit_name, resources.get(tx_name, default))


def _build_panel_main_string(resources: Mapping[str, Any]):
    value = _main_string_value(resources)
    if value in (None, ""):
        return None

    x_left, x_right, y_bottom, y_top = _panel_bounds(resources)

    font_height = _panel_main_tx_resource(resources, "FontHeightF", 0.02)
    x = resources.get("gsnPanelMainPosXF", resources.get("txPosXF", 0.5))
    y = resources.get("gsnPanelMainPosYF", resources.get("txPosYF", y_top + 0.03))

    return HluTextItem(
        text=str(value),
        x=float(x),
        y=float(y),
        resources={
            "txJust": _panel_main_tx_resource(resources, "Just", resources.get("txJust", "CenterCenter")),
            "txFontHeightF": font_height,
            "txFontColor": _panel_main_tx_resource(resources, "FontColor", resources.get("txFontColor", "black")),
            "txAngleF": _panel_main_tx_resource(resources, "AngleF", resources.get("txAngleF", 0.0)),
            "coordinate_system": "ndc",
        },
    )


def _figure_string_value(values: list[Any], index: int) -> Any:
    if not values:
        return None
    if index < len(values):
        return values[index]
    return None


def _normalize_panel_figure_just(value: Any) -> str:
    key = str(value or "bottomright").replace("_", "").replace("-", "").lower()
    mapping = {
        "bottomright": "bottomright",
        "topright": "topright",
        "topleft": "topleft",
        "bottomleft": "bottomleft",
    }
    return mapping.get(key, "bottomright")


def _panel_figure_tx_resource(
    resources: Mapping[str, Any],
    suffix: str,
    default: Any,
) -> Any:
    return resources.get(
        f"gsnPanelFigureStrings{suffix}",
        resources.get(f"tx{suffix}", default),
    )


def _build_panel_figure_string(
    resources: Mapping[str, Any],
    index: int,
) -> HluTextItem | None:
    values = _as_list_value(resources.get("gsnPanelFigureStrings"))
    value = _figure_string_value(values, index)

    if value in (None, ""):
        return None

    just = _normalize_panel_figure_just(
        resources.get("gsnPanelFigureStringsJust", resources.get("amJust", "bottomright"))
    )

    text_resources: dict[str, Any] = {
        "coordinate_system": "annotation",
        "climaraTextRegion": "data",
        "climaraPanelFigureString": True,
        "amZone": resources.get("amZone", 0),
        "amJust": just,
        "amResizeNotify": resources.get("amResizeNotify", True),
        "txFontHeightF": _panel_figure_tx_resource(resources, "FontHeightF", 0.014),
        "txFontColor": _panel_figure_tx_resource(resources, "FontColor", "black"),
        "txPerimOn": _panel_figure_tx_resource(resources, "PerimOn", True),
        "txBackgroundFillColor": _panel_figure_tx_resource(resources, "BackgroundFillColor", 0),
    }

    if "amParallelPosF" in resources:
        text_resources["amParallelPosF"] = resources["amParallelPosF"]
    if "amOrthogonalPosF" in resources:
        text_resources["amOrthogonalPosF"] = resources["amOrthogonalPosF"]

    return HluTextItem(
        text=str(value),
        x=0.5,
        y=0.5,
        resources=text_resources,
    )


def _plot_resources(plot: Any) -> dict[str, Any]:
    value = getattr(plot, "resources", None)
    if isinstance(value, Mapping):
        return dict(value)
    return {}


def _plot_attr_or_resource(plot: Any, resources: Mapping[str, Any], *names: str) -> Any:
    for name in names:
        if name in resources:
            return resources[name]
    for name in names:
        if hasattr(plot, name):
            value = getattr(plot, name)
            if value is not None:
                return value
    return None


def _is_contour_plot(plot: Any, resources: Mapping[str, Any]) -> bool:
    plot_type = str(resources.get("plot_type", "")).lower()
    if plot_type == "contour":
        return True
    return "contour" in plot.__class__.__name__.lower()


def _get_panel_labelbar_info_from_plot(plot: Any) -> dict[str, Any]:
    resources = _plot_resources(plot)

    info: dict[str, Any] = {
        "panel_labelbar": False,
        "label_strings": None,
        "fill_colors": None,
        "fill_patterns": None,
        "fill_scales": None,
        "mono_fill_color": False,
        "mono_fill_pattern": False,
        "mono_fill_scale": False,
        "end_style": "IncludeOuterBoxes",
        "cap_style": "RectangleEnds",
        "label_alignment": "InteriorEdges",
        "subset_stuff": False,
        "levels": None,
    }

    if not _is_contour_plot(plot, resources):
        return info

    fill_on = _as_bool(resources.get("cnFillOn"), False)
    if not fill_on:
        return info

    info["panel_labelbar"] = True
    info["fill_colors"] = _plot_attr_or_resource(
        plot,
        resources,
        "cnFillColors",
        "cnFillPalette",
        "colors",
    )
    info["fill_patterns"] = resources.get("cnFillPatterns")
    info["fill_scales"] = resources.get("cnFillScales")
    info["mono_fill_pattern"] = resources.get("cnMonoFillPattern", False)
    info["mono_fill_scale"] = resources.get("cnMonoFillScale", False)
    info["mono_fill_color"] = resources.get("cnMonoFillColor", False)
    info["levels"] = _plot_attr_or_resource(plot, resources, "cnLevels", "levels")
    info["end_style"] = resources.get("cnLabelBarEndStyle", "IncludeOuterBoxes")
    info["cap_style"] = resources.get("lbBoxEndCapStyle", "RectangleEnds")
    info["label_alignment"] = resources.get("lbLabelAlignment", "InteriorEdges")
    info["label_strings"] = resources.get("lbLabelStrings")

    if info["fill_scales"] is None:
        info["fill_scales"] = -1
    if info["fill_patterns"] is None:
        info["fill_patterns"] = -1

    info["subset_stuff"] = True
    return info


def _get_panel_labelbar_info(plots: Sequence[Any]) -> dict[str, Any]:
    for plot in plots:
        info = _get_panel_labelbar_info_from_plot(plot)
        if info.get("panel_labelbar"):
            return info

    return {
        "panel_labelbar": False,
        "label_strings": None,
        "fill_colors": None,
        "levels": None,
        "label_alignment": "InteriorEdges",
        "cap_style": "RectangleEnds",
        "end_style": "IncludeOuterBoxes",
        "subset_stuff": False,
    }


def _build_shared_labelbar(
    plots: Sequence[Any],
    resources: Mapping[str, Any],
    layout: HluPanelLayout,
):
    if not _panel_labelbar_on(resources):
        return None

    info = _get_panel_labelbar_info(plots)

    colors = resources.get("lbFillColors")
    if colors is None:
        colors = info.get("fill_colors")
    if colors is None:
        colors = resources.get("cnFillColors", resources.get("cnFillPalette"))
    if colors is None:
        colors = _first_plot_resource(plots, "cnFillColors", "colors", "cnFillPalette")

    levels = resources.get("lbLevels")
    if levels is None:
        levels = info.get("levels")
    if levels is None:
        levels = resources.get("cnLevels")
    if levels is None:
        levels = _first_plot_resource(plots, "cnLevels", "levels")

    labels = resources.get("lbLabelStrings", resources.get("lbLabels"))
    if labels is None:
        labels = info.get("label_strings")

    if colors is None or layout.labelbar_rect is None:
        return None

    labelbar_res = {
        "rect": layout.labelbar_rect,
        "lbOrientation": resources.get("lbOrientation", "horizontal"),
        "lbLabelFontHeightF": resources.get("lbLabelFontHeightF", 0.012),
        "lbLabelFontColor": resources.get("lbLabelFontColor", "black"),
        "lbTickLengthF": resources.get("lbTickLengthF", 0.008),
        "lbLabelGapF": resources.get("lbLabelGapF", 0.010),
        "colors": colors,
        "lbLabelAlignment": resources.get("lbLabelAlignment", info.get("label_alignment", "InteriorEdges")),
        "lbBoxEndCapStyle": resources.get("lbBoxEndCapStyle", info.get("cap_style", "RectangleEnds")),
        "EndStyle": resources.get("EndStyle", info.get("end_style", "IncludeOuterBoxes")),
        "SubsetStuff": resources.get("SubsetStuff", info.get("subset_stuff", False)),
    }

    if levels is not None:
        labelbar_res["levels"] = levels
    if labels is not None:
        labelbar_res["labels"] = labels

    if info.get("fill_patterns") is not None:
        labelbar_res["lbFillPatterns"] = info["fill_patterns"]
    if info.get("fill_scales") is not None:
        labelbar_res["lbFillScales"] = info["fill_scales"]
    if info.get("mono_fill_color") is not None:
        labelbar_res["lbMonoFillColor"] = info["mono_fill_color"]
    if info.get("mono_fill_pattern") is not None:
        labelbar_res["lbMonoFillPattern"] = info["mono_fill_pattern"]
    if info.get("mono_fill_scale") is not None:
        labelbar_res["lbMonoFillScale"] = info["mono_fill_scale"]

    return build_hlu_labelbar(labelbar_res)

def _panel_add_plot(panel: HluPanel, plot: Any) -> None:
    if hasattr(panel, "add_plot"):
        panel.add_plot(plot)
    elif hasattr(panel, "plots"):
        panel.plots.append(plot)


def _panel_add_child(panel: HluPanel, child: Any) -> None:
    if hasattr(panel, "add_child"):
        panel.add_child(child)
    elif hasattr(panel, "children"):
        panel.children.append(child)


def build_panel(
    plots: Sequence[Any],
    dims: Any = None,
    resources: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> HluPanel:
    """Build a backend-neutral HLU panel object using NCL panel semantics."""

    dims, res = _normalize_resources(dims, resources, **kwargs)
    plot_list = list(plots)

    scale_index = _scale_plot_index(len(plot_list), res) if plot_list else 0
    if plot_list:
        _, _, base_width, base_height = _plot_old_viewport(plot_list[scale_index])
        res.setdefault("climaraBasePlotWidthF", base_width)
        res.setdefault("climaraBasePlotHeightF", base_height)

    layout = compute_panel_rects(len(plot_list), res, dims)

    panel = HluPanel(
        name=str(res.get("name", "panel")),
        resources=res,
        plots=[],
    )

    panel.resources["layout"] = layout
    panel.resources["ncl_dims"] = dims
    panel.resources["ncl_row_spec"] = layout.row_spec
    panel.resources["ncl_scale"] = layout.scale

    for index, plot in enumerate(plot_list):
        if index >= len(layout.rects):
            break

        item = HluPanelItem(
            plot=plot,
            index=index,
            rect=layout.rects[index],
            resources=dict(res),
        )

        _attach_panel_item(plot, item)

        figure_string = _build_panel_figure_string(res, index)
        if figure_string is not None:
            if hasattr(plot, "add_child"):
                plot.add_child(figure_string)
            elif hasattr(plot, "children"):
                plot.children.append(figure_string)

        _panel_add_plot(panel, plot)
        _panel_add_child(panel, item)

    labelbar = _build_shared_labelbar(plot_list, res, layout)
    if labelbar is not None:
        _panel_add_child(panel, labelbar)
        panel.resources["labelbar"] = labelbar

    main_string = _build_panel_main_string(res)
    if main_string is not None:
        _panel_add_child(panel, main_string)
        panel.resources["main_string"] = main_string

    return panel


def gsn_panel(
    wks: Any,
    plots: Sequence[Any],
    dims: Any = None,
    resources: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> HluPanel:
    """Create a GSN-style panel and attach it to a workstation if possible."""

    panel = build_panel(plots, dims, resources, **kwargs)

    if hasattr(wks, "add_child"):
        wks.add_child(panel)
    elif hasattr(wks, "children"):
        wks.children.append(panel)

    if _as_bool(panel.resources.get("gsnDraw"), True):
        panel.draw()

    if _as_bool(panel.resources.get("gsnFrame"), False) and hasattr(wks, "frame"):
        wks.frame()

    return panel


def ncl_panel(
    wks: Any,
    plots: Sequence[Any],
    dims: Any = None,
    resources: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> HluPanel:
    """Alias for gsn_panel."""

    return gsn_panel(wks, plots, dims, resources, **kwargs)


def gsn_panel_maps(
    wks: Any,
    plots: Sequence[Any],
    dims: Any = None,
    resources: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> HluPanel:
    """Panel helper for map plots."""

    return gsn_panel(wks, plots, dims, resources, **kwargs)


def ncl_panel_maps(
    wks: Any,
    plots: Sequence[Any],
    dims: Any = None,
    resources: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> HluPanel:
    """Alias for gsn_panel_maps."""

    return gsn_panel_maps(wks, plots, dims, resources, **kwargs)


def panel(
    plots: Sequence[Any],
    dims: Any = None,
    resources: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> HluPanel:
    """Build a panel object without attaching it to a workstation."""

    return build_panel(plots, dims, resources, **kwargs)


def draw_panel(
    wks: Any,
    plots: Sequence[Any],
    dims: Any = None,
    resources: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> HluPanel:
    """Compatibility alias for gsn_panel."""

    return gsn_panel(wks, plots, dims, resources, **kwargs)


def _set_panel_tick_policy(*args: Any, **kwargs: Any) -> Any:
    if args:
        return args[0]
    return None


def _add_panel_labelbar(*args: Any, **kwargs: Any) -> None:
    return None


def _add_panel_strings(*args: Any, **kwargs: Any) -> None:
    return None


__all__ = [
    "HluPanelItem",
    "HluPanelLayout",
    "build_panel",
    "compute_gsn_panel_layout",
    "compute_panel_rects",
    "draw_panel",
    "gsn_panel",
    "gsn_panel_maps",
    "ncl_panel",
    "ncl_panel_maps",
    "panel",
]
