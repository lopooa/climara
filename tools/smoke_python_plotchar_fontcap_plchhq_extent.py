from __future__ import annotations

import os
from pathlib import Path

from climara.graphics._ncl_plotchar_textitem import build_ncl_plotchar_textitem_state
from climara.graphics._plotchar_fontcap import load_fontcap
from climara.graphics._plotchar_plchhq_extent import compute_plchhq_fontcap_text_extent
from climara.graphics._plotchar_state import (
    PlotcharStateError,
    PlotcharUnsupportedError,
    build_textitem_plotchar_state,
)
from climara.graphics._text_semantics import build_text_item_semantics


DEFAULT_FONT = 21
PREFERRED_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


def fontcap_dir() -> Path:
    explicit = os.environ.get("CLIMARA_PLOTCHAR_FONTCAP_DIR")
    if explicit:
        return Path(explicit)

    ncl_root = os.environ.get("NCL_SRC_ROOT")
    if not ncl_root:
        raise SystemExit("Set NCL_SRC_ROOT=/mnt/d/Projects/NCL or CLIMARA_PLOTCHAR_FONTCAP_DIR")

    return Path(ncl_root) / "common" / "src" / "fontcap"


def available_font_numbers() -> list[int]:
    root = fontcap_dir()
    out: list[int] = []

    for path in root.glob("font*.fc"):
        stem = path.stem
        try:
            out.append(int(stem.removeprefix("font")))
        except ValueError:
            continue

    return sorted(set(out))


def glyph_chars_for_font(font_number: int) -> set[str] | None:
    try:
        fontcap = load_fontcap(font_number, fontcap_dir())
    except (PlotcharStateError, PlotcharUnsupportedError, FileNotFoundError):
        return None

    chars: set[str] = set()

    for char in PREFERRED_CHARS:
        try:
            fontcap.glyph_for_ascii(ord(char))
        except PlotcharUnsupportedError:
            continue
        chars.add(char)

    return chars


def compatible_font_and_chars(min_count: int) -> tuple[int, str, bool]:
    default_chars = glyph_chars_for_font(DEFAULT_FONT)

    if not default_chars:
        raise SystemExit(
            f"SKIP: default font{DEFAULT_FONT} is not usable by the current fontcap parser."
        )

    for font_number in available_font_numbers():
        if font_number == DEFAULT_FONT:
            continue

        chars = glyph_chars_for_font(font_number)
        if not chars:
            continue

        common = default_chars & chars
        ordered = "".join(char for char in PREFERRED_CHARS if char in common)

        if len(ordered) >= min_count:
            return font_number, ordered[:min_count], True

    ordered_default = "".join(char for char in PREFERRED_CHARS if char in default_chars)

    if len(ordered_default) >= min_count:
        return DEFAULT_FONT, ordered_default[:min_count], False

    raise SystemExit(
        f"SKIP: font{DEFAULT_FONT} does not expose enough uppercase/digit glyphs for this smoke."
    )


def build_state(font: int = DEFAULT_FONT):
    semantics = build_text_item_semantics(
        "",
        func_code="~",
        font=font,
        font_height=0.04,
        font_aspect=2.0,
        font_quality="High",
        constant_spacing=0.0,
    )
    textitem_state = build_ncl_plotchar_textitem_state(semantics)
    state = build_textitem_plotchar_state(textitem_state)
    return textitem_state, state


def compute_real_string(chrs: str, font: int = DEFAULT_FONT):
    textitem_state, state = build_state(font=font)

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


def assert_raises(message_part: str, func):
    try:
        func()
    except PlotcharUnsupportedError as exc:
        message = str(exc)
        assert message_part in message, message
    else:
        raise AssertionError(f"Expected PlotcharUnsupportedError containing {message_part!r}")


def main():
    target_font, chars, used_secondary = compatible_font_and_chars(min_count=6)
    plain_body = chars[:4]

    plain = compute_real_string(f"~A~{plain_body}")
    assert plain.text == plain_body
    assert plain.glyph_count == len(plain_body)
    assert plain.metrics.width > 0.0
    assert plain.metrics.height > 0.0

    body1 = chars[:2]
    body2 = chars[2:4]
    body3 = chars[4:6]

    switched = compute_real_string(f"~A~{body1}~F{target_font}~{body2}")
    assert switched.text == body1 + body2
    assert switched.glyph_count == len(body1 + body2)
    assert switched.metrics.width > 0.0
    assert switched.metrics.height > 0.0

    script = compute_real_string(f"~A~{body1}~S~{body2}~E~{body3}")
    assert script.text == body1 + body2 + body3
    assert script.metrics.width > 0.0
    assert script.metrics.height > 0.0

    reset = compute_real_string(f"~A~{body1}~F{target_font}~{body2}~F~{body3}")
    assert reset.text == body1 + body2 + body3
    assert reset.glyph_count == len(body1 + body2 + body3)
    assert reset.metrics.width > 0.0
    assert reset.metrics.height > 0.0

    initial_down = compute_real_string(f"~D~{plain_body}")
    assert initial_down.text == plain_body
    assert initial_down.metrics.width > 0.0
    assert initial_down.metrics.height > 0.0

    assert_raises(
        "got command 'R'",
        lambda: compute_real_string(f"~A~{chars[0]}~R~{chars[1]}"),
    )

    assert_raises(
        "Unterminated inline Plotchar function-code sequence",
        lambda: compute_real_string(f"~A~{plain_body}~"),
    )

    if used_secondary:
        suffix = f"font{DEFAULT_FONT}, secondary font{target_font}"
    else:
        suffix = f"font{DEFAULT_FONT}, no compatible secondary fontcap found"

    print(f"✅ Python Plotchar fontcap PLCHHQ extent smoke passed ({suffix})")


if __name__ == "__main__":
    main()
