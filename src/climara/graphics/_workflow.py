"""
Small workflow helpers for backend-neutral graphics objects.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping


def update_resources(target: Any, resources: Mapping[str, Any] | None = None, **kwargs: Any) -> Any:
    """Merge resources into an object when it exposes a resource dictionary."""
    merged: dict[str, Any] = {}
    if resources:
        merged.update(dict(resources))
    merged.update(kwargs)

    if hasattr(target, "resources") and isinstance(target.resources, dict):
        target.resources.update(merged)
    elif hasattr(target, "res") and isinstance(target.res, dict):
        target.res.update(merged)
    return target


def draw(target: Any) -> Any:
    """Return the object after asking it to draw itself when supported."""
    method = getattr(target, "draw", None)
    if callable(method):
        return method()
    return target


def refresh(target: Any) -> Any:
    """Compatibility helper for interactive workflows."""
    method = getattr(target, "refresh", None)
    if callable(method):
        return method()
    return target


def save(target: Any, path: str | Path | None = None, **kwargs: Any) -> Any:
    """Save or close a workstation-like object when supported."""
    if path is not None:
        destination = Path(path)
    else:
        destination = None

    if destination is not None and hasattr(target, "save"):
        return target.save(destination, **kwargs)
    if destination is not None and hasattr(target, "write"):
        return target.write(destination, **kwargs)
    if hasattr(target, "frame"):
        return target.frame()
    return target


def close(target: Any) -> Any:
    """Close a workstation-like object when supported."""
    method = getattr(target, "close", None)
    if callable(method):
        return method()
    return target


__all__ = [
    "close",
    "draw",
    "refresh",
    "save",
    "update_resources",
]
