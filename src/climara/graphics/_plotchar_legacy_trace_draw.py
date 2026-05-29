from __future__ import annotations

from dataclasses import dataclass

from ._plotchar_greek_draw_provider import (
    GreekDrawPolyline,
    GreekDrawRequest,
    GreekDrawResult,
)
from ._plotchar_legacy_digitization_trace import trace_legacy_digitization_steps
from ._plotchar_legacy_glyph_provider import (
    LegacyGlyphProvider,
    LegacyGlyphRequest,
    validate_legacy_glyph_provider,
)
from ._plotchar_metrics import build_plotchar_extent_metrics


@dataclass(frozen=True)
class LegacyTraceDrawProvider:
    glyph_provider: LegacyGlyphProvider
    source_mapped: bool = True
    source_map_reference: str = "docs/ncl_plotchar_legacy_digitization_trace_source_map.md"

    def draw_for_request(self, request: GreekDrawRequest) -> GreekDrawResult:
        validate_legacy_glyph_provider(self.glyph_provider)

        steps = trace_legacy_digitization_steps(request.chrs, request.state)

        cursor_x = float(request.xpos)
        base_y = float(request.ypos)

        polylines: list[GreekDrawPolyline] = []

        dl = 0.0
        dr = 0.0
        db = 0.0
        dt = 0.0

        for step in steps:
            glyph = self.glyph_provider.glyph_for_step(
                LegacyGlyphRequest(
                    step=step,
                    size=float(request.size),
                    angle=float(request.angle),
                    cntr=float(request.cntr),
                )
            )

            for poly in glyph.polylines:
                shifted = tuple(
                    (cursor_x + x, base_y + y)
                    for x, y in poly.points
                )
                polylines.append(
                    GreekDrawPolyline(
                        points=shifted,
                        fillable=poly.fillable,
                    )
                )

            dl = max(dl, -0.0)
            dr = max(dr, cursor_x - float(request.xpos) + glyph.dr)
            db = max(db, glyph.db)
            dt = max(dt, glyph.dt)

            cursor_x += glyph.advance

        return GreekDrawResult(
            polylines=tuple(polylines),
            metrics=build_plotchar_extent_metrics(
                dl=dl,
                dr=dr,
                db=db,
                dt=dt,
            ),
            text="".join(step.char for step in steps),
            font_number=int(getattr(request.state, "nodf", 21)),
            glyph_count=len(steps),
        )


__all__ = [
    "LegacyTraceDrawProvider",
]
