from __future__ import annotations

from dataclasses import dataclass
from typing import Any


TEXT_DIRECTION_ACROSS = "Across"
TEXT_DIRECTION_DOWN = "Down"

TEXT_JUST_BOTTOM_LEFT = "BottomLeft"
TEXT_JUST_BOTTOM_CENTER = "BottomCenter"
TEXT_JUST_BOTTOM_RIGHT = "BottomRight"
TEXT_JUST_CENTER_LEFT = "CenterLeft"
TEXT_JUST_CENTER_CENTER = "CenterCenter"
TEXT_JUST_CENTER_RIGHT = "CenterRight"
TEXT_JUST_TOP_LEFT = "TopLeft"
TEXT_JUST_TOP_CENTER = "TopCenter"
TEXT_JUST_TOP_RIGHT = "TopRight"

TEXT_QUALITY_HIGH = "High"
TEXT_QUALITY_MEDIUM = "Medium"
TEXT_QUALITY_LOW = "Low"
TEXT_QUALITY_WORKSTATION = "Workstation"

TEXT_QUALITY_INDEX = {
    TEXT_QUALITY_HIGH: 0,
    TEXT_QUALITY_MEDIUM: 1,
    TEXT_QUALITY_LOW: 2,
    TEXT_QUALITY_WORKSTATION: 3,
}


def _norm_key(value: Any) -> str:
    return str(value).strip().lower().replace("_", "")


def normalize_text_direction(value: Any | None) -> str:
    if value is None:
        return TEXT_DIRECTION_ACROSS

    aliases = {
        "across": TEXT_DIRECTION_ACROSS,
        "nhlacross": TEXT_DIRECTION_ACROSS,
        "down": TEXT_DIRECTION_DOWN,
        "nhldown": TEXT_DIRECTION_DOWN,
    }

    key = _norm_key(value)
    if key not in aliases:
        raise ValueError(f"Unsupported TextItem direction: {value!r}")

    return aliases[key]


def normalize_text_just(value: Any | None) -> str:
    if value is None:
        return TEXT_JUST_CENTER_CENTER

    aliases = {
        "bottomleft": TEXT_JUST_BOTTOM_LEFT,
        "bottomcenter": TEXT_JUST_BOTTOM_CENTER,
        "bottomright": TEXT_JUST_BOTTOM_RIGHT,
        "centerleft": TEXT_JUST_CENTER_LEFT,
        "centercenter": TEXT_JUST_CENTER_CENTER,
        "centerright": TEXT_JUST_CENTER_RIGHT,
        "topleft": TEXT_JUST_TOP_LEFT,
        "topcenter": TEXT_JUST_TOP_CENTER,
        "topright": TEXT_JUST_TOP_RIGHT,
        "nhlbottomleft": TEXT_JUST_BOTTOM_LEFT,
        "nhlbottomcenter": TEXT_JUST_BOTTOM_CENTER,
        "nhlbottomright": TEXT_JUST_BOTTOM_RIGHT,
        "nhlcenterleft": TEXT_JUST_CENTER_LEFT,
        "nhlcentercenter": TEXT_JUST_CENTER_CENTER,
        "nhlcenterright": TEXT_JUST_CENTER_RIGHT,
        "nhltopleft": TEXT_JUST_TOP_LEFT,
        "nhltopcenter": TEXT_JUST_TOP_CENTER,
        "nhltopright": TEXT_JUST_TOP_RIGHT,
    }

    key = _norm_key(value)
    if key not in aliases:
        raise ValueError(f"Unsupported TextItem justification: {value!r}")

    return aliases[key]


def normalize_text_quality(value: Any | None) -> str:
    if value is None:
        return TEXT_QUALITY_HIGH

    aliases = {
        "high": TEXT_QUALITY_HIGH,
        "nhlhigh": TEXT_QUALITY_HIGH,
        "medium": TEXT_QUALITY_MEDIUM,
        "nhlmedium": TEXT_QUALITY_MEDIUM,
        "low": TEXT_QUALITY_LOW,
        "nhllow": TEXT_QUALITY_LOW,
        "workstation": TEXT_QUALITY_WORKSTATION,
        "nhlworkstation": TEXT_QUALITY_WORKSTATION,
    }

    key = _norm_key(value)
    if key not in aliases:
        raise ValueError(f"Unsupported TextItem font quality: {value!r}")

    return aliases[key]


