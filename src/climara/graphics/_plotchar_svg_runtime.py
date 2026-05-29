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
    fillable: bool = False


@dataclass(frozen=True)
class PlotcharSvgRenderResult:
    polylines: tuple[PlotcharNdcPolyline, ...]
    metrics: PlotcharExtentMetrics
    text: str
    font_number: int
    glyph_count: int = 0



def _translate_plotchar_svg_result(
    result: PlotcharSvgRenderResult,
    *,
    dx: float,
    dy: float,
) -> PlotcharSvgRenderResult:
    shifted = tuple(
        PlotcharNdcPolyline(
            points=tuple((x + dx, y + dy) for x, y in poly.points),
            fillable=poly.fillable,
        )
        for poly in result.polylines
    )

    return PlotcharSvgRenderResult(
        polylines=shifted,
        metrics=result.metrics,
        text=result.text,
        font_number=result.font_number,
        glyph_count=result.glyph_count,
    )


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


def _anchor_offset_from_just(
    metrics: PlotcharExtentMetrics,
    just: str,
) -> tuple[float, float]:
    horizontal, vertical = _split_just(just)

    if horizontal == "left":
        u = -float(metrics.dl)
    elif horizontal == "right":
        u = +float(metrics.dr)
    else:
        u = 0.5 * (float(metrics.dr) - float(metrics.dl))

    if vertical == "bottom":
        v = -float(metrics.db)
    elif vertical == "top":
        v = +float(metrics.dt)
    else:
        v = 0.5 * (float(metrics.dt) - float(metrics.db))

    return u, v


def _start_origin_from_just(
    x: float,
    y: float,
    metrics: PlotcharExtentMetrics,
    just: str,
    *,
    angle_deg: float = 0.0,
) -> tuple[float, float]:
    u, v = _anchor_offset_from_just(metrics, just)

    angle = float(angle_deg)
    if math.isclose(angle, 360.0, abs_tol=1e-12):
        angle = 0.0

    radians = math.radians(angle)
    coso = math.cos(radians)
    sino = math.sin(radians)

    return (
        float(x) - (u * coso - v * sino),
        float(y) - (u * sino + v * coso),
    )


def _pieces_from_rdgu_glyph(
    glyph: PlotcharRdguGlyph,
) -> tuple[tuple[tuple[tuple[float, float], ...], bool], ...]:
    pieces: list[tuple[tuple[tuple[float, float], ...], bool]] = []
    current: list[tuple[float, float]] = []

    def flush(*, fillable: bool) -> None:
        nonlocal current

        if len(current) >= 2:
            if fillable and len(current) >= 3:
                if current[0] != current[-1]:
                    current.append(current[0])
                pieces.append((tuple(current), True))
            else:
                pieces.append((tuple(current), False))

        current = []

    for x, y in glyph.points:
        x = float(x)
        y = float(y)

        if x == -2048.0:
            # NCL PLCHHQ draw branch: RDGU(K) == -2048 triggers GPL
            # for the accumulated XCRA/YCRA polyline.
            flush(fillable=False)
            continue

        if x == -2047.0:
            # NCL mapped pre-processing explicitly closes fill areas around
            # RDGU == -2047. Treat this as a fill-area candidate, not as a
            # generic stroke segment.
            flush(fillable=True)
            continue

        if x <= -2047.0 or y <= -2047.0:
            flush(fillable=False)
            continue

        current.append((x, y))

    flush(fillable=False)
    return tuple(pieces)


def _segments_from_rdgu_glyph(
    glyph: PlotcharRdguGlyph,
) -> tuple[tuple[tuple[float, float], ...], ...]:
    return tuple(points for points, _ in _pieces_from_rdgu_glyph(glyph))


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
    coso: float = 1.0
    sino: float = 0.0
    ipic: int = 1
    script_shift: float = 0.0
    manual_x_shift: float = 0.0
    manual_y_shift: float = 0.0
    zinx: float = 1.0
    ziny: float = 1.0
    zinz: float = 1.0
    line_index: int = 0


def _offset_from_text_axes(
    x: float,
    y: float,
    *,
    u: float,
    v: float,
    cursor: _RuntimeCursor,
) -> tuple[float, float]:
    return (
        float(x) + float(u) * cursor.coso - float(v) * cursor.sino,
        float(y) + float(u) * cursor.sino + float(v) * cursor.coso,
    )



