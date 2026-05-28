from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ._ncl_plotchar_textitem import build_ncl_plotchar_textitem_state
from ._plotchar_fontcap import PlotcharRdguGlyph, glyphs_to_rdgu, load_fontcap
from ._plotchar_function_code import parse_textitem_plotchar_real_string
from ._plotchar_metrics import PlotcharExtentMetrics
from ._plotchar_plchhq_extent import compute_plchhq_fontcap_text_extent
from ._plotchar_state import PlotcharUnsupportedError, build_textitem_plotchar_state
from ._text_semantics import build_text_item_semantics, normalize_text_just


@dataclass(frozen=True)
class PlotcharNdcPolyline:
    points: tuple[tuple[float, float], ...]


@dataclass(frozen=True)
class PlotcharSvgRenderResult:
    polylines: tuple[PlotcharNdcPolyline, ...]
    metrics: PlotcharExtentMetrics
    text: str
    font_number: int


def _split_just(just: str) -> tuple[str, str]:
    value = normalize_text_just(just)

    if value.endswith("Left"):
        horizontal = "left"
    elif value.endswith("Right"):
        horizontal = "right"
    else:
        horizontal = "center"

    if value.startswith("Bottom"):
        vertical = "bottom"
    elif value.startswith("Top"):
        vertical = "top"
    else:
        vertical = "center"

    return horizontal, vertical


def _start_origin_from_just(
    x: float,
    y: float,
    metrics: PlotcharExtentMetrics,
    just: str,
) -> tuple[float, float]:
    horizontal, vertical = _split_just(just)

    if horizontal == "left":
        x0 = float(x) + float(metrics.dl)
    elif horizontal == "right":
        x0 = float(x) - float(metrics.dr)
    else:
        x0 = float(x) + 0.5 * (float(metrics.dl) - float(metrics.dr))

    if vertical == "bottom":
        y0 = float(y) + float(metrics.db)
    elif vertical == "top":
        y0 = float(y) - float(metrics.dt)
    else:
        y0 = float(y) + 0.5 * (float(metrics.db) - float(metrics.dt))

    return x0, y0


def _segments_from_rdgu_glyph(
    glyph: PlotcharRdguGlyph,
) -> tuple[tuple[tuple[float, float], ...], ...]:
    segments: list[tuple[tuple[float, float], ...]] = []
    current: list[tuple[float, float]] = []

    for x, y in glyph.points:
        if x <= -2047.0 or y <= -2047.0:
            if len(current) >= 2:
                segments.append(tuple(current))
            current = []
            continue

        current.append((float(x), float(y)))

    if len(current) >= 2:
        segments.append(tuple(current))

    return tuple(segments)


def _plotchar_sizm(size: float, state) -> float:
    size = float(size)

    if size <= 0.0 or size >= 1.0:
        raise PlotcharUnsupportedError(
            "Current Plotchar SVG runtime stage only supports fractional TextItem SIZE "
            "with 0 < SIZE < 1. Address-unit SIZE remains guarded/source-mapped separately."
        )

    if float(state.wpic[0]) == 0.0:
        raise PlotcharUnsupportedError(
            "WPIC(1) is zero; cannot reproduce PLCHHQ SIZM semantics."
        )

    sizm = size / float(state.wpic[0])

    if int(state.iquf) == 0:
        sizm = float(state.siza) * sizm

    return sizm


def _spacing_for_glyph(state, glyph: PlotcharRdguGlyph, ipic: int) -> tuple[float, float]:
    xmzm = float(state.zinx) * float(state.zinz) * float(state.xmul[ipic - 1])

    if float(state.cons) == 0.0:
        return -xmzm * float(glyph.rdgu_left), xmzm * float(glyph.rdgu_right)

    if float(state.cons) < 0.0:
        return -float(state.cons), -float(state.cons)

    return (
        float(state.cons) * float(state.wpic[ipic - 1]),
        float(state.cons) * float(state.wpic[ipic - 1]),
    )


def _event_zoom(value: int) -> float:
    if int(value) <= 0:
        raise PlotcharUnsupportedError(
            "Plotchar SVG runtime refuses non-positive zoom values."
        )

    return float(value) / 100.0


def _event_move_units(value: int, *, sizm: float) -> float:
    return float(value) * float(sizm)


@dataclass
class _RuntimeCursor:
    x0: float
    y0: float
    x: float
    y: float
    ipic: int = 1
    script_shift: float = 0.0
    manual_x_shift: float = 0.0
    manual_y_shift: float = 0.0
    zinx: float = 1.0
    ziny: float = 1.0
    zinz: float = 1.0
    line_index: int = 0


