"""
Removed legacy renderer module.

climara graphics now uses backend-neutral HLU/GSN objects and the SVG renderer.
"""

from __future__ import annotations


def render(*args, **kwargs):
    raise RuntimeError("Legacy renderer module has been removed from climara.")


def save(*args, **kwargs):
    raise RuntimeError("Legacy renderer module has been removed from climara.")


__all__ = [
    "render",
    "save",
]
