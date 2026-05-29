from __future__ import annotations

import math

from ._plotchar_state import PlotcharUnsupportedError


def _finite_float(value, *, name: str) -> float:
    try:
        out = float(value)
    except Exception as exc:
        raise PlotcharUnsupportedError(
            f"Plotchar draw-provider result {name} must be numeric, got {type(value).__name__}."
        ) from exc

    if not math.isfinite(out):
        raise PlotcharUnsupportedError(
            f"Plotchar draw-provider result {name} must be finite, got {out!r}."
        )

    return out


def _nonnegative_metric(value, *, name: str) -> float:
    out = _finite_float(value, name=name)

    if out < 0.0:
        raise PlotcharUnsupportedError(
            f"Plotchar draw-provider result {name} must be non-negative, got {out}."
        )

    return out


def validate_plotchar_draw_provider_result(result, *, label: str) -> None:
    metrics = getattr(result, "metrics", None)

    if metrics is None:
        raise PlotcharUnsupportedError(
            f"{label} draw-provider result must include metrics."
        )

    _nonnegative_metric(getattr(metrics, "dl", None), name=f"{label}.metrics.dl")
    _nonnegative_metric(getattr(metrics, "dr", None), name=f"{label}.metrics.dr")
    _nonnegative_metric(getattr(metrics, "db", None), name=f"{label}.metrics.db")
    _nonnegative_metric(getattr(metrics, "dt", None), name=f"{label}.metrics.dt")

    try:
        int(getattr(result, "font_number"))
    except Exception as exc:
        raise PlotcharUnsupportedError(
            f"{label} draw-provider result font_number must be convertible to int."
        ) from exc

    try:
        glyph_count = int(getattr(result, "glyph_count"))
    except Exception as exc:
        raise PlotcharUnsupportedError(
            f"{label} draw-provider result glyph_count must be convertible to int."
        ) from exc

    if glyph_count < 0:
        raise PlotcharUnsupportedError(
            f"{label} draw-provider result glyph_count must be non-negative, got {glyph_count}."
        )

    polylines = getattr(result, "polylines", None)

    if polylines is None:
        raise PlotcharUnsupportedError(
            f"{label} draw-provider result must include polylines."
        )

    for poly_index, poly in enumerate(polylines):
        points = getattr(poly, "points", None)

        if points is None:
            raise PlotcharUnsupportedError(
                f"{label} draw-provider polyline {poly_index} must include points."
            )

        if len(points) < 2:
            raise PlotcharUnsupportedError(
                f"{label} draw-provider polyline {poly_index} must contain at least two points."
            )

        for point_index, point in enumerate(points):
            if len(point) != 2:
                raise PlotcharUnsupportedError(
                    f"{label} draw-provider polyline {poly_index} point {point_index} must be a 2-tuple."
                )

            _finite_float(
                point[0],
                name=f"{label}.polyline[{poly_index}].point[{point_index}].x",
            )
            _finite_float(
                point[1],
                name=f"{label}.polyline[{poly_index}].point[{point_index}].y",
            )


__all__ = [
    "validate_plotchar_draw_provider_result",
]