def _glyph_scale_factors(state, cursor: _RuntimeCursor) -> tuple[float, float]:
    ipic = cursor.ipic

    xmzm = (
        float(cursor.zinx)
        * float(cursor.zinz)
        * float(state.xmul[ipic - 1])
    )
    ymzm = (
        float(cursor.ziny)
        * float(cursor.zinz)
        * float(state.ymul[ipic - 1])
    )

    return xmzm, ymzm


def _draw_text_event(
    *,
    event,
    state,
    cursor: _RuntimeCursor,
    size: float,
    fontcap_dir: str | Path | None,
) -> tuple[PlotcharNdcPolyline, ...]:
    if not event.text:
        return ()

    if any(ord(char) < 32 or ord(char) > 126 for char in event.text):
        raise PlotcharUnsupportedError(
            "Plotchar SVG runtime currently supports printable ASCII fontcap glyphs only."
        )

    fontcap = load_fontcap(int(event.font_number), fontcap_dir)
    glyphs = [fontcap.glyph_for_ascii(ord(char)) for char in event.text]
    rdgu_glyphs = glyphs_to_rdgu(
        glyphs,
        fontcap.metrics,
        chgt=float(state.hpic[cursor.ipic - 1]),
    )

    sizm = _plotchar_sizm(size, state)
    xmzm, ymzm = _glyph_scale_factors(state, cursor)

    out: list[PlotcharNdcPolyline] = []

    for char, glyph in zip(event.text, rdgu_glyphs):
        dtle, dtre = _spacing_for_glyph(state, glyph, cursor.ipic)

        center_x = cursor.x + dtle * sizm
        center_y = cursor.y

        if char != " ":
            for segment in _segments_from_rdgu_glyph(glyph):
                points: list[tuple[float, float]] = []

                for gx, gy in segment:
                    px = (
                        center_x
                        + cursor.manual_x_shift
                        + sizm * xmzm * float(gx)
                    )
                    py = (
                        center_y
                        + cursor.manual_y_shift
                        + cursor.script_shift
                        + sizm * ymzm * float(gy)
                    )
                    points.append((px, py))

                if len(points) >= 2:
                    out.append(PlotcharNdcPolyline(points=tuple(points)))

        cursor.x = center_x + dtre * sizm

    return tuple(out)


def _apply_event_state(event, *, state, cursor: _RuntimeCursor, size: float) -> None:
    kind = str(event.kind)

    sizm = _plotchar_sizm(size, state)

    if kind == "subscript":
        cursor.ipic = 2
        cursor.script_shift = -float(state.ssic) * sizm
        return

    if kind == "superscript":
        cursor.ipic = 2
        cursor.script_shift = float(state.sspr) * sizm
        return

    if kind in {"normal_script", "principal"}:
        cursor.ipic = 1
        cursor.script_shift = 0.0
        return

    if kind in {"indexical", "index"}:
        cursor.ipic = 2
        return

    if kind in {"cartographic", "carto"}:
        cursor.ipic = 3
        return

    if kind == "hmove":
        cursor.manual_x_shift += _event_move_units(int(event.value), sizm=sizm)
        return

    if kind == "vmove":
        cursor.manual_y_shift += _event_move_units(int(event.value), sizm=sizm)
        return

    if kind == "xzoom":
        cursor.zinx = _event_zoom(int(event.value))
        return

    if kind == "yzoom":
        cursor.ziny = _event_zoom(int(event.value))
        return

    if kind == "zzoom":
        cursor.zinz = _event_zoom(int(event.value))
        return

    if kind in {"carriage_return", "carriage", "newline"}:
        cursor.line_index += 1
        cursor.x = cursor.x0
        cursor.y = cursor.y0 - float(cursor.line_index) * float(state.vpic[0]) * sizm
        cursor.manual_x_shift = 0.0
        cursor.manual_y_shift = 0.0
        cursor.script_shift = 0.0
        cursor.ipic = 1
        return

    raise PlotcharUnsupportedError(
        f"Plotchar SVG runtime does not yet implement parsed event kind {kind!r}. "
        "This event remains guarded until its exact draw semantics are mapped."
    )


def _render_events_to_ndc_polylines(
    events,
    *,
    state,
    xpos: float,
    ypos: float,
    size: float,
    fontcap_dir: str | Path | None,
) -> tuple[PlotcharNdcPolyline, ...]:
    cursor = _RuntimeCursor(
        x0=float(xpos),
        y0=float(ypos),
        x=float(xpos),
        y=float(ypos),
    )

    out: list[PlotcharNdcPolyline] = []

    for event in events:
        kind = str(event.kind)

        if kind == "text":
            out.extend(
                _draw_text_event(
                    event=event,
                    state=state,
                    cursor=cursor,
                    size=size,
                    fontcap_dir=fontcap_dir,
                )
            )
        else:
            _apply_event_state(
                event,
                state=state,
                cursor=cursor,
                size=size,
            )

    return tuple(out)


