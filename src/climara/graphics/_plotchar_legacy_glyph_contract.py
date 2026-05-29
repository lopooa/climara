from __future__ import annotations

import math

from ._plotchar_legacy_glyph_provider import LegacyGlyphResult
from ._plotchar_state import PlotcharUnsupportedError


def _finite_float(value, *, name: str) -> float:
    try:
        out = float(value)
    except Exception as exc:
        raise PlotcharUnsupportedError(
            f"Legacy glyph result {name} must be numeric, got {type(value).__name__}."
        ) from exc

    if not math.isfinite(out):
        raise PlotcharUnsupportedError(
            f"Legacy glyph result {name} must be finite, got {out!r}."
        )

    return out


def validate_legacy_glyph_result(result: LegacyGlyphResult) -> None:
    advance = _finite_float(result.advance, name="advance")
    dl = _finite_float(result.dl, name="dl")
    dr = _finite_float(result.dr, name="dr")
    db = _finite_float(result.db, name="db")
    dt = _finite_float(result.dt, name="dt")

    if advance <= 0.0:
        raise PlotcharUnsupportedError(
            f"Legacy glyph result advance must be positive, got {advance}."
        )

    for name, value in {
        "dl": dl,
        "dr": dr,
        "db": db,
        "dt": dt,
    }.items():
        if value < 0.0:
            raise PlotcharUnsupportedError(
                f"Legacy glyph result {name} must be non-negative, got {value}."
            )

    if not result.polylines:
        raise PlotcharUnsupportedError(
            "Legacy glyph result must contain at least one polyline."
        )

    for poly_index, poly in enumerate(result.polylines):
        if len(poly.points) < 2:
            raise PlotcharUnsupportedError(
                f"Legacy glyph polyline {poly_index} must contain at least two points."
            )

        for point_index, point in enumerate(poly.points):
            if len(point) != 2:
                raise PlotcharUnsupportedError(
                    f"Legacy glyph polyline {poly_index} point {point_index} must be a 2-tuple."
                )

            _finite_float(
                point[0],
                name=f"polyline[{poly_index}].point[{point_index}].x",
            )
            _finite_float(
                point[1],
                name=f"polyline[{poly_index}].point[{point_index}].y",
            )


__all__ = [
    "validate_legacy_glyph_result",
]
