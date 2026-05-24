from __future__ import annotations

from functools import lru_cache
from importlib.resources import files
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, ListedColormap


def ncl_color_to_mpl(value):
    """Convert common NCL color names to Matplotlib-compatible colors.

    Examples
    --------
    gray42 -> "0.42"
    grey70 -> "0.7"
    transparent -> "none"
    """
    if value is None:
        return None

    if isinstance(value, (tuple, list)):
        return value

    text = str(value).strip()
    key = text.replace("_", "").replace("-", "").replace(" ", "").lower()

    if key in ["none", "transparent", "no", "false", "off"]:
        return "none"

    for prefix in ["gray", "grey"]:
        if not key.startswith(prefix):
            continue

        number = key[len(prefix):]

        try:
            gray = float(number)
        except ValueError:
            continue

        if gray > 1.0:
            gray = gray / 100.0

        gray = min(max(gray, 0.0), 1.0)

        return f"{gray:g}"

    return text


def _parse_rgb_line(line: str):
    line = line.strip()

    if not line or line.startswith("#") or line.startswith(";"):
        return None

    if "=" in line:
        return None

    parts = line.replace(",", " ").split()

    if len(parts) < 3:
        return None

    try:
        rgb = [float(parts[0]), float(parts[1]), float(parts[2])]
    except ValueError:
        return None

    if max(rgb) > 1.0:
        rgb = [v / 255.0 for v in rgb]

    rgb = [min(max(v, 0.0), 1.0) for v in rgb]

    return rgb


def read_rgb_colormap(path: str | Path, name: str | None = None, listed: bool = True):
    path = Path(path)
    colors = []

    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            rgb = _parse_rgb_line(line)
            if rgb is not None:
                colors.append(rgb)

    if not colors:
        raise ValueError(f"No RGB colors found in {path}")

    if name is None:
        name = path.stem

    if listed:
        return ListedColormap(colors, name=name)

    return LinearSegmentedColormap.from_list(name, colors)


@lru_cache(maxsize=128)
def _get_package_rgb_path(name: str):
    resource_dir = files("climara").joinpath("resources", "colormaps")
    rgb_path = resource_dir.joinpath(f"{name}.rgb")

    if rgb_path.is_file():
        return rgb_path

    return None


def get_colormap(name=None):
    if name is None:
        return plt.get_cmap("viridis")

    path = Path(str(name))

    if path.is_file():
        return read_rgb_colormap(path)

    rgb_path = _get_package_rgb_path(str(name))

    if rgb_path is not None:
        return read_rgb_colormap(rgb_path, name=str(name))

    return plt.get_cmap(str(name))


def list_builtin_colormaps():
    resource_dir = files("climara").joinpath("resources", "colormaps")
    names = []

    for item in resource_dir.iterdir():
        if item.name.endswith(".rgb"):
            names.append(item.name[:-4])

    return sorted(names)
