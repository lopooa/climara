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


def glyph_text(font_number: int = 21, count: int = 3) -> str:
    fontcap = load_fontcap(font_number, fontcap_dir())
    preferred = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

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
    a, b, c = glyph_text(21, count=3)

    parsed = parse_textitem_plotchar_real_string(
        f"~A~{a}~I~{b}~K~{c}~P~{a}",
        func_code="~",
        default_font_number=21,
    )
    assert parsed.text == a + b + c + a
    assert [event.kind for event in parsed.events] == [
        "text",
        "size",
        "text",
        "size",
        "text",
        "size",
        "text",
    ]
    assert [event.value for event in parsed.events if event.kind == "size"] == [2, 3, 1]

    principal = compute_real_string(f"~A~{a}{b}{c}")
    indexical = compute_real_string(f"~A~{a}~I~{b}{c}")
    cartographic = compute_real_string(f"~A~{a}~K~{b}{c}")
    restored = compute_real_string(f"~A~{a}~I~{b}~P~{c}")

    assert principal.metrics.width > 0.0
    assert indexical.metrics.width > 0.0
    assert cartographic.metrics.width > 0.0
    assert restored.metrics.width > 0.0

    assert indexical.metrics.height <= principal.metrics.height
    assert cartographic.metrics.height <= principal.metrics.height
    assert restored.text == a + b + c

    print("✅ Python Plotchar P/I/K size-level function-code smoke passed")


if __name__ == "__main__":
    main()
