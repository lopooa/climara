from __future__ import annotations

from typing import Any

LABEL_ALIGNMENT_BOX_CENTERS = "BoxCenters"
LABEL_ALIGNMENT_INTERIOR_EDGES = "InteriorEdges"
LABEL_ALIGNMENT_EXTERNAL_EDGES = "ExternalEdges"

ORIENTATION_HORIZONTAL = "Horizontal"
ORIENTATION_VERTICAL = "Vertical"

END_STYLE_INCLUDE_OUTER_BOXES = "IncludeOuterBoxes"
END_STYLE_INCLUDE_MIN_MAX_LABELS = "IncludeMinMaxLabels"
END_STYLE_EXCLUDE_OUTER_BOXES = "ExcludeOuterBoxes"

BOX_END_CAP_RECTANGLE_ENDS = "RectangleEnds"

NCL_LABELBAR_DEFAULTS: dict[str, Any] = {
    "lbLabelBarOn": True,
    "lbOrientation": ORIENTATION_VERTICAL,
    "lbJustification": "BottomLeft",
    "lbBoxMajorExtentF": 1.0,
    "lbBoxMinorExtentF": 0.33,
    "lbBoxCount": 16,
    "lbBoxSizing": "UniformSizing",
    "lbAutoManage": True,
    "lbLabelOffsetF": 0.1,
    "lbTitleOffsetF": 0.03,
    "lbLeftMarginF": 0.05,
    "lbRightMarginF": 0.05,
    "lbBottomMarginF": 0.05,
    "lbTopMarginF": 0.05,
    "lbMonoFillColor": False,
    "lbFillColor": "Foreground",
    "lbFillColors": None,
    "lbMonoFillPattern": False,
    "lbFillPattern": "SolidFill",
    "lbFillPatterns": None,
    "lbMonoFillScale": True,
    "lbFillScaleF": 1.0,
    "lbFillScales": None,
    "lbLabelStrings": None,
    "lbLabelAutoStride": True,
    "lbLabelsOn": True,
    "lbLabelPosition": "Right",
    "lbLabelAngleF": 0.0,
    "lbLabelAlignment": LABEL_ALIGNMENT_BOX_CENTERS,
    "lbLabelDirection": "Across",
    "lbLabelJust": "CenterCenter",
    "lbLabelFontHeightF": 0.02,
    "lbLabelStride": 1,
    "lbBoxLinesOn": True,
    "lbBoxSeparatorLinesOn": True,
    "lbBoxEndCapStyle": BOX_END_CAP_RECTANGLE_ENDS,
    "lbPerimOn": False,
    "lbRasterFillOn": False,
}

GSN_CREATE_LABELBAR_DEFAULTS: dict[str, Any] = {
    "vpXF": 0.1,
    "vpYF": 0.1,
    "vpWidthF": 0.8,
    "vpHeightF": 0.3,
    "lbOrientation": ORIENTATION_HORIZONTAL,
    "lbPerimOn": False,
    "lbLabelFontHeightF": 0.1,
    "lbMonoFillPattern": True,
    "lbAutoManage": False,
}

_ALIGNMENT_ALIASES = {
    "boxcenters": LABEL_ALIGNMENT_BOX_CENTERS,
    "box_centers": LABEL_ALIGNMENT_BOX_CENTERS,
    "nhlboxcenters": LABEL_ALIGNMENT_BOX_CENTERS,
    "interioredges": LABEL_ALIGNMENT_INTERIOR_EDGES,
    "interior_edges": LABEL_ALIGNMENT_INTERIOR_EDGES,
    "nhlinterioredges": LABEL_ALIGNMENT_INTERIOR_EDGES,
    "externaledges": LABEL_ALIGNMENT_EXTERNAL_EDGES,
    "external_edges": LABEL_ALIGNMENT_EXTERNAL_EDGES,
    "nhlexternaledges": LABEL_ALIGNMENT_EXTERNAL_EDGES,
}

_ORIENTATION_ALIASES = {
    "horizontal": ORIENTATION_HORIZONTAL,
    "nhlhorizontal": ORIENTATION_HORIZONTAL,
    "vertical": ORIENTATION_VERTICAL,
    "nhlvertical": ORIENTATION_VERTICAL,
}

