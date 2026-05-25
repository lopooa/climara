"""
Color table helpers for climara graphics.

The return type is a small Python object that stores normalized RGB triples.
Backends can convert it to their own native representation.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


RgbTriple = tuple[float, float, float]


@dataclass(frozen=True)
class HluColorMap:
    """Backend-neutral color table."""

    name: str
    colors: tuple[RgbTriple, ...]

    def __len__(self) -> int:
        return len(self.colors)

    def __iter__(self):
        return iter(self.colors)

    def __getitem__(self, item):
        return self.colors[item]

    def to_hex_list(self) -> list[str]:
        return [rgb_to_hex(value) for value in self.colors]


_BUILTIN_TABLES: dict[str, tuple[RgbTriple, ...]] = {
    "default": (
        (0.2667, 0.0039, 0.3294),
        (0.2824, 0.1400, 0.4575),
        (0.2539, 0.2653, 0.5296),
        (0.2068, 0.3718, 0.5531),
        (0.1636, 0.4711, 0.5581),
        (0.1276, 0.5669, 0.5506),
        (0.1347, 0.6586, 0.5176),
        (0.2669, 0.7488, 0.4406),
        (0.4775, 0.8214, 0.3182),
        (0.7414, 0.8734, 0.1496),
        (0.9932, 0.9062, 0.1439),
    ),
    "greys": (
        (0.0000, 0.0000, 0.0000),
        (0.2500, 0.2500, 0.2500),
        (0.5000, 0.5000, 0.5000),
        (0.7500, 0.7500, 0.7500),
        (1.0000, 1.0000, 1.0000),
    ),
}


def _clean_channel(value: float) -> float:
    value = float(value)
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value


def normalize_rgb(values: Sequence[float]) -> RgbTriple:
    """Normalize an RGB triple to the 0..1 range."""
    if len(values) < 3:
        raise ValueError("RGB values need at least three channels.")

    rgb = [float(values[0]), float(values[1]), float(values[2])]
    largest = sorted(abs(item) for item in rgb)[-1]
    if largest > 1.0:
        rgb = [item / 255.0 for item in rgb]
    return tuple(_clean_channel(item) for item in rgb)  # type: ignore[return-value]


def rgb_to_hex(values: Sequence[float]) -> str:
    """Convert an RGB triple to a CSS-style hex string."""
    red, green, blue = normalize_rgb(values)
    return "#{:02x}{:02x}{:02x}".format(
        round(red * 255.0),
        round(green * 255.0),
        round(blue * 255.0),
    )


def read_rgb_table(path: str | Path) -> list[RgbTriple]:
    """Read a simple NCL-style .rgb table."""
    table_path = Path(path)
    if not table_path.exists():
        raise FileNotFoundError(table_path)

    colors: list[RgbTriple] = []
    for raw_line in table_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith(";"):
            continue

        parts = line.replace(",", " ").split()
        if len(parts) < 3:
            continue

        try:
            values = [float(parts[0]), float(parts[1]), float(parts[2])]
        except ValueError:
            continue

        colors.append(normalize_rgb(values))

    if not colors:
        raise ValueError(f"No RGB rows were found in {table_path}.")
    return colors


def make_discrete_colormap(
    colors: Iterable[Sequence[float]],
    name: str = "climara_table",
) -> HluColorMap:
    """Create a backend-neutral color table from RGB triples."""
    values = tuple(normalize_rgb(item) for item in colors)
    if not values:
        raise ValueError("At least one RGB triple is required.")
    return HluColorMap(name=name, colors=values)


def read_rgb_colormap(path: str | Path, name: str | None = None) -> HluColorMap:
    """Read a color table from an .rgb file."""
    table_path = Path(path)
    cmap_name = name or table_path.stem
    return make_discrete_colormap(read_rgb_table(table_path), name=cmap_name)


def get_colormap(name: str | Path | HluColorMap | None = None) -> HluColorMap:
    """Return a backend-neutral color table."""
    if isinstance(name, HluColorMap):
        return name

    if name is None:
        return HluColorMap(name="default", colors=_BUILTIN_TABLES["default"])

    candidate = Path(str(name))
    if candidate.exists():
        return read_rgb_colormap(candidate)

    key = str(name).lower()
    if key not in _BUILTIN_TABLES:
        raise ValueError(f"Unknown climara color table: {name!r}")

    return HluColorMap(name=key, colors=_BUILTIN_TABLES[key])


resolve_colormap = get_colormap


__all__ = [
    "HluColorMap",
    "RgbTriple",
    "get_colormap",
    "make_discrete_colormap",
    "normalize_rgb",
    "read_rgb_colormap",
    "read_rgb_table",
    "resolve_colormap",
    "rgb_to_hex",
]
