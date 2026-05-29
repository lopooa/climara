from __future__ import annotations

from ._plotchar_size_address_unit import (
    build_size_address_unit_request,
    compute_size_address_unit_extent,
    size_address_unit_requested,
)

from ._plotchar_mapped_coordinate import (
    MappedCoordinateTransformProvider,
    build_mapped_coordinate_request,
    compute_mapped_coordinate_extent,
    mapped_coordinate_requested,
    raise_mapped_coordinate_guard,
)

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from ._plotchar_fontcap import PlotcharRdguGlyph, glyphs_to_rdgu, load_fontcap
from ._plotchar_function_code import parse_textitem_plotchar_real_string
from ._plotchar_metrics import PlotcharExtentMetrics, build_plotchar_extent_metrics
from ._plotchar_state import PlotcharState, PlotcharStateError, PlotcharUnsupportedError, build_textitem_plotchar_state


@dataclass(frozen=True)
class PlotcharTextExtentResult:
    metrics: PlotcharExtentMetrics
    state: PlotcharState
    text: str
    font_number: int
    glyph_count: int


def _require_textitem_measurement_contract(*, angle: float, cntr: float, state: PlotcharState) -> None:
    angle_value = float(angle)
    cntr_value = float(cntr)

    if not math.isfinite(angle_value):
        raise PlotcharUnsupportedError(
            "Python PLCHHQ extent core requires a finite ANGD value."
        )

    if not math.isfinite(cntr_value):
        raise PlotcharUnsupportedError(
            "Python PLCHHQ extent core requires a finite CNTR value."
        )

    if cntr_value < -1.0 or cntr_value > 1.0:
        raise PlotcharUnsupportedError(
            "Python PLCHHQ extent core currently supports source-mapped CNTR in [-1, 1] only."
        )

    if int(state.itef) != 1:
        raise PlotcharUnsupportedError(
            "Python PLCHHQ extent core requires PCSETI('TE', 1), matching TextItem.c DoPcCalc."
        )
    if int(state.iquf) != 0:
        raise PlotcharUnsupportedError(
            "Python PLCHHQ fontcap extent core currently maps the high-quality Plotchar branch only (IQUF == 0)."
        )
    if int(state.imap) != 0:
        raise_mapped_coordinate_guard()





def _text_from_textitem_real_string(chrs: str, *, func_code: str) -> str:
    parsed = parse_textitem_plotchar_real_string(chrs, func_code=func_code)
    return parsed.text

def _plotchar_sizm(size: float, state: PlotcharState) -> float:
    # PLCHHQ.f lines 284-302 for IMAP <= 0 and TextItem SIZE < 1.
    size = float(size)
    if size <= 0.0:
        raise PlotcharUnsupportedError(
            "Python PLCHHQ extent core does not yet support SIZE <= 0.0 address-unit semantics."
        )
    if size >= 1.0:
        raise PlotcharUnsupportedError(
            "Python PLCHHQ extent core currently implements TextItem fractional SIZE < 1.0 only."
        )
    if state.wpic[0] == 0.0:
        raise PlotcharStateError("WPIC(1) is zero; cannot reproduce PLCHHQ SIZM=SIZE/WPIC(1)")

    sizm = size / float(state.wpic[0])
    if int(state.iquf) == 0:
        sizm = float(state.siza) * sizm
    return sizm


def _set_plchhq_geometry_state(
    state: PlotcharState,
    *,
    xbeg: float,
    ybeg: float,
    xcen: float,
    ycen: float,
    xend: float,
    yend: float,
) -> None:
    # PLCHHQ stores XBEG/YBEG/XEND/YEND in the PCPRMS common block for
    # later PCGETR retrieval. XCEN/YCEN are the current character center
    # variables and are not shifted by the final centering adjustment in
    # the PLCHHQ end-of-string block.
    state.xbeg = float(xbeg)
    state.ybeg = float(ybeg)
    state.xcen = float(xcen)
    state.ycen = float(ycen)
    state.xend = float(xend)
    state.yend = float(yend)