@dataclass(frozen=True)
class _SvgRuntimeEvent:
    kind: str
    text: str = ""
    font_number: int = 21
    value: int = 0
    use_q_unit: bool = False


@dataclass(frozen=True)
class _SvgRuntimeParsedText:
    text: str
    events: tuple[_SvgRuntimeEvent, ...]


def _flush_text_event(
    events: list[_SvgRuntimeEvent],
    buffer: list[str],
    *,
    font_number: int,
) -> None:
    if not buffer:
        return

    events.append(
        _SvgRuntimeEvent(
            kind="text",
            text="".join(buffer),
            font_number=int(font_number),
        )
    )
    buffer.clear()


def _parse_int_command_value(token: str, command: str) -> int:
    raw = token[1:].strip()
    if raw == "":
        raise PlotcharUnsupportedError(
            f"Plotchar SVG runtime command {command!r} requires an integer value."
        )

    try:
        return int(raw)
    except ValueError as exc:
        raise PlotcharUnsupportedError(
            f"Plotchar SVG runtime command {command!r} received non-integer value {raw!r}."
        ) from exc


def _parse_optional_int_command_value(token: str, command: str) -> int:
    raw = token[1:].strip()
    if raw == "":
        return 0

    try:
        return int(raw)
    except ValueError as exc:
        raise PlotcharUnsupportedError(
            f"Plotchar SVG runtime command {command!r} received non-integer value {raw!r}."
        ) from exc


