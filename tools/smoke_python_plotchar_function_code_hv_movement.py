from __future__ import annotations

import os
from pathlib import Path

from climara.graphics._ncl_plotchar_textitem import build_ncl_plotchar_textitem_state
from climara.graphics._plotchar_fontcap import load_fontcap
from climara.graphics._plotchar_function_code import parse_textitem_plotchar_real_string
from climara.graphics._plotchar_plchhq_extent import compute_plchhq_fontcap_text_extent
from climara.graphics._plotchar_state import PlotcharUnsupportedError, build_textitem_plotchar_state
from climara.graphics._text_semantics import build_text_item_semantics


def fontcap_dir() -> Path:
    explicit = os.environ.get("CLIMARA_PLOTCHAR_FONTCAP_DIR")
    if explicit:
        return Path(explicit)

    ncl_root = os.environ.get("NCL_SRC_ROOT")
    if not ncl_root:
        raise SystemExit("Set NCL_SRC_ROOT=/mnt/d/Projects/NCL or CLIMARA_PLOTCHAR_FONTCAP_DIR")

    return Path(ncl_root) / "common" / "src" / "fontcap"


def glyph_text(font_number: int = 21, count: int = 2) -> str:
    fontcap = load_fontcap(font_number, fontcap_dir())
    preferred = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    chars = []

    for char in preferred:
        try:
            fontcap.glyph_for_ascii(ord(char))
        except PlotcharUnsupportedError:
            continue
        chars.append(char)
        if len(chars) == count:
            return "".join(chars)

    raise AssertionError(f"Not enough glyphs in font{font_number}")


def compute_real_string(chrs: str):
    semantics = build_text_item_semantics(
        "",
        func_code="~",
        font=21,
        font_height=0.04,
        font_aspect=2.0,
        font_quality="High",
        constant_spacing=0.0,
    )
    textitem_state = build_ncl_plotchar_textitem_state(semantics)
    state = build_textitem_plotchar_state(textitem_state)

    return compute_plchhq_fontcap_text_extent(
        chrs=chrs,
        state=state,
        xpos=0.5,
        ypos=0.5,
        size=textitem_state.real_size,
        angle=360.0,
        cntr=-1.0,
        fontcap_dir=fontcap_dir(),
    )


def main():
    a, b = glyph_text(21, count=2)

    parsed = parse_textitem_plotchar_real_string(
        f"~A~{a}~H10~{b}",
        func_code="~",
        default_font_number=21,
    )
    assert parsed.text == a + b
    assert [event.kind for event in parsed.events] == ["text", "hmove", "text"]
    assert parsed.events[1].value == 10
    assert parsed.events[1].use_q_unit is False

    parsed = parse_textitem_plotchar_real_string(
        f"~A~{a}~H1Q~{b}",
        func_code="~",
        default_font_number=21,
    )
    assert parsed.events[1].kind == "hmove"
    assert parsed.events[1].value == 1
    assert parsed.events[1].use_q_unit is True

    parsed = parse_textitem_plotchar_real_string(
        f"~A~{a}~V0Q~{b}",
        func_code="~",
        default_font_number=21,
    )
    assert parsed.events[1].kind == "vmove"
    assert parsed.events[1].value == 0
    assert parsed.events[1].use_q_unit is True

    plain = compute_real_string(f"~A~{a}{b}")
    hmove = compute_real_string(f"~A~{a}~H10~{b}")
    hmove_q = compute_real_string(f"~A~{a}~H1Q~{b}")
    vmove = compute_real_string(f"~A~{a}~V10~{b}")
    vmove_q = compute_real_string(f"~A~{a}~V0Q~{b}")

    assert hmove.text == a + b
    assert hmove.metrics.width > plain.metrics.width
    assert hmove_q.metrics.width > plain.metrics.width

    assert vmove.text == a + b
    assert vmove.metrics.height > plain.metrics.height
    assert vmove_q.metrics.height > plain.metrics.height

    assert hmove.state.pcgetr("XE") > plain.state.pcgetr("XE")
    assert vmove.state.pcgetr("YE") > plain.state.pcgetr("YE")

    negative_h = compute_real_string(f"~A~{a}~H-1~{b}")
    assert negative_h.metrics.width > 0.0
    assert negative_h.metrics.height > 0.0

    print("✅ Python Plotchar H/V movement function-code smoke passed")


if __name__ == "__main__":
    main()
