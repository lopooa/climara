from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from ._labelbar_semantics import (
    END_STYLE_EXCLUDE_OUTER_BOXES,
    END_STYLE_INCLUDE_MIN_MAX_LABELS,
    END_STYLE_INCLUDE_OUTER_BOXES,
    GSN_CREATE_LABELBAR_DEFAULTS,
    LABEL_ALIGNMENT_EXTERNAL_EDGES,
    LABEL_ALIGNMENT_INTERIOR_EDGES,
    NCL_LABELBAR_DEFAULTS,
    NCL_LABELBAR_DEFAULT_TITLE,
    label_alignment_for_end_style,
    label_count_for_alignment,
    label_indices_for_stride,
    normalize_box_count,
    normalize_end_style,
    normalize_label_alignment,
    normalize_label_stride,
    normalize_orientation,
    normalize_title_direction,
    normalize_title_position,
    resolve_title_on,
    uniform_label_axis_positions,
)


def _as_tuple(value: Any | None) -> tuple[Any, ...]:
    if value is None:
        return ()
    if isinstance(value, tuple):
        return value
    if isinstance(value, str):
        return (value,)
    if isinstance(value, Sequence):
        return tuple(value)
    return (value,)


def _as_label_tuple(value: Any | None) -> tuple[str, ...]:
    return tuple(str(item) for item in _as_tuple(value))


def _is_empty_sequence(value: Any | None) -> bool:
    return len(_as_tuple(value)) == 0


def _first_non_empty(*values: Any) -> Any | None:
    for value in values:
        if value is not None and not _is_empty_sequence(value):
            return value
    return None


def _as_resource_dict(value: Mapping[str, Any] | None) -> dict[str, Any]:
    if value is None:
        return {}
    return dict(value)


def _is_resource_mapping(value: Any) -> bool:
    return isinstance(value, Mapping)


def _rect_from_resources(resources: Mapping[str, Any]) -> tuple[float, float, float, float]:
    return (
        float(resources.get("vpXF", 0.1)),
        float(resources.get("vpYF", 0.1)),
        float(resources.get("vpWidthF", 0.8)),
        float(resources.get("vpHeightF", 0.3)),
    )


def _normalize_rect(value: Any | None, resources: Mapping[str, Any]) -> tuple[float, float, float, float]:
    if value is None:
        value = resources.get("rect")

    if value is None:
        return _rect_from_resources(resources)

    items = _as_tuple(value)
    if len(items) != 4:
        raise ValueError(f"LabelBar rect must have four values, got {value!r}")

    return tuple(float(item) for item in items)  # type: ignore[return-value]