_END_STYLE_ALIASES = {
    "includeouterboxes": END_STYLE_INCLUDE_OUTER_BOXES,
    "include_outer_boxes": END_STYLE_INCLUDE_OUTER_BOXES,
    "includeminmaxlabels": END_STYLE_INCLUDE_MIN_MAX_LABELS,
    "include_min_max_labels": END_STYLE_INCLUDE_MIN_MAX_LABELS,
    "excludeouterboxes": END_STYLE_EXCLUDE_OUTER_BOXES,
    "exclude_outer_boxes": END_STYLE_EXCLUDE_OUTER_BOXES,
}


def _norm_key(value: Any) -> str:
    return str(value).strip().replace("-", "_").replace(" ", "_").lower()


def normalize_label_alignment(value: Any | None) -> str:
    if value is None:
        return LABEL_ALIGNMENT_BOX_CENTERS
    key = _norm_key(value)
    if key not in _ALIGNMENT_ALIASES:
        raise ValueError(f"Unsupported lbLabelAlignment: {value!r}")
    return _ALIGNMENT_ALIASES[key]


def normalize_orientation(value: Any | None) -> str:
    if value is None:
        return ORIENTATION_VERTICAL
    key = _norm_key(value)
    if key not in _ORIENTATION_ALIASES:
        raise ValueError(f"Unsupported lbOrientation: {value!r}")
    return _ORIENTATION_ALIASES[key]


def normalize_end_style(value: Any | None) -> str | None:
    if value is None:
        return None
    key = _norm_key(value)
    if key not in _END_STYLE_ALIASES:
        raise ValueError(f"Unsupported labelbar end style: {value!r}")
    return _END_STYLE_ALIASES[key]


def normalize_box_count(value: Any) -> int:
    try:
        count = int(value)
    except Exception as exc:
        raise ValueError(f"Invalid lbBoxCount: {value!r}") from exc
    return max(1, count)


def normalize_label_stride(value: Any | None) -> int:
    if value is None:
        return 1
    try:
        stride = int(value)
    except Exception as exc:
        raise ValueError(f"Invalid lbLabelStride: {value!r}") from exc
    return max(1, stride)


def label_count_for_alignment(box_count: Any, alignment: Any | None) -> int:
    count = normalize_box_count(box_count)
    mode = normalize_label_alignment(alignment)

    if mode == LABEL_ALIGNMENT_BOX_CENTERS:
        return count
    if mode == LABEL_ALIGNMENT_INTERIOR_EDGES:
        return max(0, count - 1)
    return count + 1


def label_indices_for_stride(
    box_count: Any,
    alignment: Any | None,
    stride: Any | None = 1,
) -> tuple[int, ...]:
    count = label_count_for_alignment(box_count, alignment)
    step = normalize_label_stride(stride)
    return tuple(range(0, count, step))


def uniform_label_axis_positions(
    box_count: Any,
    alignment: Any | None,
    stride: Any | None = 1,
) -> tuple[float, ...]:
    count = normalize_box_count(box_count)
    mode = normalize_label_alignment(alignment)
    indices = label_indices_for_stride(count, mode, stride)

    if mode == LABEL_ALIGNMENT_BOX_CENTERS:
        return tuple((idx + 0.5) / count for idx in indices)

    if mode == LABEL_ALIGNMENT_INTERIOR_EDGES:
        return tuple((idx + 1.0) / count for idx in indices)

    return tuple((idx + 0.5) / (count + 1.0) for idx in indices)


def label_alignment_for_end_style(
    end_style: Any | None,
    explicit_alignment: Any | None = None,
) -> str:
    if explicit_alignment is not None:
        return normalize_label_alignment(explicit_alignment)

    style = normalize_end_style(end_style)

    if style is None:
        return LABEL_ALIGNMENT_INTERIOR_EDGES
    if style == END_STYLE_INCLUDE_OUTER_BOXES:
        return LABEL_ALIGNMENT_INTERIOR_EDGES
    return LABEL_ALIGNMENT_EXTERNAL_EDGES
