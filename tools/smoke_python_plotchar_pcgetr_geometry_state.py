from __future__ import annotations

import os
from pathlib import Path

from climara.graphics._ncl_plotchar_textitem import build_ncl_plotchar_textitem_state
from climara.graphics._plotchar_plchhq_extent import compute_plchhq_fontcap_text_extent
from climara.graphics._plotchar_state import build_textitem_plotchar_state
from climara.graphics._text_semantics import build_text_item_semantics


def almost_equal(value, expected, tol=1e-12):
    assert abs(value - expected) <= tol, (value, expected)


def fontcap_dir() -> Path:
    explicit = os.environ.get("CLIMARA_PLOTCHAR_FONTCAP_DIR")
    if explicit:
        return Path(explicit)

    ncl_root = os.environ.get("NCL_SRC_ROOT")
    if not ncl_root:
        raise SystemExit("Set NCL_SRC_ROOT=/mnt/d/Projects/NCL or CLIMARA_PLOTCHAR_FONTCAP_DIR")

    return Path(ncl_root) / "common" / "src" / "fontcap"


def compute_for_text(text: str):
    semantics = build_text_item_semantics(
        text,
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
        chrs=semantics.real_string,
        state=state,
        xpos=0.5,
        ypos=0.5,
        size=textitem_state.real_size,
        angle=360.0,
        cntr=-1.0,
        fontcap_dir=fontcap_dir(),
    )


def main():
    result = compute_for_text("ABC")
    state = result.state

    almost_equal(state.pcgetr("XB"), state.xbeg)
    almost_equal(state.pcgetr("XC"), state.xcen)
    almost_equal(state.pcgetr("XE"), state.xend)
    almost_equal(state.pcgetr("YB"), state.ybeg)
    almost_equal(state.pcgetr("YC"), state.ycen)
    almost_equal(state.pcgetr("YE"), state.yend)

    almost_equal(state.pcgetr("XB"), 0.5)
    almost_equal(state.pcgetr("YB"), 0.5)

    assert state.pcgetr("XE") > state.pcgetr("XB")
    assert state.pcgetr("XC") >= state.pcgetr("XB")
    assert state.pcgetr("XC") <= state.pcgetr("XE")

    almost_equal(state.pcgetr("YC"), 0.5)
    almost_equal(state.pcgetr("YE"), 0.5)

    empty = compute_for_text("")
    empty_state = empty.state

    almost_equal(empty.metrics.width, 0.0)
    almost_equal(empty.metrics.height, 0.0)
    almost_equal(empty_state.pcgetr("XB"), 0.5)
    almost_equal(empty_state.pcgetr("YB"), 0.5)
    almost_equal(empty_state.pcgetr("XE"), 0.5)
    almost_equal(empty_state.pcgetr("YE"), 0.5)

    print("✅ Python Plotchar PCGETR geometry state smoke passed")


if __name__ == "__main__":
    main()