def _resource_bool(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() not in {"false", "0", "off", "no"}
    return bool(value)


def _default_label_string(index: int) -> str:
    return f"Label_{index}"


def _label_string_at(labels: tuple[str, ...], index: int) -> str:
    if 0 <= index < len(labels):
        return labels[index]
    return _default_label_string(index)


def _visible_label_strings(labels: tuple[str, ...], indices: tuple[int, ...]) -> tuple[str, ...]:
    return tuple(_label_string_at(labels, index) for index in indices)


def _resolve_gsn_labelbar_resources(
    nbox: int,
    colors: tuple[Any, ...],
    labels: tuple[str, ...],
    user_resources: Mapping[str, Any],
) -> tuple[dict[str, Any], tuple[Any, ...], tuple[str, ...]]:
    resources: dict[str, Any] = {}
    resources.update(NCL_LABELBAR_DEFAULTS)
    resources.update(GSN_CREATE_LABELBAR_DEFAULTS)
    resources.update(user_resources)

    end_style_value = resources.get("EndStyle", resources.get("cnLabelBarEndStyle"))
    end_style = normalize_end_style(end_style_value)

    explicit_alignment = None
    if "lbLabelAlignment" in user_resources:
        explicit_alignment = user_resources["lbLabelAlignment"]

    label_alignment = label_alignment_for_end_style(end_style, explicit_alignment)

    label_values = _first_non_empty(
        resources.get("lbLabelStrings"),
        resources.get("labels"),
        labels,
        resources.get("levels"),
        resources.get("lbLevels"),
    )
    new_labels = _as_label_tuple(label_values)

    color_values = _first_non_empty(
        resources.get("lbFillColors"),
        resources.get("colors"),
        colors,
    )
    base_colors = _as_tuple(color_values)

    subset_stuff = _resource_bool(resources.get("SubsetStuff", False))
    box_count = nbox
    fill_colors = base_colors

    if end_style == END_STYLE_EXCLUDE_OUTER_BOXES:
        if subset_stuff and len(base_colors) >= 2:
            fill_colors = base_colors[1:-1]
            box_count = max(1, nbox - 2)
        else:
            box_count = nbox
            fill_colors = base_colors
    else:
        box_count = nbox
        fill_colors = base_colors

    if not fill_colors:
        fill_colors = _as_tuple(resources.get("lbFillColors"))
   
        fill_colors = base_colors

    if not fill_colors:
        fill_colors = _as_tuple(resources.get("lbFillColors"))
    if not fill_colors:
        box_count = normalize_box_count(resources.get("lbBoxCount", box_count))
    else:
        box_count = normalize_box_count(box_count)

    resources["lbBoxCount"] = box_count
    resources["lbFillColors"] = fill_colors
    resources["lbLabelStrings"] = new_labels
    resources["colors"] = fill_colors
    resources["labels"] = new_labels
    resources["lbLabelAlignment"] = label_alignment
    resources["lbOrientation"] = normalize_orientation(resources.get("lbOrientation"))
    resources["lbLabelStride"] = normalize_label_stride(resources.get("lbLabelStride", 1))

    return resources, fill_colors, new_labels


class HluLabelBar:
    object_type = "labelbar"
    plot_type = "labelbar"

    def __init__(
        self,
        rect: Any | None = None,
        colors: Sequence[Any] | None = None,
        labels: Sequence[Any] | None = None,
        resources: Mapping[str, Any] | None = None,
        *,
        name: str = "labelbar",
        levels: Sequence[Any] | None = None,
        fill_patterns: Sequence[Any] | None = None,
        fill_scales: Sequence[Any] | None = None,
        **extra_resources: Any,
    ) -> None:
        user_resources = _as_resource_dict(resources)
        user_resources.update(extra_resources)

        merged_resources: dict[str, Any] = {}
        merged_resources.update(NCL_LABELBAR_DEFAULTS)
        merged_resources.update(user_resources)

        self.name = name
        self.resources = merged_resources
        self.rect = _normalize_rect(rect, merged_resources)

        self.colors = _as_tuple(colors if colors is not None else merged_resources.get("lbFillColors"))
        self.fill_colors = self.colors
        self.labels = _as_label_tuple(labels if labels is not None else merged_resources.get("lbLabelStrings"))
        self.label_strings = self.labels
        self.levels = _as_tuple(levels)

        self.fill_patterns = _as_tuple(
            fill_patterns if fill_patterns is not None else merged_resources.get("lbFillPatterns")
        )
        self.fill_scales = _as_tuple(
            fill_scales if fill_scales is not None else merged_resources.get("lbFillScales")
        )

        self.orientation = normalize_orientation(merged_resources.get("lbOrientation"))
        self.label_alignment = normalize_label_alignment(merged_resources.get("lbLabelAlignment"))
        self.box_count = normalize_box_count(merged_resources.get("lbBoxCount", len(self.colors) or 16))
        self.label_stride = normalize_label_stride(merged_resources.get("lbLabelStride", 1))
        self.label_count = label_count_for_alignment(self.box_count, self.label_alignment)
        self.label_indices = label_indices_for_stride(
            self.box_count,
            self.label_alignment,
            self.label_stride,
        )
        self.label_draw_count = len(self.label_indices)
        self.visible_label_strings = _visible_label_strings(self.label_strings, self.label_indices)
        self.label_axis_positions = uniform_label_axis_positions(
            self.box_count,
            self.label_alignment,
            self.label_stride,
        )

        self.box_end_cap_style = str(merged_resources.get("lbBoxEndCapStyle", "RectangleEnds"))
        self.auto_manage = _resource_bool(merged_resources.get("lbAutoManage", True))
        self.perim_on = _resource_bool(merged_resources.get("lbPerimOn", False))
        self.labels_on = _resource_bool(merged_resources.get("lbLabelsOn", True))

        title_string = merged_resources.get("lbTitleString", NCL_LABELBAR_DEFAULT_TITLE)
        if title_string is None:
            title_string = NCL_LABELBAR_DEFAULT_TITLE

        self.title_string = str(title_string)
        self.title_on = resolve_title_on(merged_resources.get("lbTitleOn"), self.title_string)
        self.title_position = normalize_title_position(merged_resources.get("lbTitlePosition"))
        self.title_direction = normalize_title_direction(
            merged_resources.get("lbTitleDirection"),
            self.title_position,
        )
        self.title_extent = float(merged_resources.get("lbTitleExtentF", 0.15))
        self.title_offset = float(merged_resources.get("lbTitleOffsetF", 0.03))
        self.title_angle = float(merged_resources.get("lbTitleAngleF", 0.0))

        self.label_font_height = float(merged_resources.get("lbLabelFontHeightF", 0.02))
        self.label_offset = float(merged_resources.get("lbLabelOffsetF", 0.1))
        self.box_minor_extent = float(merged_resources.get("lbBoxMinorExtentF", 0.33))

        self.resources["rect"] = self.rect
        self.resources["vpXF"] = self.rect[0]
        self.resources["vpYF"] = self.rect[1]
        self.resources["vpWidthF"] = self.rect[2]
        self.resources["vpHeightF"] = self.rect[3]
        self.resources["lbFillColors"] = self.fill_colors
        self.resources["lbLabelStrings"] = self.label_strings
        self.resources["lbOrientation"] = self.orientation
        self.resources["lbLabelAlignment"] = self.label_alignment
        self.resources["lbBoxCount"] = self.box_count
        self.resources["lbLabelStride"] = self.label_stride
        self.resources["lbTitleString"] = self.title_string
        self.resources["lbTitleOn"] = self.title_on
        self.resources["lbTitlePosition"] = self.title_position
        self.resources["lbTitleDirection"] = self.title_direction
        self.resources["lbTitleExtentF"] = self.title_extent
        self.resources["lbTitleOffsetF"] = self.title_offset
        self.resources["lbTitleAngleF"] = self.title_angle

    @property
    def x(self) -> float:
        return self.rect[0]

    @property
    def y(self) -> float:
        return self.rect[1]

    @property
    def width(self) -> float:
        return self.rect[2]

    @property
    def height(self) -> float:
        return self.rect[3]

    @property
    def vpXF(self) -> float:
        return self.rect[0]

    @property
    def vpYF(self) -> float:
        return self.rect[1]

    @property
    def vpWidthF(self) -> float:
        return self.rect[2]

    @property
    def vpHeightF(self) -> float:
        return self.rect[3]

    def get(self, key: str, default: Any = None) -> Any:
        return self.resources.get(key, default)

    def to_resource_dict(self) -> dict[str, Any]:
        return dict(self.resources)

    def compute_geometry(self):
        from ._labelbar_geometry import compute_labelbar_geometry

        return compute_labelbar_geometry(self)

    def build_plotchar_metrics_bundle(
        self,
        *,
        title: Any | None = None,
        labels: Any = (),
    ):
        from ._labelbar_plotchar_metrics_bundle import (
            build_labelbar_plotchar_metrics_bundle,
        )

        return build_labelbar_plotchar_metrics_bundle(
            title=title,
            labels=labels,
        )

    def build_uniform_plotchar_metrics_bundle(
        self,
        *,
        title: Any | None = None,
        label: Any,
    ):
        from ._labelbar_plotchar_metrics_bundle import (
            build_uniform_labelbar_plotchar_metrics_bundle,
        )

        return build_uniform_labelbar_plotchar_metrics_bundle(
            self,
            title=title,
            label=label,
        )

    def validate_plotchar_metrics_bundle(self, bundle: Any):
        from ._labelbar_plotchar_metrics_bundle import (
            validate_labelbar_plotchar_metrics_bundle,
        )

        return validate_labelbar_plotchar_metrics_bundle(self, bundle)

    def build_adjust_pipeline_from_plotchar_metrics_bundle(
        self,
        bundle: Any,
        *,
        perim_on: bool = False,
        background_fill_on: bool = False,
        perim_space: float = 0.0,
    ):
        from ._labelbar_plotchar_metrics_bundle import (
            build_labelbar_adjust_pipeline_from_plotchar_metrics_bundle,
        )

        return build_labelbar_adjust_pipeline_from_plotchar_metrics_bundle(
            self,
            bundle,
            perim_on=perim_on,
            background_fill_on=background_fill_on,
            perim_space=perim_space,
        )

    def compute_adjusted_geometry_from_plotchar_metrics_bundle(
        self,
        bundle: Any,
        *,
        perim_on: bool = False,
        background_fill_on: bool = False,
        perim_space: float = 0.0,
    ):
        from ._labelbar_plotchar_metrics_bundle import (
            compute_labelbar_adjusted_geometry_from_plotchar_metrics_bundle,
        )

        return compute_labelbar_adjusted_geometry_from_plotchar_metrics_bundle(
            self,
            bundle,
            perim_on=perim_on,
            background_fill_on=background_fill_on,
            perim_space=perim_space,
        )

    def render_adjusted_svg_from_plotchar_metrics_bundle(
        self,
        bundle: Any,
        *,
        width: int = 1000,
        height: int = 800,
        background: str | None = "white",
        stroke: Any = "black",
        text_fill: Any | None = None,
        default_label_font_height: float = 0.012,
    ) -> str:
        from ._labelbar_plotchar_metrics_bundle import (
            render_adjusted_labelbar_svg_from_plotchar_metrics_bundle,
        )

        return render_adjusted_labelbar_svg_from_plotchar_metrics_bundle(
            self,
            bundle,
            width=width,
            height=height,
            background=background,
            stroke=stroke,
            text_fill=text_fill,
            default_label_font_height=default_label_font_height,
        )

    def build_plotchar_metrics_bundle_from_provider(self, provider: Any):
        from ._labelbar_plotchar_metrics_provider import (
            build_labelbar_plotchar_metrics_bundle_from_provider,
        )

        return build_labelbar_plotchar_metrics_bundle_from_provider(
            self,
            provider,
        )

    def build_adjust_pipeline_from_plotchar_metrics_provider(
        self,
        provider: Any,
        *,
        perim_on: bool = False,
        background_fill_on: bool = False,
        perim_space: float = 0.0,
    ):
        from ._labelbar_plotchar_metrics_provider import (
            build_labelbar_adjust_pipeline_from_plotchar_metrics_provider,
        )

        return build_labelbar_adjust_pipeline_from_plotchar_metrics_provider(
            self,
            provider,
            perim_on=perim_on,
            background_fill_on=background_fill_on,
            perim_space=perim_space,
        )

    def compute_adjusted_geometry_from_plotchar_metrics_provider(
        self,
        provider: Any,
        *,
        perim_on: bool = False,
        background_fill_on: bool = False,
        perim_space: float = 0.0,
    ):
        from ._labelbar_plotchar_metrics_provider import (
            compute_labelbar_adjusted_geometry_from_plotchar_metrics_provider,
        )

        return compute_labelbar_adjusted_geometry_from_plotchar_metrics_provider(
            self,
            provider,
            perim_on=perim_on,
            background_fill_on=background_fill_on,
            perim_space=perim_space,
        )

    def render_adjusted_svg_from_plotchar_metrics_provider(
        self,
        provider: Any,
        *,
        width: int = 1000,
        height: int = 800,
        background: str | None = "white",
        stroke: Any = "black",
        text_fill: Any | None = None,
        default_label_font_height: float = 0.012,
    ) -> str:
        from ._labelbar_plotchar_metrics_provider import (
            render_adjusted_labelbar_svg_from_plotchar_metrics_provider,
        )

        return render_adjusted_labelbar_svg_from_plotchar_metrics_provider(
            self,
            provider,
            width=width,
            height=height,
            background=background,
            stroke=stroke,
            text_fill=text_fill,
            default_label_font_height=default_label_font_height,
        )


    def save_adjusted_svg_from_plotchar_metrics_bundle(
        self,
        bundle: Any,
        path: Any,
        *,
        width: int = 1000,
        height: int = 800,
        background: str | None = "white",
        stroke: Any = "black",
        text_fill: Any | None = None,
        default_label_font_height: float = 0.012,
    ):
        from ._labelbar_plotchar_metrics_bundle import (
            save_adjusted_labelbar_svg_from_plotchar_metrics_bundle,
        )

        return save_adjusted_labelbar_svg_from_plotchar_metrics_bundle(
            self,
            bundle,
            path,
            width=width,
            height=height,
            background=background,
            stroke=stroke,
            text_fill=text_fill,
            default_label_font_height=default_label_font_height,
        )


def build_hlu_labelbar(
    *args: Any,
    resources: Mapping[str, Any] | None = None,
    rect: Any | None = None,
    colors: Sequence[Any] | None = None,
    labels: Sequence[Any] | None = None,
    levels: Sequence[Any] | None = None,
    fill_patterns: Sequence[Any] | None = None,
    fill_scales: Sequence[Any] | None = None,
    name: str = "labelbar",
    **extra_resources: Any,
) -> HluLabelBar:
    if args:
        if len(args) == 1 and _is_resource_mapping(args[0]) and resources is None and rect is None:
            resources = args[0]
        else:
            if len(args) >= 1 and rect is None:
                rect = args[0]
            if len(args) >= 2 and colors is None:
                colors = args[1]
            if len(args) >= 3 and labels is None:
                labels = args[2]
            if len(args) >= 4 and resources is None:
                resources = args[3]
            if len(args) > 4:
                raise TypeError("build_hlu_labelbar accepts at most four positional arguments")

    user_resources = _as_resource_dict(resources)
    user_resources.update(extra_resources)

    base_color_values = _first_non_empty(
        colors,
        user_resources.get("lbFillColors"),
        user_resources.get("colors"),
    )
    base_label_values = _first_non_empty(
        labels,
        user_resources.get("lbLabelStrings"),
        user_resources.get("labels"),
        user_resources.get("levels"),
        user_resources.get("lbLevels"),
    )

    base_colors = _as_tuple(base_color_values)
    base_labels = _as_label_tuple(base_label_values)

    nbox = len(base_colors)
    if nbox <= 0:
        nbox = normalize_box_count(user_resources.get("lbBoxCount", NCL_LABELBAR_DEFAULTS["lbBoxCount"]))

    resolved_resources, fill_colors, label_strings = _resolve_gsn_labelbar_resources(
        nbox,
        base_colors,
        base_labels,
        user_resources,
    )

    resolved_rect = _normalize_rect(rect, resolved_resources)

    return HluLabelBar(
        rect=resolved_rect,
        colors=fill_colors,
        labels=label_strings,
        resources=resolved_resources,
        name=name,
        levels=levels,
        fill_patterns=fill_patterns,
        fill_scales=fill_scales,
    )


def _merge_labelbar_resources(
    resources: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Merge LabelBar resource dictionaries for legacy compatibility."""

    merged = _as_resource_dict(resources)
    merged.update(kwargs)
    return merged


def create_hlu_labelbar(*args: Any, **kwargs: Any) -> HluLabelBar:
    """Compatibility alias for build_hlu_labelbar."""

    return build_hlu_labelbar(*args, **kwargs)


__all__ = [
    "HluLabelBar",
    "_merge_labelbar_resources",
    "build_hlu_labelbar",
    "create_hlu_labelbar",
]
