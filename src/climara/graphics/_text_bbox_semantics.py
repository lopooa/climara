from __future__ import annotations

from dataclasses import dataclass
from math import cos, radians, sin
from typing import Any

from ._plotchar_metrics import PlotcharExtentMetrics
from ._text_bbox import TextBBox, TextItemBBoxRequest, build_text_bbox


_EPS = 1.19209290e-7


@dataclass(frozen=True)
class TextBBoxCornerPoints:
    p0: tuple[float, float]
    p1: tuple[float, float]
    p2: tuple[float, float]
    p3: tuple[float, float]

    @property
    def points(self) -> tuple[tuple[float, float], ...]:
        return (self.p0, self.p1, self.p2, self.p3)


@dataclass(frozen=True)
class TextBBoxSemantics:
    bbox: TextBBox
    real_x: float
    real_y: float
    corners: TextBBoxCornerPoints
    sanitized_metrics: PlotcharExtentMetrics


def _sanitize_metric(value: float) -> float:
    out = float(value)
    if abs(out) > 10.0:
        return 0.0001
    return out


def sanitize_plotchar_metrics(
    metrics: PlotcharExtentMetrics,
) -> PlotcharExtentMetrics:
    dl = _sanitize_metric(metrics.dl)
    dr = _sanitize_metric(metrics.dr)
    db = _sanitize_metric(metrics.db)
    dt = _sanitize_metric(metrics.dt)

    if abs(dl + dr) < _EPS:
        dl = 0.0001
        dr = 0.0001

    if abs(db + dt) < _EPS:
        db = 0.0001
        dt = 0.0001

    return PlotcharExtentMetrics(
        dl=dl,
        dr=dr,
        db=db,
        dt=dt,
    )


def _just_key(value: Any) -> str:
    return str(value).strip().replace("_", "").replace("-", "").lower()


def text_real_position_from_plotchar_metrics(
    request: TextItemBBoxRequest,
    metrics: PlotcharExtentMetrics,
) -> tuple[float, float]:
    dl = metrics.dl
    dr = metrics.dr
    db = metrics.db
    dt = metrics.dt

    x = request.x
    y = request.y

    key = _just_key(request.semantics.just)

    if key in {"centerleft", "leftcenter"}:
        real_x = x + dl
        real_y = y - dt + 0.5 * (db + dt)
    elif key in {"centercenter", "centrecenter", "center", "centre"}:
        real_x = x + dl - 0.5 * (dl + dr)
        real_y = y - dt + 0.5 * (db + dt)
    elif key in {"centerright", "rightcenter"}:
        real_x = x - dr
        real_y = y - dt + 0.5 * (db + dt)

    elif key == "topleft":
        real_x = x + dl
        real_y = y - dt
    elif key in {"topcenter", "topcentre"}:
        real_x = x + dl - 0.5 * (dl + dr)
        real_y = y - dt
    elif key == "topright":
        real_x = x - dr
        real_y = y - dt

    elif key == "bottomleft":
        real_x = x + dl
        real_y = y + db
    elif key in {"bottomcenter", "bottomcentre"}:
        real_x = x + dl - 0.5 * (dl + dr)
        real_y = y + db
    elif key == "bottomright":
        real_x = x - dr
        real_y = y + db

    else:
        real_x = x + dl - 0.5 * (dl + dr)
        real_y = y - dt + 0.5 * (db + dt)

    return real_x, real_y


def _rotate_point(
    x: float,
    y: float,
    *,
    origin_x: float,
    origin_y: float,
    angle: float,
) -> tuple[float, float]:
    c = cos(radians(angle))
    s = sin(radians(angle))

    return (
        x * c + y * s + origin_x * (1.0 - c) - origin_y * s,
        -x * s + y * c + origin_y * (1.0 - c) + origin_x * s,
    )


def text_bbox_corners_from_plotchar_metrics(
    request: TextItemBBoxRequest,
    metrics: PlotcharExtentMetrics,
    *,
    perim_space: float = 0.0,
) -> TextBBoxCornerPoints:
    real_x, real_y = text_real_position_from_plotchar_metrics(request, metrics)

    space = float(perim_space)

    p0 = (
        real_x - metrics.dl - space,
        real_y - metrics.db - space,
    )
    p1 = (
        real_x - metrics.dl - space,
        real_y + metrics.dt + space,
    )
    p2 = (
        real_x + metrics.dr + space,
        real_y + metrics.dt + space,
    )
    p3 = (
        real_x + metrics.dr + space,
        real_y - metrics.db - space,
    )

    angle = float(request.semantics.angle)

    if abs(angle) < _EPS:
        return TextBBoxCornerPoints(p0=p0, p1=p1, p2=p2, p3=p3)

    return TextBBoxCornerPoints(
        p0=_rotate_point(p0[0], p0[1], origin_x=request.x, origin_y=request.y, angle=angle),
        p1=_rotate_point(p1[0], p1[1], origin_x=request.x, origin_y=request.y, angle=angle),
        p2=_rotate_point(p2[0], p2[1], origin_x=request.x, origin_y=request.y, angle=angle),
        p3=_rotate_point(p3[0], p3[1], origin_x=request.x, origin_y=request.y, angle=angle),
    )


def compute_text_bbox_from_plotchar_metrics(
    request: TextItemBBoxRequest,
    metrics: PlotcharExtentMetrics,
    *,
    perim_on: bool = False,
    background_fill_on: bool = False,
    perim_space: float = 0.0,
) -> TextBBoxSemantics:
    sanitized = sanitize_plotchar_metrics(metrics)

    if perim_on or background_fill_on:
        spacing = float(request.semantics.font_height) * float(perim_space)
    else:
        spacing = 0.0

    real_x, real_y = text_real_position_from_plotchar_metrics(
        request,
        sanitized,
    )

    corners = text_bbox_corners_from_plotchar_metrics(
        request,
        sanitized,
        perim_space=spacing,
    )

    xs = tuple(point[0] for point in corners.points)
    ys = tuple(point[1] for point in corners.points)

    bbox = build_text_bbox(
        l=min(xs),
        r=max(xs),
        b=min(ys),
        t=max(ys),
        coordinate_space=request.coordinate_space,
    )

    return TextBBoxSemantics(
        bbox=bbox,
        real_x=real_x,
        real_y=real_y,
        corners=corners,
        sanitized_metrics=sanitized,
    )


__all__ = [
    "TextBBoxCornerPoints",
    "TextBBoxSemantics",
    "compute_text_bbox_from_plotchar_metrics",
    "sanitize_plotchar_metrics",
    "text_bbox_corners_from_plotchar_metrics",
    "text_real_position_from_plotchar_metrics",
]
