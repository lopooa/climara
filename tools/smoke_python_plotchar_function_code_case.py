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


def has_glyphs(text: str, font_number: int = 21) -> bool:
    fontcap = load_fontcap(font_number, fontcap_dir())

    for char in text:
        try:
            fontcap.glyph_for_ascii(ord(char))
        except PlotcharUnsupportedError:
            return False

    return True


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
    required = "ABCDabcd"
    if not has_glyphs(required, font_number=21):
        raise SystemExit("font21 lacks required ASCII case glyphs for this smoke")

    parsed = parse_textitem_plotchar_real_string(
        "~A~ab~U2~cd",
        func_code="~",
        default_font_number=21,
    )
    assert parsed.text == "ABCD"
    assert [segment.text for segment in parsed.segments] == ["AB", "CD"]

    parsed = parse_textitem_plotchar_real_string(
        "~A~AB~L2~CD",
        func_code="~",
        default_font_number=21,
    )
    assert parsed.text == "ABcd"
    assert [segment.text for segment in parsed.segments] == ["AB", "cd"]

    parsed = parse_textitem_plotchar_real_string(
        "~A~AB~L~CD",
        func_code="~",
        default_font_number=21,
    )
    assert parsed.text == "ABcd"

    parsed = parse_textitem_plotchar_real_string(
        "~A~ab~U0~cd",
        func_code="~",
        default_font_number=21,
    )
    assert parsed.text == "ABCD"

    lower = compute_real_string("~A~AB~L2~CD")
    upper = compute_real_string("~A~ab~U2~cd")
    indefinite = compute_real_string("~A~AB~L~CD")

    assert lower.text == "ABcd"
    assert upper.text == "ABCD"
    assert indefinite.text == "ABcd"

    assert lower.metrics.width > 0.0
    assert lower.metrics.height > 0.0
    assert upper.metrics.width > 0.0
    assert upper.metrics.height > 0.0
    assert indefinite.metrics.width > 0.0
    assert indefinite.metrics.height > 0.0

    print("✅ Python Plotchar U/L case function-code smoke passed")


if __name__ == "__main__":
    main()
