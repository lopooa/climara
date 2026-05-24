from __future__ import annotations


def ncl_thickness_to_mpl(value):
    """Convert NCL gs*ThicknessF to temporary Matplotlib bridge linewidth.

    NCL thickness values are not the same as Matplotlib point widths.
    Keep the NCL resource value in objects, and only scale it in the
    current backend bridge.
    """
    value = float(value)

    if value <= 0:
        return 0.0

    return value * 0.28