def text_quality_index(value: Any | None) -> int:
    return TEXT_QUALITY_INDEX[normalize_text_quality(value)]


def normalize_func_code(value: Any | None) -> str:
    if value is None:
        return "~"

    out = str(value)
    if not out:
        return "~"

    return out[0]


def normalize_text_angle(value: Any | None, default: float = 0.0) -> float:
    if value is None:
        angle = default
    else:
        angle = float(value)

    if angle < 0.0:
        angle = angle + 360.0

    return angle


def non_negative_text_float(value: Any | None, default: float) -> float:
    if value is None:
        out = default
    else:
        out = float(value)

    if out < 0.0:
        return 0.0

    return out


def text_real_string(text: Any, direction: Any | None = None, func_code: Any | None = None) -> str:
    normalized_direction = normalize_text_direction(direction)
    code = normalize_func_code(func_code)

    if normalized_direction == TEXT_DIRECTION_DOWN:
        direction_code = "D"
    else:
        direction_code = "A"

    return f"{code}{direction_code}{code}{str(text)}"


def text_uses_func_code(text: Any, func_code: Any | None = None) -> bool:
    code = normalize_func_code(func_code)
    return code in str(text)


@dataclass(frozen=True)
class TextItemSemantics:
    text: str
    direction: str
    real_string: str
    func_code: str
    just: str
    angle: float
    font: Any
    font_color: Any
    font_height: float
    font_aspect: float
    font_thickness: float
    font_quality: str
    quality_index: int
    constant_spacing: float


def plotchar_real_size_from_text_semantics(semantics: TextItemSemantics) -> float:
    aspect = float(semantics.font_aspect)
    if aspect <= 0.0:
        aspect = 1.3125

    return 1.0 / aspect * float(semantics.font_height) * 1.125


def build_text_item_semantics(
    text: Any,
    *,
    direction: Any | None = None,
    func_code: Any | None = None,
    just: Any | None = None,
    angle: Any | None = None,
    font: Any = 21,
    font_color: Any = "Foreground",
    font_height: Any = 0.025,
    font_aspect: Any = 1.3125,
    font_thickness: Any = 1.0,
    font_quality: Any = "High",
    constant_spacing: Any = 0.0,
) -> TextItemSemantics:
    normalized_text = str(text)
    normalized_direction = normalize_text_direction(direction)
    normalized_func_code = normalize_func_code(func_code)
    normalized_quality = normalize_text_quality(font_quality)

    return TextItemSemantics(
        text=normalized_text,
        direction=normalized_direction,
        real_string=text_real_string(
            normalized_text,
            direction=normalized_direction,
            func_code=normalized_func_code,
        ),
        func_code=normalized_func_code,
        just=normalize_text_just(just),
        angle=normalize_text_angle(angle),
        font=font,
        font_color=font_color,
        font_height=non_negative_text_float(font_height, 0.025),
        font_aspect=float(font_aspect),
        font_thickness=float(font_thickness),
        font_quality=normalized_quality,
        quality_index=text_quality_index(normalized_quality),
        constant_spacing=non_negative_text_float(constant_spacing, 0.0),
    )


__all__ = [
    "TEXT_DIRECTION_ACROSS",
    "TEXT_DIRECTION_DOWN",
    "TEXT_JUST_BOTTOM_LEFT",
    "TEXT_JUST_BOTTOM_CENTER",
    "TEXT_JUST_BOTTOM_RIGHT",
    "TEXT_JUST_CENTER_LEFT",
    "TEXT_JUST_CENTER_CENTER",
    "TEXT_JUST_CENTER_RIGHT",
    "TEXT_JUST_TOP_LEFT",
    "TEXT_JUST_TOP_CENTER",
    "TEXT_JUST_TOP_RIGHT",
    "TEXT_QUALITY_HIGH",
    "TEXT_QUALITY_MEDIUM",
    "TEXT_QUALITY_LOW",
    "TEXT_QUALITY_WORKSTATION",
    "TEXT_QUALITY_INDEX",
    "TextItemSemantics",
    "build_text_item_semantics",
    "normalize_func_code",
    "normalize_text_angle",
    "normalize_text_direction",
    "normalize_text_just",
    "normalize_text_quality",
    "plotchar_real_size_from_text_semantics",
    "non_negative_text_float",
    "text_quality_index",
    "text_real_string",
    "text_uses_func_code",
]