def _spacing_for_glyph(state: PlotcharState, glyph: PlotcharRdguGlyph, ipic: int) -> tuple[float, float]:
    xmzm = float(state.zinx) * float(state.zinz) * float(state.xmul[ipic - 1])
    if state.cons == 0.0:
        return -xmzm * glyph.rdgu_left, xmzm * glyph.rdgu_right
    if state.cons < 0.0:
        return -float(state.cons), -float(state.cons)
    return float(state.cons) * float(state.wpic[ipic - 1]), float(state.cons) * float(state.wpic[ipic - 1])


def compute_plchhq_extent_from_rdgu_glyphs(
    glyphs: Iterable[PlotcharRdguGlyph],
    *,
    state: PlotcharState,
    xpos: float,
    ypos: float,
    size: float,
    angle: float,
    cntr: float,
) -> PlotcharExtentResult:
    _require_textitem_measurement_contract(angle=angle, cntr=cntr, state=state)

    glyphs = tuple(glyphs)
    if not glyphs:
        state._set_extent_vectors_from_plchhq(dl=0.0, dr=0.0, db=0.0, dt=0.0)
        _set_plchhq_geometry_state(
            state,
            xbeg=float(xpos),
            ybeg=float(ypos),
            xcen=float(xpos),
            ycen=float(ypos),
            xend=float(xpos),
            yend=float(ypos),
        )
        return PlotcharTextExtentResult(
            metrics=build_plotchar_extent_metrics(dl=0.0, dr=0.0, db=0.0, dt=0.0),
            state=state,
            text="",
            font_number=int(state.nodf),
            glyph_count=0,
        )

    sizm = _plotchar_sizm(size, state)
    angrad = math.radians(float(angle))
    sino = math.sin(angrad)
    coso = math.cos(angrad)
    stso = sizm * sino
    stco = sizm * coso

    xfra = float(xpos)
    yfra = float(ypos)
    xbeg = xfra
    ybeg = yfra
    xcen = xbeg
    ycen = ybeg
    xrgt = xbeg
    yrgt = ybeg

    dstl = -1.0e6
    dstr = -1.0e6
    dstb = -1.0e6
    dstt = -1.0e6

    addp = 0.0
    subp = 0.0
    vepc = 0.0
    ipic = 1

    xmzm = float(state.zinx) * float(state.zinz) * float(state.xmul[ipic - 1])
    ymzm = float(state.ziny) * float(state.zinz) * float(state.ymul[ipic - 1])

    for glyph in glyphs:
        dtle, dtre = _spacing_for_glyph(state, glyph, ipic)

        xcen = xrgt + dtle * stco
        ycen = yrgt + dtle * stso

        if addp != 0.0:
            if state.adds < 0.0:
                xcen += addp * stco
                ycen += addp * stso
            else:
                xcen += 0.5 * (addp + state.adds * state.wpic[ipic - 1]) * stco
                ycen += 0.5 * (addp + state.adds * state.wpic[ipic - 1]) * stso

        if subp != 0.0:
            if state.subs < 0.0:
                xcen -= subp * stco
                ycen -= subp * stso
            else:
                xcen -= 0.5 * (subp + state.subs * state.wpic[ipic - 1]) * stco
                ycen -= 0.5 * (subp + state.subs * state.wpic[ipic - 1]) * stso

        xrgt = xcen + dtre * stco
        yrgt = ycen + dtre * stso

        ucen = +(xcen - xfra) * coso + (ycen - yfra) * sino
        vcen = -(xcen - xfra) * sino + (ycen - yfra) * coso

        for x, y in glyph.points:
            if x > -2047.0:
                dstl = max(dstl, -ucen - sizm * xmzm * x)
                dstr = max(dstr, +ucen + sizm * xmzm * x)
                dstb = max(dstb, -vcen - sizm * ymzm * y)
                dstt = max(dstt, +vcen + sizm * ymzm * y)

        vepc = state.vpic[ipic - 1]

        if state.adds < 0.0:
            addp = -state.adds
        elif state.adds > 0.0:
            addp = state.adds * state.wpic[ipic - 1]
        else:
            addp = 0.0

        if state.subs < 0.0:
            subp = -state.subs
        elif state.subs > 0.0:
            subp = state.subs * state.wpic[ipic - 1]
        else:
            subp = 0.0

    # PLCHHQ end-of-string for Across text: XEND=XRGT/YEND=YRGT. For TextItem's
    # CNTR=-1, XADJ/YADJ are exactly zero, but keep the formula here because it
    # is the source boundary that must be extended when other CNTR cases are mapped.
    xend = xrgt
    yend = yrgt
    xadj = -0.5 * (float(cntr) + 1.0) * (xend - xbeg)
    yadj = -0.5 * (float(cntr) + 1.0) * (yend - ybeg)

    dstl = dstl - xadj * coso - yadj * sino
    dstr = dstr + xadj * coso + yadj * sino
    dstb = dstb + xadj * sino - yadj * coso
    dstt = dstt - xadj * sino + yadj * coso

    _set_plchhq_geometry_state(
        state,
        xbeg=xbeg + xadj,
        ybeg=ybeg + yadj,
        xcen=xcen,
        ycen=ycen,
        xend=xend + xadj,
        yend=yend + yadj,
    )

    if min(dstl, dstr, dstb, dstt) <= -999999.0:
        # This can happen for strings with only spaces or empty/no-point glyphs.
        dstl = dstr = dstb = dstt = 0.0

    state._set_extent_vectors_from_plchhq(dl=dstl, dr=dstr, db=dstb, dt=dstt)

    return PlotcharTextExtentResult(
        metrics=build_plotchar_extent_metrics(dl=dstl, dr=dstr, db=dstb, dt=dstt),
        state=state,
        text="",
        font_number=int(state.nodf),
        glyph_count=len(glyphs),
    )








