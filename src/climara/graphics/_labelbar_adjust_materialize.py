from __future__ import annotations

from dataclasses import dataclass, replace
from math import isfinite
from typing import Any

from ._labelbar_adjust import LabelBarAdjustGeometryResult
from ._labelbar_geometry import (
    LabelBarGeometry,
    NdcTextItemSpec,
    NdcTextPlacement,
)
from ._text_bbox import TextBBox


@dataclass(frozen=True)
class LabelBarAdjustedGeometry:
    source_geometry: LabelBarGeometry
    external_view_bbox: TextBBox
    nominal_perim_bbox: TextBBox
    adjusted_bar_bbox: TextBBox
    adjusted_label_bbox: TextBBox | None
    adjusted_title_bbox: TextBBox | None
    final_box_locs: tuple[float, ...]
    final_label_locs: tuple[float, ...]
    final_label_const_pos: float | None
    final_label_text_positions: tuple[NdcTextPlacement, ...]
    final_title_text_position: NdcTextPlacement | None
    final_title_text_item: NdcTextItemSpec | None
    final_title_x: float | None
    final_title_y: float | None
    x_offset: float
    y_offset: float
    major_offset: float
    minor_offset: float


def _key(value: Any) -> str:
    return str(value).strip().replace("_", "").replace("-", "").lower()


def _finite(value: float) -> float:
    out = float(value)
    if not isfinite(out):
        raise ValueError("LabelBar adjusted geometry materialization requires finite values")
    return out


def _assert_bbox(box: TextBBox | None) -> None:
    if box is None:
        return
    for value in (box.l, box.r, box.b, box.t, box.width, box.height):
        _finite(value)


def _materialize_label_positions(
    geometry: LabelBarGeometry,
    *,
    final_label_locs: tuple[float, ...],
    final_label_const_pos: float | None,
) -> tuple[NdcTextPlacement, ...]:
    if not geometry.label_text_positions:
        return ()

    const_pos = (
        geometry.label_const_pos
        if final_label_const_pos is None
        else final_label_const_pos
    )

    orientation = _key(geometry.multi_text_orientation)

    if len(final_label_locs) != len(geometry.label_text_positions):
        raise ValueError(
            "LabelBar adjusted label_locs count must match existing label text positions"
        )

    out = []
    for loc, old in zip(final_label_locs, geometry.label_text_positions):
        if orientation in {"yconst", "nhlmtextyconst"}:
            out.append(
                NdcTextPlacement(
                    x=_finite(loc),
                    y=_finite(const_pos),
                    text=old.text,
                )
            )
        elif orientation in {"xconst", "nhlmtextxconst"}:
            out.append(
                NdcTextPlacement(
                    x=_finite(const_pos),
                    y=_finite(loc),
                    text=old.text,
                )
            )
        else:
            raise ValueError(f"Unsupported MultiText orientation: {geometry.multi_text_orientation!r}")

    return tuple(out)


def _materialize_title_position(
    geometry: LabelBarGeometry,
    *,
    final_title_x: float | None,
    final_title_y: float | None,
) -> NdcTextPlacement | None:
    if geometry.title_text_position is None:
        return None

    if final_title_x is None or final_title_y is None:
        return geometry.title_text_position

    return NdcTextPlacement(
        x=_finite(final_title_x),
        y=_finite(final_title_y),
        text=geometry.title_text_position.text,
    )


def _materialize_title_item(
    geometry: LabelBarGeometry,
    title_position: NdcTextPlacement | None,
) -> NdcTextItemSpec | None:
    if geometry.title_text_item is None or title_position is None:
        return None

    return replace(
        geometry.title_text_item,
        x=title_position.x,
        y=title_position.y,
    )


def materialize_labelbar_adjusted_geometry(
    result: LabelBarAdjustGeometryResult,
) -> LabelBarAdjustedGeometry:
    geometry = result.request.geometry

    if not isinstance(geometry, LabelBarGeometry):
        raise TypeError("Expected LabelBarGeometry in LabelBarAdjustGeometryResult")

    writeback = result.writeback_semantics
    perimeter = writeback.perimeter_semantics

    final_label_positions = _materialize_label_positions(
        geometry,
        final_label_locs=result.final_label_locs,
        final_label_const_pos=result.final_label_const_pos,
    )

    final_title_position = _materialize_title_position(
        geometry,
        final_title_x=result.final_title_x,
        final_title_y=result.final_title_y,
    )

    final_title_item = _materialize_title_item(
        geometry,
        final_title_position,
    )

    for value in (
        *result.final_box_locs,
        *result.final_label_locs,
        result.x_offset,
        result.y_offset,
        result.major_offset,
        result.minor_offset,
    ):
        _finite(value)

    if result.final_label_const_pos is not None:
        _finite(result.final_label_const_pos)
    if result.final_title_x is not None:
        _finite(result.final_title_x)
    if result.final_title_y is not None:
        _finite(result.final_title_y)

    for box in (
        result.final_view_bbox,
        perimeter.nominal_perim_bbox,
        result.final_adjusted_bar_bbox,
        result.final_adjusted_label_bbox,
        result.final_adjusted_title_bbox,
    ):
        _assert_bbox(box)

    return LabelBarAdjustedGeometry(
        source_geometry=geometry,
        external_view_bbox=result.final_view_bbox,
        nominal_perim_bbox=perimeter.nominal_perim_bbox,
        adjusted_bar_bbox=result.final_adjusted_bar_bbox,
        adjusted_label_bbox=result.final_adjusted_label_bbox,
        adjusted_title_bbox=result.final_adjusted_title_bbox,
        final_box_locs=result.final_box_locs,
        final_label_locs=result.final_label_locs,
        final_label_const_pos=result.final_label_const_pos,
        final_label_text_positions=final_label_positions,
        final_title_text_position=final_title_position,
        final_title_text_item=final_title_item,
        final_title_x=result.final_title_x,
        final_title_y=result.final_title_y,
        x_offset=result.x_offset,
        y_offset=result.y_offset,
        major_offset=result.major_offset,
        minor_offset=result.minor_offset,
    )


__all__ = [
    "LabelBarAdjustedGeometry",
    "materialize_labelbar_adjusted_geometry",
]
