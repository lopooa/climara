"""
NCL-style resource defaults for climara graphics.

This module keeps style settings as plain Python dictionaries. It does not
touch any drawing backend. Rendering backends may read these resources later.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping


_DEFAULT_STYLE: dict[str, Any] = {
    "wkBackgroundColor": "white",
    "wkForegroundColor": "black",
    "gsnFrame": True,
    "gsnDraw": True,
    "txFont": "helvetica",
    "txFontHeightF": 0.014,
    "txFontColor": "black",
    "gsnLeftStringFontHeightF": 0.014,
    "gsnCenterStringFontHeightF": 0.014,
    "gsnRightStringFontHeightF": 0.014,
    "lbLabelFontHeightF": 0.012,
    "lbTitleFontHeightF": 0.012,
    "tmLabelFontHeightF": 0.011,
}


_ACTIVE_STYLE: dict[str, Any] = deepcopy(_DEFAULT_STYLE)


def get_default_style() -> dict[str, Any]:
    """Return a copy of the package default graphics resources."""
    return deepcopy(_DEFAULT_STYLE)


def get_active_style() -> dict[str, Any]:
    """Return a copy of the active graphics resources."""
    return deepcopy(_ACTIVE_STYLE)


def set_style(resources: Mapping[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
    """Merge resources into the active style and return the result."""
    if resources:
        _ACTIVE_STYLE.update(dict(resources))
    if kwargs:
        _ACTIVE_STYLE.update(kwargs)
    return get_active_style()


def reset_style() -> dict[str, Any]:
    """Reset active graphics resources to package defaults."""
    _ACTIVE_STYLE.clear()
    _ACTIVE_STYLE.update(deepcopy(_DEFAULT_STYLE))
    return get_active_style()


def ncl_style(resources: Mapping[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
    """Activate climara's NCL-like default resources."""
    reset_style()
    return set_style(resources, **kwargs)


def apply_style(resources: Mapping[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
    """Compatibility alias for :func:`set_style`."""
    return set_style(resources, **kwargs)


__all__ = [
    "apply_style",
    "get_active_style",
    "get_default_style",
    "ncl_style",
    "reset_style",
    "set_style",
]