def compute_plchhq_extent_from_plotchar_events(
    events,
    *,
    state: PlotcharState,
    xpos: float,
    ypos: float,
    size: float,
    angle: float,
    cntr: float,
    fontcap_dir: str | Path | None = None,
) -> PlotcharTextExtentResult:
    _require_textitem_measurement_contract(angle=angle, cntr=cntr, state=state)

    sizm = _plotchar_sizm(size, state)
    angrad = math.radians(float(angle))
    sino = math.sin(angrad)
    coso = math.cos(angrad)
    sinm = math.sin(angrad - math.pi / 2.0)
    cosm = math.cos(angrad - math.pi / 2.0)
    sinp = math.sin(angrad + math.pi / 2.0)
    cosp = math.cos(angrad + math.pi / 2.0)
    stso = sizm * sino
    stco = sizm * coso

    xfra = float(xpos)
    yfra = float(ypos)
    xbeg = xfra
    ybeg = yfra
    xbol = xbeg
    ybol = ybeg
    xcen = xbeg
    ycen = ybeg
    xrgt = xbeg
    yrgt = ybeg

    dstl = -1.0e6
    dstr = -1.0e6
    dstb = -1.0e6
    dstt = -1.0e6

    addp = 0.0
    subp = 0.0
    ipic = 1
    glyph_count = 0
    text_parts: list[str] = []

    ndwn = 0
    lcwd = 0
    vepc = 0.0

    xmzm = [
        float(state.zinx) * float(state.zinz) * float(value)
        for value in state.xmul
    ]
    ymzm = [
        float(state.ziny) * float(state.zinz) * float(value)
        for value in state.ymul
    ]

    script_stack: list[dict[str, float | int]] = []

    def zoom_value(value: int) -> float:
        zoom = float(value) / 100.0
        if zoom == 0.0:
            zoom = 1.0
        return zoom

    def y_zoom_q_adjust(old_zoom: float, new_zoom: float) -> None:
        nonlocal xcen, ycen, xrgt, yrgt

        if int(state.iquf) != 0:
            return

        dely = 0.5 * float(state.hpic[ipic - 1]) * (new_zoom - old_zoom)
        xcen -= dely * stso
        ycen += dely * stco
        xrgt -= dely * stso
        yrgt += dely * stco

    def push_script(kind: str, count: int) -> None:
        nonlocal xrgt, yrgt, ipic

        if len(script_stack) >= 5:
            active_level = 5
        else:
            active_level = len(script_stack) + 1

        if kind == "subscript":
            sint = sinm
            cost = cosm
        else:
            sint = sinp
            cost = cosp

        offs = float(state.sspr) * sizm
        if ipic != 1:
            offs = float(state.ssic) * sizm

        cost *= offs
        sint *= offs

        script_stack.append(
            {
                "xcen": xcen,
                "ycen": ycen,
                "xrgt": xrgt,
                "yrgt": yrgt,
                "ipic": ipic,
                "sint": sint,
                "cost": cost,
                "count": int(count),
                "level": active_level,
            }
        )

        xrgt += cost
        yrgt += sint

        if ipic == 1:
            ipic = 2
        else:
            ipic = 3

    def pop_script_end() -> None:
        nonlocal xcen, ycen, xrgt, yrgt, ipic

        if not script_stack:
            return

        saved = script_stack.pop()
        xcen = float(saved["xcen"])
        ycen = float(saved["ycen"])
        xrgt = float(saved["xrgt"])
        yrgt = float(saved["yrgt"])
        ipic = int(saved["ipic"])

    def pop_script_normal() -> None:
        nonlocal xcen, ycen, xrgt, yrgt, ipic

        if not script_stack:
            return

        saved = script_stack.pop()
        xcen = float(saved["xcen"])
        ycen = float(saved["ycen"])
        xrgt -= float(saved["cost"])
        yrgt -= float(saved["sint"])
        ipic = int(saved["ipic"])

    def after_glyph_script_countdown() -> None:
        if not script_stack:
            return

        top = script_stack[-1]
        count = int(top["count"])
        if count > 0:
            count -= 1
            top["count"] = count
            if count == 0:
                pop_script_end()

    for event in events:
        if event.kind == "down":
            ndwn = int(event.value)
            if ndwn <= 0:
                ndwn = 10**9
            lcwd = 1
            continue

        if event.kind == "across":
            ndwn = 0
            lcwd = 0
            continue

        if event.kind == "size":
            value = int(event.value)
            if value not in (1, 2, 3):
                raise PlotcharUnsupportedError(
                    f"Unsupported PLCHHQ size-level IPIC value: {value!r}"
                )
            ipic = value
            continue

        if event.kind in {"subscript", "superscript"}:
            push_script(event.kind, int(event.value))
            continue

        if event.kind == "end_script":
            pop_script_end()
            continue

        if event.kind == "normal_script":
            pop_script_normal()
            continue

        if event.kind == "carriage":
            xbol = xbol + sizm * float(state.vpic[ipic - 1]) * cosm
            ybol = ybol + sizm * float(state.vpic[ipic - 1]) * sinm
            xcen = xbol
            ycen = ybol
            xrgt = xbol
            yrgt = ybol
            addp = 0.0
            subp = 0.0
            continue

        if event.kind == "xzoom":
            zoom = zoom_value(int(event.value))
            xmzm = [zoom * float(value) for value in state.xmul]
            continue

        if event.kind == "yzoom":
            old_zoom = ymzm[0] / float(state.ymul[0])
            zoom = zoom_value(int(event.value))
            ymzm = [zoom * float(value) for value in state.ymul]

            if bool(event.use_q_unit):
                y_zoom_q_adjust(old_zoom, zoom)

            continue

        if event.kind == "zzoom":
            old_zoom = ymzm[0] / float(state.ymul[0])
            zoom = zoom_value(int(event.value))
            xmzm = [zoom * float(value) for value in state.xmul]
            ymzm = [zoom * float(value) for value in state.ymul]

            if bool(event.use_q_unit):
                y_zoom_q_adjust(old_zoom, zoom)

            continue

        if event.kind == "hmove":
            nupa = int(event.value)
            delx = float(nupa)
            if bool(event.use_q_unit):
                if nupa == 0:
                    nupa = 1
                delx = float(nupa) * float(state.wpic[ipic - 1])

            xcen += delx * stco
            ycen += delx * stso
            xrgt += delx * stco
            yrgt += delx * stso
            continue

        if event.kind == "vmove":
            nupa = int(event.value)
            dely = float(nupa)
            if bool(event.use_q_unit):
                if nupa == 0:
                    nupa = 1
                dely = float(nupa) * float(state.vpic[ipic - 1])

            xcen -= dely * stso
            ycen += dely * stco
            xrgt -= dely * stso
            yrgt += dely * stco
            continue

        if event.kind != "text":
            raise PlotcharUnsupportedError(
                f"Unsupported Plotchar parsed event kind: {event.kind!r}"
            )

        segment_text = event.text
        if any(ord(char) < 32 or ord(char) > 126 for char in segment_text):
            raise PlotcharUnsupportedError(
                "Python PLCHHQ fontcap extent core currently supports printable ASCII fontcap characters only."
            )

        fontcap = load_fontcap(int(event.font_number), fontcap_dir)
        glyphs = [fontcap.glyph_for_ascii(ord(char)) for char in segment_text]
        rdgu_glyphs = glyphs_to_rdgu(glyphs, fontcap.metrics, chgt=state.hpic[ipic - 1])

        text_parts.append(segment_text)
        glyph_count += len(glyphs)

        for glyph in rdgu_glyphs:
            dtle, dtre = _spacing_for_glyph(state, glyph, ipic)

            if ndwn > 0 and len(script_stack) == 0:
                lcwd = 1
                xcen += 0.5 * sizm * (vepc + float(state.vpic[ipic - 1])) * cosm
                ycen += 0.5 * sizm * (vepc + float(state.vpic[ipic - 1])) * sinm

                if addp != 0.0:
                    if state.adds < 0.0:
                        xcen += sizm * addp * cosm
                        ycen += sizm * addp * sinm
                    else:
                        xcen += sizm * 0.5 * (addp + state.adds * state.wpic[ipic - 1]) * cosm
                        ycen += sizm * 0.5 * (addp + state.adds * state.wpic[ipic - 1]) * sinm

                if subp != 0.0:
                    if state.subs < 0.0:
                        xcen -= sizm * subp * cosm
                        ycen -= sizm * subp * sinm
                    else:
                        xcen -= sizm * 0.5 * (subp + state.subs * state.wpic[ipic - 1]) * cosm
                        ycen -= sizm * 0.5 * (subp + state.subs * state.wpic[ipic - 1]) * sinm

                ndwn -= 1
            else:
                lcwd = 0

            if lcwd == 0:
                xcen = xrgt + dtle * stco
                ycen = yrgt + dtle * stso

                if addp != 0.0:
                    if state.adds < 0.0:
                        xcen += addp * stco
                        ycen += addp * stso
                    else:
                        xcen += 0.5 * (addp + state.adds * state.wpic[ipic - 1]) * stco
                        ycen += 0.5 * (addp + state.adds * state.wpic[ipic - 1]) * stso

                if subp != 0.0:
                    if state.subs < 0.0:
                        xcen -= subp * stco
                        ycen -= subp * stso
                    else:
                        xcen -= 0.5 * (subp + state.subs * state.wpic[ipic - 1]) * stco
                        ycen -= 0.5 * (subp + state.subs * state.wpic[ipic - 1]) * stso

            xrgt = xcen + dtre * stco
            yrgt = ycen + dtre * stso

            ucen = +(xcen - xfra) * coso + (ycen - yfra) * sino
            vcen = -(xcen - xfra) * sino + (ycen - yfra) * coso

            for x, y in glyph.points:
                if x > -2047.0:
                    dstl = max(dstl, -ucen - sizm * xmzm[ipic - 1] * x)
                    dstr = max(dstr, +ucen + sizm * xmzm[ipic - 1] * x)
                    dstb = max(dstb, -vcen - sizm * ymzm[ipic - 1] * y)
                    dstt = max(dstt, +vcen + sizm * ymzm[ipic - 1] * y)

            vepc = float(state.vpic[ipic - 1])

            if state.adds < 0.0:
                addp = -state.adds
            elif state.adds > 0.0:
                addp = state.adds * state.wpic[ipic - 1]
            else:
                addp = 0.0

            if state.subs < 0.0:
                subp = -state.subs
            elif state.subs > 0.0:
                subp = state.subs * state.wpic[ipic - 1]
            else:
                subp = 0.0

            after_glyph_script_countdown()

    if lcwd != 0:
        xend = xcen + 0.5 * vepc * stso
        yend = ycen - 0.5 * vepc * stco
    else:
        xend = xrgt
        yend = yrgt

    xadj = -0.5 * (float(cntr) + 1.0) * (xend - xbeg)
    yadj = -0.5 * (float(cntr) + 1.0) * (yend - ybeg)

    dstl = dstl - xadj * coso - yadj * sino
    dstr = dstr + xadj * coso + yadj * sino
    dstb = dstb + xadj * sino - yadj * coso
    dstt = dstt - xadj * sino + yadj * coso

    _set_plchhq_geometry_state(
        state,
        xbeg=xbeg + xadj,
        ybeg=ybeg + yadj,
        xcen=xcen,
        ycen=ycen,
        xend=xend + xadj,
        yend=yend + yadj,
    )

    if min(dstl, dstr, dstb, dstt) <= -999999.0:
        dstl = dstr = dstb = dstt = 0.0

    state._set_extent_vectors_from_plchhq(dl=dstl, dr=dstr, db=dstb, dt=dstt)

    return PlotcharTextExtentResult(
        metrics=build_plotchar_extent_metrics(dl=dstl, dr=dstr, db=dstb, dt=dstt),
        state=state,
        text="".join(text_parts),
        font_number=int(state.nodf),
        glyph_count=glyph_count,
    )

