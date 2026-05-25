"""
HLU-style text item.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


def _merge_resources(
    resources: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    out: dict[str, Any] = {}
    if resources:
        out.update(dict(resources))
    out.update(kwargs)
    return out


@dataclass(init=False)
class HluTextItem:
    """Backend-neutral text item in normalized device coordinates."""

    text: str
    x: float
    y: float
    resources: dict[str, Any]
    children: list[Any]
    coordinate_system: str

    def __init__(
        self,
        text: str | None = None,
        x: float | None = None,
        y: float | None = None,
        resources: Mapping[str, Any] | None = None,
        **kwargs: Any,
    ):
        res = _merge_resources(resources)

        if text is None:
            text = kwargs.pop("string", kwargs.pop("txString", ""))

        if x is None:
            x = kwargs.pop("xpos", kwargs.pop("txPosXF", 0.5))

        if y is None:
            y = kwargs.pop("ypos", kwargs.pop("txPosYF", 0.5))

        extra_resources = kwargs.pop("res", None)
        if isinstance(extra_resources, Mapping):
            res.update(dict(extra_resources))

        res.update(kwargs)

        self.text = str(text)
        self.x = float(x)
        self.y = float(y)
        self.resources = res
        self.children = []
        self.coordinate_system = str(res.get("coordinate_system", "ndc"))

    @property
    def string(self) -> str:
        return self.text

    @string.setter
    def string(self, value: Any) -> None:
        self.text = str(value)

    def set_values(
        self,
        resources: Mapping[str, Any] | None = None,
        **kwargs: Any,
    ):
        self.resources.update(_merge_resources(resources, **kwargs))
        return self

    def add_child(self, child: Any):
        self.children.append(child)
        return child


def build_text_item(
    text: str,
    x: float,
    y: float,
    resources: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> HluTextItem:
    """Build a backend-neutral text item."""

    return HluTextItem(text=text, x=x, y=y, resources=resources, **kwargs)


__all__ = [
    "HluTextItem",
    "build_text_item",
]
