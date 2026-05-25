"""
NCL-style workstation object.

Only SVG output is implemented for now. The object stores HLU/GSN-style
children and writes them through the SVG renderer when frame() is called.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
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


def _as_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


@dataclass
class NclWorkstation:
    """Backend-neutral NCL/HLU-style workstation."""

    wks_type: str = "svg"
    name: str = "climara"
    resources: dict[str, Any] = field(default_factory=dict)
    children: list[Any] = field(default_factory=list)
    frame_count: int = 0
    last_output: Path | None = None

    def add_child(self, child: Any):
        self.children.append(child)
        return child

    def add_plot(self, plot: Any):
        return self.add_child(plot)

    def set_values(
        self,
        resources: Mapping[str, Any] | None = None,
        **kwargs: Any,
    ):
        self.resources.update(_merge_resources(resources, **kwargs))
        return self

    def draw(self):
        self.resources["drawn"] = True
        return self

    def clear(self):
        self.children.clear()
        return self

    def _output_path(self, path: str | Path | None = None) -> Path:
        if path is not None:
            output = Path(path)
        else:
            base = Path(self.name)
            if base.suffix.lower() == ".svg":
                if self.frame_count == 0:
                    output = base
                else:
                    output = base.with_name(f"{base.stem}_{self.frame_count + 1:03d}.svg")
            else:
                if self.frame_count == 0:
                    output = base.with_suffix(".svg")
                else:
                    output = base.with_name(f"{base.name}_{self.frame_count + 1:03d}.svg")

        if output.suffix.lower() != ".svg":
            output = output.with_suffix(".svg")

        return output

    def frame(
        self,
        path: str | Path | None = None,
        width: int | None = None,
        height: int | None = None,
        background: str | None = None,
        clear: bool | None = None,
    ) -> Path:
        """Write the current workstation contents to one SVG frame."""

        wks_type = str(self.wks_type).lower()
        if wks_type != "svg":
            raise NotImplementedError(
                f"Only SVG workstation output is implemented now, got {self.wks_type!r}."
            )

        from ._render_svg import save_svg

        output = self._output_path(path)
        width_value = _as_int(width if width is not None else self.resources.get("wkWidth"), 1000)
        height_value = _as_int(height if height is not None else self.resources.get("wkHeight"), 800)
        background_value = background
        if background_value is None:
            background_value = self.resources.get("wkBackgroundColor", "white")

        save_svg(
            self,
            output,
            width=width_value,
            height=height_value,
            background=background_value,
        )

        self.frame_count += 1
        self.last_output = output

        clear_after = clear
        if clear_after is None:
            clear_after = bool(self.resources.get("wkClearAfterFrame", False))

        if clear_after:
            self.clear()

        return output

    def save(self, path: str | Path | None = None, **kwargs: Any) -> Path:
        """Alias for frame()."""

        return self.frame(path=path, **kwargs)

    def close(self):
        """Compatibility no-op."""

        self.resources["closed"] = True
        return self


def gsn_open_wks(
    wks_type: str,
    name: str | Path,
    resources: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> NclWorkstation:
    """Open an NCL-style workstation."""

    res = _merge_resources(resources, **kwargs)
    return NclWorkstation(
        wks_type=str(wks_type),
        name=str(name),
        resources=res,
    )


def frame(
    wks: NclWorkstation,
    path: str | Path | None = None,
    **kwargs: Any,
) -> Path:
    """Advance one frame on a workstation."""

    if not hasattr(wks, "frame"):
        raise TypeError("frame() expects a workstation-like object.")
    return wks.frame(path=path, **kwargs)


def open_wks(
    wks_type: str,
    name: str | Path,
    resources: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> NclWorkstation:
    """Compatibility alias for gsn_open_wks()."""

    return gsn_open_wks(wks_type, name, resources, **kwargs)


__all__ = [
    "NclWorkstation",
    "frame",
    "gsn_open_wks",
    "open_wks",
]