def compute_plchhq_fontcap_text_extent(
    *,
    chrs: str,
    state: PlotcharState,
    xpos: float,
    ypos: float,
    size: float,
    angle: float,
    cntr: float,
    fontcap_dir: str | Path | None = None,
    mapped_transform_provider: MappedCoordinateTransformProvider | None = None,
    mapped_runtime_strategy: object | None = None,
    size_address_runtime_strategy: object | None = None,
    size_address_scale_provider: object | None = None,
) -> PlotcharTextExtentResult:
    if size_address_unit_requested(size):
        request = build_size_address_unit_request(
            chrs=chrs,
            state=state,
            xpos=xpos,
            ypos=ypos,
            size=size,
            angle=angle,
            cntr=cntr,
            fontcap_dir=fontcap_dir,
            runtime_strategy=size_address_runtime_strategy,
            scale_provider=size_address_scale_provider,
        )
        size_result = compute_size_address_unit_extent(request)
        return PlotcharTextExtentResult(
            metrics=size_result.metrics,
            state=size_result.state,
            text=size_result.text,
            font_number=size_result.font_number,
            glyph_count=size_result.glyph_count,
        )

    if mapped_coordinate_requested(state):
        request = build_mapped_coordinate_request(
            chrs=chrs,
            state=state,
            xpos=xpos,
            ypos=ypos,
            size=size,
            angle=angle,
            cntr=cntr,
            fontcap_dir=fontcap_dir,
            transform_provider=mapped_transform_provider,
            runtime_strategy=mapped_runtime_strategy,
        )
        mapped_result = compute_mapped_coordinate_extent(request)
        return PlotcharTextExtentResult(
            metrics=mapped_result.metrics,
            state=mapped_result.state,
            text=mapped_result.text,
            font_number=mapped_result.font_number,
            glyph_count=mapped_result.glyph_count,
        )

    parsed = parse_textitem_plotchar_real_string(
        chrs,
        func_code=chr(state.nfcc) if state.nfcc >= 0 else ":",
        default_font_number=int(state.nodf),
    )
    return compute_plchhq_extent_from_plotchar_events(
        parsed.events,
        state=state,
        xpos=xpos,
        ypos=ypos,
        size=size,
        angle=angle,
        cntr=cntr,
        fontcap_dir=fontcap_dir,
    )