def _parse_svg_runtime_real_string_preserve_case(
    chrs: str,
    *,
    func_code: str,
    default_font_number: int,
) -> _SvgRuntimeParsedText:
    code = str(func_code)[0]
    across_prefix = f"{code}A{code}"
    down_prefix = f"{code}D{code}"

    if chrs.startswith(down_prefix):
        raise PlotcharUnsupportedError(
            "Down-text remains guarded until PLCHHQ NDWN/LCWD drawing semantics are fully mapped."
        )

    if not chrs.startswith(across_prefix):
        raise PlotcharUnsupportedError(
            "Plotchar SVG runtime currently accepts only TextItem Across real_string prefixes."
        )

    body = chrs[len(across_prefix):]
    events: list[_SvgRuntimeEvent] = []
    buffer: list[str] = []
    current_font = int(default_font_number)

    case_mode: str | None = None
    previous_case_mode: str | None = None
    case_countdown = 0

    def emit_plain_char(char: str) -> None:
        nonlocal case_mode, previous_case_mode, case_countdown

        if case_mode == "upper":
            out_char = char.upper()
        elif case_mode == "lower":
            out_char = char.lower()
        else:
            out_char = char

        buffer.append(out_char)

        if case_countdown > 0:
            case_countdown -= 1
            if case_countdown == 0:
                case_mode = previous_case_mode
                previous_case_mode = None

    i = 0
    while i < len(body):
        char = body[i]

        if char != code:
            emit_plain_char(char)
            i += 1
            continue

        j = body.find(code, i + 1)
        if j < 0:
            raise PlotcharUnsupportedError(
                "Plotchar SVG runtime found an unterminated function-code command."
            )

        token = body[i + 1:j]
        if token == "":
            buffer.append(code)
            i = j + 1
            continue

        command = token[0].upper()
        _flush_text_event(events, buffer, font_number=current_font)

        if command == "B":
            events.append(_SvgRuntimeEvent(kind="subscript", font_number=current_font))
        elif command == "S":
            events.append(_SvgRuntimeEvent(kind="superscript", font_number=current_font))
        elif command in {"N", "E"}:
            events.append(_SvgRuntimeEvent(kind="normal_script", font_number=current_font))
        elif command == "C":
            events.append(_SvgRuntimeEvent(kind="carriage_return", font_number=current_font))
        elif command == "P":
            events.append(_SvgRuntimeEvent(kind="principal", font_number=current_font))
        elif command == "I":
            events.append(_SvgRuntimeEvent(kind="indexical", font_number=current_font))
        elif command == "K":
            events.append(_SvgRuntimeEvent(kind="cartographic", font_number=current_font))
        elif command == "H":
            events.append(
                _SvgRuntimeEvent(
                    kind="hmove",
                    font_number=current_font,
                    value=_parse_int_command_value(token, command),
                )
            )
        elif command == "V":
            events.append(
                _SvgRuntimeEvent(
                    kind="vmove",
                    font_number=current_font,
                    value=_parse_int_command_value(token, command),
                )
            )
        elif command == "X":
            events.append(
                _SvgRuntimeEvent(
                    kind="xzoom",
                    font_number=current_font,
                    value=_parse_int_command_value(token, command),
                )
            )
        elif command == "Y":
            events.append(
                _SvgRuntimeEvent(
                    kind="yzoom",
                    font_number=current_font,
                    value=_parse_int_command_value(token, command),
                )
            )
        elif command == "Z":
            events.append(
                _SvgRuntimeEvent(
                    kind="zzoom",
                    font_number=current_font,
                    value=_parse_int_command_value(token, command),
                )
            )
        elif command == "F":
            current_font = _parse_int_command_value(token, command)
        elif command == "R":
            # NCL PLCHHQ font-definition branch:
            # R is for Roman font, implemented here as the current
            # source-mapped Roman/fontcap runtime path.
            pass
        elif command == "G":
            raise PlotcharUnsupportedError(
                "Plotchar G Greek-font command remains guarded. NCL PLCHHQ maps Greek "
                "through IFGR/INDA/IDDA digitization offsets, not the current fontcap "
                "font-number path. Implement the non-fontcap/PWRITX-digitization branch "
                "before enabling G."
            )
        elif command == "U":
            previous_case_mode = case_mode
            case_mode = "upper"
            case_countdown = _parse_optional_int_command_value(token, command)
        elif command == "L":
            previous_case_mode = case_mode
            case_mode = "lower"
            case_countdown = _parse_optional_int_command_value(token, command)
        else:
            raise PlotcharUnsupportedError(
                f"Plotchar SVG runtime does not yet implement function-code command {token!r}."
            )

        i = j + 1

    _flush_text_event(events, buffer, font_number=current_font)

    rendered_text = "".join(event.text for event in events if event.kind == "text")
    return _SvgRuntimeParsedText(
        text=rendered_text,
        events=tuple(events),
    )


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

    font_number = int(event.font_number)
    if font_number <= 0:
        raise PlotcharUnsupportedError(
            "PWRITX/font0/non-fontcap SVG draw remains guarded. "
            "Do not load font0 as a fontcap file; implement the non-fontcap "
            "digitization/draw branch before enabling font0 rendering."
        )

    fontcap = load_fontcap(font_number, fontcap_dir)
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

        center_x, center_y = _offset_from_text_axes(
            cursor.x,
            cursor.y,
            u=dtle * sizm,
            v=0.0,
            cursor=cursor,
        )

        if char != " ":
            for segment, fillable in _pieces_from_rdgu_glyph(glyph):
                points: list[tuple[float, float]] = []

                for gx, gy in segment:
                    px, py = _offset_from_text_axes(
                        center_x,
                        center_y,
                        u=cursor.manual_x_shift + sizm * xmzm * float(gx),
                        v=cursor.manual_y_shift + cursor.script_shift + sizm * ymzm * float(gy),
                        cursor=cursor,
                    )
                    points.append((px, py))

                if len(points) >= 2:
                    out.append(
                        PlotcharNdcPolyline(
                            points=tuple(points),
                            fillable=bool(fillable),
                        )
                    )

        cursor.x, cursor.y = _offset_from_text_axes(
            center_x,
            center_y,
            u=dtre * sizm,
            v=0.0,
            cursor=cursor,
        )

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
        line_step = float(cursor.line_index) * float(state.vpic[0]) * sizm
        cursor.x, cursor.y = _offset_from_text_axes(
            cursor.x0,
            cursor.y0,
            u=0.0,
            v=-line_step,
            cursor=cursor,
        )
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
    angle_deg: float,
    cntr: float = -1.0,
    fontcap_dir: str | Path | None,
) -> tuple[PlotcharNdcPolyline, ...]:
    angle = float(angle_deg)
    if math.isclose(angle, 360.0, abs_tol=1e-12):
        angle = 0.0

    radians = math.radians(angle)

    cursor = _RuntimeCursor(
        x0=float(xpos),
        y0=float(ypos),
        x=float(xpos),
        y=float(ypos),
        coso=math.cos(radians),
        sino=math.sin(radians),
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

    cntr_value = float(cntr)

    if not math.isclose(cntr_value, -1.0, rel_tol=0.0, abs_tol=1e-12):
        if cntr_value < -1.0 or cntr_value > 1.0:
            raise PlotcharUnsupportedError(
                "SVG Plotchar runtime supports CNTR in [-1, 1] for the current Across/fontcap subset only."
            )

        if any(str(event.kind) in {"carriage_return", "carriage", "newline"} for event in events):
            raise PlotcharUnsupportedError(
                "SVG Plotchar runtime keeps CNTR != -1 with carriage-return guarded until multi-line PLCHHQ draw adjustment is source-mapped."
            )

        xadj = -0.5 * (cntr_value + 1.0) * (cursor.x - cursor.x0)
        yadj = -0.5 * (cntr_value + 1.0) * (cursor.y - cursor.y0)

        shifted: list[PlotcharNdcPolyline] = []
        for poly in out:
            shifted.append(
                PlotcharNdcPolyline(
                    points=tuple((x + xadj, y + yadj) for x, y in poly.points)
                )
            )
        return tuple(shifted)

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
    cntr: Any | None = None,
    fontcap_dir: str | Path | None = None,
    pwritx_draw_provider=None,
    greek_draw_provider=None,
    mapped_draw_provider=None,
    map_mode: Any | None = None,
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

    if not math.isfinite(float(semantics.angle)):
        raise PlotcharUnsupportedError(
            "Current Plotchar SVG runtime requires a finite txAngleF value."
        )

    textitem_state = build_ncl_plotchar_textitem_state(semantics)
    plotchar_state = build_textitem_plotchar_state(textitem_state)

    if map_mode is not None:
        plotchar_state.pcseti("MA", int(map_mode))

    cntr_value = -1.0 if cntr is None else float(cntr)

    if (
        int(plotchar_state.nodf) <= 0
        or int(getattr(plotchar_state, "imap", 0)) > 0
        or _real_string_has_greek_command(semantics.real_string, plotchar_state)
    ):
        if int(plotchar_state.nodf) <= 0 and pwritx_draw_provider is None:
            raise PlotcharUnsupportedError(
                "TextItem SVG runtime keeps PWRITX/font0/non-fontcap draw guarded. "
                "Pass climaraPlotcharPwritxDrawProvider for explicit source-mapped provider rendering."
            )

        if _real_string_has_greek_command(semantics.real_string, plotchar_state) and greek_draw_provider is None:
            raise PlotcharUnsupportedError(
                "TextItem SVG runtime keeps G Greek draw guarded. "
                "Pass climaraPlotcharGreekDrawProvider for explicit source-mapped provider rendering."
            )

        if int(getattr(plotchar_state, "imap", 0)) > 0 and mapped_draw_provider is None:
            raise PlotcharUnsupportedError(
                "TextItem SVG runtime keeps mapped Plotchar draw guarded for IMAP > 0. "
                "Pass climaraPlotcharMappedDrawProvider for explicit source-mapped provider rendering."
            )

        origin_result = render_plchhq_real_string_to_ndc_polylines(
            chrs=semantics.real_string,
            state=plotchar_state,
            xpos=0.0,
            ypos=0.0,
            size=textitem_state.real_size,
            angle=float(semantics.angle),
            cntr=cntr_value,
            fontcap_dir=fontcap_dir,
            pwritx_draw_provider=pwritx_draw_provider,
            greek_draw_provider=greek_draw_provider,
            mapped_draw_provider=mapped_draw_provider,
        )

        x0, y0 = _start_origin_from_just(
            float(x),
            float(y),
            origin_result.metrics,
            semantics.just,
            angle_deg=semantics.angle,
        )

        return _translate_plotchar_svg_result(
            origin_result,
            dx=x0,
            dy=y0,
        )

    if not math.isclose(cntr_value, -1.0, rel_tol=0.0, abs_tol=1e-12):
        raise PlotcharUnsupportedError(
            "TextItem SVG runtime keeps CNTR fixed at -1. "
            "Use render_plchhq_real_string_to_ndc_polylines(...) for low-level PLCHHQ CNTR draw tests."
        )

    validated = compute_plchhq_fontcap_text_extent(
        chrs=semantics.real_string,
        state=plotchar_state,
        xpos=0.5,
        ypos=0.5,
        size=textitem_state.real_size,
        angle=float(semantics.angle),
        cntr=cntr_value,
        fontcap_dir=fontcap_dir,
    )

    parsed = _parse_svg_runtime_real_string_preserve_case(
        semantics.real_string,
        func_code=semantics.func_code,
        default_font_number=int(plotchar_state.nodf),
    )

    x0, y0 = _start_origin_from_just(
        float(x),
        float(y),
        validated.metrics,
        semantics.just,
        angle_deg=semantics.angle,
    )

    polylines = _render_events_to_ndc_polylines(
        parsed.events,
        state=plotchar_state,
        xpos=x0,
        ypos=y0,
        size=textitem_state.real_size,
        angle_deg=semantics.angle,
        cntr=cntr_value,
        fontcap_dir=fontcap_dir,
    )

    return PlotcharSvgRenderResult(
        polylines=polylines,
        metrics=validated.metrics,
        text=validated.text,
        font_number=int(plotchar_state.nodf),
    )





def _real_string_has_greek_command(chrs: str, state) -> bool:
    code = chr(state.nfcc) if getattr(state, "nfcc", -1) >= 0 else ":"
    return f"{code}G{code}" in str(chrs) or f"{code}g{code}" in str(chrs)


def render_plchhq_real_string_to_ndc_polylines(
    *,
    chrs: str,
    state,
    xpos: float,
    ypos: float,
    size: float,
    angle: float,
    cntr: float,
    fontcap_dir: str | Path | None = None,
    size_address_runtime_strategy=None,
    size_address_scale_provider=None,
    pwritx_draw_provider=None,
    greek_draw_provider=None,
    mapped_draw_provider=None,
) -> PlotcharSvgRenderResult:
    if int(getattr(state, "imap", 0)) > 0:
        if mapped_draw_provider is None:
            raise PlotcharUnsupportedError(
                "Mapped Plotchar SVG draw remains guarded for IMAP > 0. "
                "Pass an explicit source-mapped mapped_draw_provider to the low-level PLCHHQ renderer."
            )

        from ._plotchar_mapped_draw_provider import (
            MappedDrawRequest,
            validate_mapped_draw_provider,
        )

        validate_mapped_draw_provider(mapped_draw_provider)

        request = MappedDrawRequest(
            chrs=chrs,
            state=state,
            xpos=float(xpos),
            ypos=float(ypos),
            size=float(size),
            angle=float(angle),
            cntr=float(cntr),
            fontcap_dir=fontcap_dir,
        )

        draw_result = mapped_draw_provider.draw_for_request(request)

        from ._plotchar_draw_provider_contract import validate_plotchar_draw_provider_result

        validate_plotchar_draw_provider_result(
            draw_result,
            label="mapped",
        )

        polylines = tuple(
            PlotcharNdcPolyline(
                points=tuple(poly.points),
                fillable=bool(getattr(poly, "fillable", False)),
            )
            for poly in draw_result.polylines
        )

        return PlotcharSvgRenderResult(
            polylines=polylines,
            metrics=draw_result.metrics,
            text=draw_result.text,
            font_number=int(draw_result.font_number),
            glyph_count=int(draw_result.glyph_count),
        )

    if _real_string_has_greek_command(chrs, state):
        if greek_draw_provider is None:
            raise PlotcharUnsupportedError(
                "G Greek SVG draw remains guarded. NCL PLCHHQ uses IFGR/INDA/IDDA "
                "digitization offsets for Greek glyph selection; pass an explicit "
                "source-mapped greek_draw_provider to the low-level PLCHHQ renderer."
            )

        from ._plotchar_greek_draw_provider import (
            GreekDrawRequest,
            validate_greek_draw_provider,
        )

        validate_greek_draw_provider(greek_draw_provider)

        request = GreekDrawRequest(
            chrs=chrs,
            state=state,
            xpos=float(xpos),
            ypos=float(ypos),
            size=float(size),
            angle=float(angle),
            cntr=float(cntr),
            fontcap_dir=fontcap_dir,
        )

        draw_result = greek_draw_provider.draw_for_request(request)

        from ._plotchar_draw_provider_contract import validate_plotchar_draw_provider_result

        validate_plotchar_draw_provider_result(
            draw_result,
            label="greek",
        )

        polylines = tuple(
            PlotcharNdcPolyline(
                points=tuple(poly.points),
                fillable=bool(getattr(poly, "fillable", False)),
            )
            for poly in draw_result.polylines
        )

        return PlotcharSvgRenderResult(
            polylines=polylines,
            metrics=draw_result.metrics,
            text=draw_result.text,
            font_number=int(draw_result.font_number),
            glyph_count=int(draw_result.glyph_count),
        )

    if int(getattr(state, "nodf", 1)) <= 0:
        if pwritx_draw_provider is None:
            raise PlotcharUnsupportedError(
                "PWRITX/font0/non-fontcap SVG draw remains guarded. "
                "Pass an explicit source-mapped pwritx_draw_provider to the low-level PLCHHQ renderer."
            )

        from ._plotchar_pwritx_draw_provider import (
            PwritxDrawRequest,
            validate_pwritx_draw_provider,
        )

        validate_pwritx_draw_provider(pwritx_draw_provider)

        request = PwritxDrawRequest(
            chrs=chrs,
            state=state,
            xpos=float(xpos),
            ypos=float(ypos),
            size=float(size),
            angle=float(angle),
            cntr=float(cntr),
            fontcap_dir=fontcap_dir,
        )

        draw_result = pwritx_draw_provider.draw_for_request(request)

        from ._plotchar_draw_provider_contract import validate_plotchar_draw_provider_result

        validate_plotchar_draw_provider_result(
            draw_result,
            label="pwritx",
        )

        polylines = tuple(
            PlotcharNdcPolyline(
                points=tuple(poly.points),
                fillable=bool(getattr(poly, "fillable", False)),
            )
            for poly in draw_result.polylines
        )

        return PlotcharSvgRenderResult(
            polylines=polylines,
            metrics=draw_result.metrics,
            text=draw_result.text,
            font_number=int(draw_result.font_number),
            glyph_count=int(draw_result.glyph_count),
        )

    validated = compute_plchhq_fontcap_text_extent(
        chrs=chrs,
        state=state,
        xpos=xpos,
        ypos=ypos,
        size=size,
        angle=angle,
        cntr=cntr,
        fontcap_dir=fontcap_dir,
        size_address_runtime_strategy=size_address_runtime_strategy,
        size_address_scale_provider=size_address_scale_provider,
    )

    draw_size = float(size)

    if size_address_scale_provider is not None:
        from ._plotchar_size_address_unit import SizeAddressUnitRequest

        request = SizeAddressUnitRequest(
            chrs=chrs,
            state=state,
            xpos=float(xpos),
            ypos=float(ypos),
            size=float(size),
            angle=float(angle),
            cntr=float(cntr),
            fontcap_dir=fontcap_dir,
        )
        draw_size = float(size_address_scale_provider.fractional_core_size(request))

    parsed = _parse_svg_runtime_real_string_preserve_case(
        chrs,
        func_code=chr(state.nfcc) if state.nfcc >= 0 else ":",
        default_font_number=int(state.nodf),
    )

    polylines = _render_events_to_ndc_polylines(
        parsed.events,
        state=state,
        xpos=float(xpos),
        ypos=float(ypos),
        size=draw_size,
        angle_deg=float(angle),
        cntr=float(cntr),
        fontcap_dir=fontcap_dir,
    )

    return PlotcharSvgRenderResult(
        polylines=polylines,
        metrics=validated.metrics,
        text=validated.text,
        font_number=int(state.nodf),
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
        cntr=resources.get("climaraPlotcharCntr"),
        fontcap_dir=fontcap_dir,
        pwritx_draw_provider=resources.get("climaraPlotcharPwritxDrawProvider"),
        greek_draw_provider=resources.get("climaraPlotcharGreekDrawProvider"),
        mapped_draw_provider=resources.get("climaraPlotcharMappedDrawProvider"),
        map_mode=resources.get("climaraPlotcharMapMode"),
    )


__all__ = [
    "PlotcharNdcPolyline",
    "PlotcharSvgRenderResult",
    "render_plchhq_real_string_to_ndc_polylines",
    "render_text_object_to_ndc_polylines",
    "render_text_semantics_to_ndc_polylines",
]
