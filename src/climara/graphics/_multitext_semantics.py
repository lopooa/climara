from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Iterator

from ._text_semantics import TextItemSemantics, build_text_item_semantics


@dataclass(frozen=True)
class MultiTextSemantics:
    items: tuple[TextItemSemantics, ...]

    def __len__(self) -> int:
        return len(self.items)

    def __iter__(self) -> Iterator[TextItemSemantics]:
        return iter(self.items)

    @property
    def texts(self) -> tuple[str, ...]:
        return tuple(item.text for item in self.items)

    @property
    def real_strings(self) -> tuple[str, ...]:
        return tuple(item.real_string for item in self.items)


def build_multitext_semantics(
    texts: Iterable[Any],
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
) -> MultiTextSemantics:
    return MultiTextSemantics(
        items=tuple(
            build_text_item_semantics(
                text,
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
            for text in texts
        )
    )


__all__ = [
    "MultiTextSemantics",
    "build_multitext_semantics",
]