def render_text_semantics_to_ndc_polylines(
    *,
    text: str,
    x: float,
    y: float,
    just: str = "CenterCenter",
    direction: Any | None = "Across",
    func_code: Any | None = "~",
    angle: Any | None = 0.0,
    font: Any = 21,
    font_color: Any = "black",
    font_height: Any = 0.025,
    font_aspect: Any = 1.3125,
    font_thickness: Any = 1.0,
    font_quality: Any = "High",
    constant_spacing: Any = 0.0,
    fontcap_dir: str | Path | None = None,
) -> PlotcharSvgRenderResult:
    semantics = build_text_item_semantics(
        text=text,
        direction=direction,
        func_code=func_code,
        just=just,
        angle=angle,
        font=font,
        font_color=font_color,
        font_height=font_height,
        font_aspect=font_aspect,
        font_thickness=font_thickness,
        font_quality=font_quality,
        constant_spacing=constant_spacing,
    )

    if semantics.direction != "Across":
        raise PlotcharUnsupportedError(
            "Down-text remains guarded until PLCHHQ NDWN/LCWD drawing semantics are fully mapped."
        )

    if not (
        math.isclose(float(semantics.angle), 0.0, abs_tol=1e-12)
        or math.isclose(float(semantics.angle), 360.0, abs_tol=1e-12)
    ):
        raise PlotcharUnsupportedError(
            "Current Plotchar SVG runtime supports Across text with angle 0/360 only."
        )

    textitem_state = build_ncl_plotchar_textitem_state(semantics)
    plotchar_state = build_textitem_plotchar_state(textitem_state)

    validated = compute_plchhq_fontcap_text_extent(
        chrs=semantics.real_string,
        state=plotchar_state,
        xpos=0.5,
        ypos=0.5,
        size=textitem_state.real_size,
        angle=360.0,
        cntr=-1.0,
        fontcap_dir=fontcap_dir,
    )

    parsed = parse_textitem_plotchar_real_string(
        semantics.real_string,
        func_code=semantics.func_code,
        default_font_number=int(plotchar_state.nodf),
    )

    x0, y0 = _start_origin_from_just(
        float(x),
        float(y),
        validated.metrics,
        semantics.just,
    )

    polylines = _render_events_to_ndc_polylines(
        parsed.events,
        state=plotchar_state,
        xpos=x0,
        ypos=y0,
        size=textitem_state.real_size,
        fontcap_dir=fontcap_dir,
    )

    return PlotcharSvgRenderResult(
        polylines=polylines,
        metrics=validated.metrics,
        text=validated.text,
        font_number=int(plotchar_state.nodf),
    )


def render_text_object_to_ndc_polylines(
    obj,
    *,
    viewport: tuple[float, float, float, float] = (0.0, 0.0, 1.0, 1.0),
    fontcap_dir: str | Path | None = None,
) -> PlotcharSvgRenderResult:
    text = str(getattr(obj, "text", getattr(obj, "string", "")))
    x = float(getattr(obj, "x", 0.5))
    y = float(getattr(obj, "y", 0.5))
    resources = getattr(obj, "resources", {}) or {}

    left, bottom, width, height = viewport
    gx = left + x * width
    gy = bottom + y * height

    return render_text_semantics_to_ndc_polylines(
        text=text,
        x=gx,
        y=gy,
        just=resources.get("txJust", resources.get("justify", "CenterCenter")),
        direction=resources.get("txDirection", resources.get("direction", "Across")),
        func_code=resources.get("txFuncCode", "~"),
        angle=resources.get("txAngleF", resources.get("angle", 0.0)),
        font=resources.get("txFont", resources.get("font", 21)),
        font_color=resources.get("txFontColor", resources.get("font_color", "black")),
        font_height=resources.get("txFontHeightF", resources.get("font_size", 0.025)),
        font_aspect=resources.get("txFontAspectF", resources.get("font_aspect", 1.3125)),
        font_thickness=resources.get("txFontThicknessF", resources.get("font_thickness", 1.0)),
        font_quality=resources.get("txFontQuality", resources.get("font_quality", "High")),
        constant_spacing=resources.get(
            "txConstantSpacingF",
            resources.get("constant_spacing", 0.0),
        ),
        fontcap_dir=fontcap_dir,
    )


__all__ = [
    "PlotcharNdcPolyline",
    "PlotcharSvgRenderResult",
    "render_text_object_to_ndc_polylines",
    "render_text_semantics_to_ndc_polylines",
]
