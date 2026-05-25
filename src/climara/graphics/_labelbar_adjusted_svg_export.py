from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any

from ._labelbar_svg_adapter import (
    SvgLabelBarPrimitives,
    labelbar_to_adjusted_svg_primitives_from_supplied_plotchar_metrics,
)
from ._render_svg import SvgDocument
from ._text_semantics import text_uses_func_code


def _color(value: Any, default: str = "black") -> str:
    if value is None:
        return default

    if isinstance(value, str):
        return value

    if isinstance(value, (tuple, list)):
        items = list(value)[:3]
        if not items:
            return default

        vals = []
        for item in items:
            vals.append(float(item))

        if max(abs(item) for item in vals) <= 1.0:
            vals = [item * 255.0 for item in vals]

        vals = [min(255, max(0, round(item))) for item in vals]
        return "#{:02x}{:02x}{:02x}".format(vals[0], vals[1], vals[2])

    return str(value)


def _text_anchor(just: Any) -> str:
    key = str(just or "CenterCenter").strip().lower()

    if "left" in key:
        return "start"
    if "right" in key:
        return "end"
    return "middle"


def _text_font_size(text_item: Any, doc: SvgDocument, default_font_height: float) -> float:
    font_height = getattr(text_item, "font_height", None)

    if font_height is None:
        font_height = default_font_height

    return max(1.0, float(font_height) * float(doc.height))


def _text_transform(text_item: Any) -> str:
    angle = float(getattr(text_item, "angle", 0.0) or 0.0)

    if abs(angle) <= 1e-12:
        return ""

    return (
        f' transform="rotate({angle:.3f} '
        f'{float(text_item.x):.3f} {float(text_item.y):.3f})"'
    )


def _text_data_attrs(text_item: Any) -> str:
    pairs = (
        ("data-ncl-direction", "direction"),
        ("data-ncl-real-string", "real_string"),
        ("data-ncl-func-code", "func_code"),
        ("data-ncl-just", "just"),
        ("data-ncl-font", "font"),
        ("data-ncl-font-height", "font_height"),
        ("data-ncl-font-aspect", "font_aspect"),
        ("data-ncl-font-thickness", "font_thickness"),
        ("data-ncl-font-quality", "font_quality"),
        ("data-ncl-quality-index", "quality_index"),
        ("data-ncl-constant-spacing", "constant_spacing"),
    )

    attrs = []
    for svg_name, field_name in pairs:
        value = getattr(text_item, field_name, None)
        if value is None:
            continue
        attrs.append(f' {svg_name}="{escape(str(value), quote=True)}"')

    return "".join(attrs)


def _render_text_primitive(
    doc: SvgDocument,
    text_item: Any,
    *,
    default_font_height: float,
) -> None:
    direction = getattr(text_item, "direction", None)

    if direction not in (None, "Across"):
        raise NotImplementedError(
            f"NCL TextItem direction {direction!r} is not implemented in the explicit "
            "adjusted LabelBar SVG export path."
        )

    if text_uses_func_code(
        getattr(text_item, "text", ""),
        getattr(text_item, "func_code", None),
    ):
        raise NotImplementedError(
            "NCL Plotchar function-code sequences are not implemented in the explicit "
            "adjusted LabelBar SVG export path."
        )

    font_size = _text_font_size(
        text_item,
        doc,
        default_font_height=default_font_height,
    )

    doc.add(
        f'<text x="{float(text_item.x):.3f}" y="{float(text_item.y):.3f}" '
        f'font-size="{font_size:.3f}" '
        f'fill="{escape(_color(text_item.fill))}" '
        f'text-anchor="{_text_anchor(getattr(text_item, "just", None))}"'
        f'{_text_data_attrs(text_item)}'
        f'{_text_transform(text_item)}>'
        f'{escape(str(text_item.text))}</text>'
    )


def add_adjusted_labelbar_primitives_to_svg_document(
    primitives: SvgLabelBarPrimitives,
    doc: SvgDocument,
    *,
    default_label_font_height: float = 0.012,
) -> SvgDocument:
    doc.add('<g data-climara-labelbar-adjusted="supplied-plotchar-metrics">')

    for polygon in primitives.polygons:
        points = " ".join(
            f"{point.x:.3f},{point.y:.3f}"
            for point in polygon.points
        )
        doc.add(
            f'<polygon points="{escape(points)}" '
            f'fill="{escape(_color(polygon.fill, "none"))}" '
            f'stroke="{escape(_color(polygon.stroke, "none"))}" '
            f'stroke-width="{float(polygon.stroke_width):.3f}" />'
        )

    for title_item in getattr(primitives, "title_texts", ()):
        _render_text_primitive(
            doc,
            title_item,
            default_font_height=default_label_font_height,
        )

    for text_item in primitives.texts:
        _render_text_primitive(
            doc,
            text_item,
            default_font_height=default_label_font_height,
        )

    for line in primitives.lines:
        doc.add(
            f'<line x1="{line.p1.x:.3f}" y1="{line.p1.y:.3f}" '
            f'x2="{line.p2.x:.3f}" y2="{line.p2.y:.3f}" '
            f'stroke="{escape(_color(line.stroke))}" '
            f'stroke-width="{float(line.stroke_width):.3f}" />'
        )

    doc.add("</g>")

    return doc


def render_adjusted_labelbar_svg_from_supplied_plotchar_metrics(
    obj: Any,
    *,
    title_metrics: Any | None = None,
    label_metrics: Any = (),
    width: int = 1000,
    height: int = 800,
    background: str | None = "white",
    stroke: Any = "black",
    text_fill: Any | None = None,
    default_label_font_height: float = 0.012,
) -> str:
    doc = SvgDocument(
        width=int(width),
        height=int(height),
        background=background,
    )

    primitives = labelbar_to_adjusted_svg_primitives_from_supplied_plotchar_metrics(
        obj,
        width,
        height,
        title_metrics=title_metrics,
        label_metrics=label_metrics,
        stroke=stroke,
        text_fill=text_fill,
    )

    add_adjusted_labelbar_primitives_to_svg_document(
        primitives,
        doc,
        default_label_font_height=default_label_font_height,
    )

    return doc.tostring()


def save_adjusted_labelbar_svg_from_supplied_plotchar_metrics(
    obj: Any,
    path: str | Path,
    *,
    title_metrics: Any | None = None,
    label_metrics: Any = (),
    width: int = 1000,
    height: int = 800,
    background: str | None = "white",
    stroke: Any = "black",
    text_fill: Any | None = None,
    default_label_font_height: float = 0.012,
) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)

    svg = render_adjusted_labelbar_svg_from_supplied_plotchar_metrics(
        obj,
        title_metrics=title_metrics,
        label_metrics=label_metrics,
        width=width,
        height=height,
        background=background,
        stroke=stroke,
        text_fill=text_fill,
        default_label_font_height=default_label_font_height,
    )

    output.write_text(svg, encoding="utf-8")
    return output


__all__ = [
    "add_adjusted_labelbar_primitives_to_svg_document",
    "render_adjusted_labelbar_svg_from_supplied_plotchar_metrics",
    "save_adjusted_labelbar_svg_from_supplied_plotchar_metrics",
]