def _require_textitem_fontcap_mainline_call(call) -> None:
    state = call.state
    quality_index = int(getattr(state, "quality_index", -1))
    effective_font = int(getattr(state, "effective_font", -999))
    font = int(getattr(state, "font", effective_font))

    if quality_index != 0:
        raise PlotcharUnsupportedError(
            "Python Plotchar mainline currently implements only the NCL high-quality "
            "fontcap branch for TextItem measurement. Medium, Low, and Workstation "
            "quality paths use different PLCHHQ/PWRITX/workstation semantics and "
            "must remain guarded until mapped from the NCL source."
        )

    if effective_font == 0 or font == 0:
        raise PlotcharUnsupportedError(
            "NCL Plotchar font 0 selects the PWRITX database / non-fontcap branch. "
            "The Python mainline currently implements the fontcap branch only and "
            "must not approximate PWRITX metrics."
        )


def compute_textitem_call_fontcap_metrics(call, *, fontcap_dir: str | Path | None = None) -> PlotcharExtentMetrics:
    _require_textitem_fontcap_mainline_call(call)

    state = build_textitem_plotchar_state(call.state)
    return compute_plchhq_fontcap_text_extent(
        chrs=call.chrs,
        state=state,
        xpos=call.xpos,
        ypos=call.ypos,
        size=call.size,
        angle=call.angd,
        cntr=call.cntr,
        fontcap_dir=fontcap_dir,
    ).metrics

