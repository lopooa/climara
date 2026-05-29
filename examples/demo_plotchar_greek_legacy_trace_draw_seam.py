from pathlib import Path

from climara.graphics._plotchar_greek_draw_provider import GreekDrawRequest
from climara.graphics._plotchar_legacy_glyph_provider import (
    LegacyGlyphPolyline,
    LegacyGlyphResult,
)
from climara.graphics._plotchar_legacy_trace_draw import LegacyTraceDrawProvider
from climara.graphics._plotchar_state import PlotcharState, PlotcharUnsupportedError
from climara.graphics._plotchar_svg_runtime import render_plchhq_real_string_to_ndc_polylines
from climara.graphics._primitive import HluPrimitive, build_polyline
from climara.graphics._render_svg import save_svg


class DemoSourceMappedLegacyGlyphProvider:
    source_mapped = True
    source_map_reference = "docs/ncl_plotchar_legacy_digitization_source_map.md"

    def __init__(self):
        self.steps = []

    def glyph_for_step(self, request):
        self.steps.append(request.step)

        # Deliberately simple demo glyph. This is not NCL digitization output.
        width = 0.035
        height = 0.055

        return LegacyGlyphResult(
            polylines=(
                LegacyGlyphPolyline(
                    points=(
                        (0.0, 0.0),
                        (width * 0.5, height),
                        (width, 0.0),
                    )
                ),
                LegacyGlyphPolyline(
                    points=(
                        (width * 0.25, height * 0.35),
                        (width * 0.75, height * 0.35),
                    )
                ),
            ),
            advance=width * 1.25,
            dl=0.0,
            dr=width,
            db=0.0,
            dt=height,
        )


class BadLegacyGlyphProvider:
    source_mapped = False
    source_map_reference = ""

    def glyph_for_step(self, request):
        raise AssertionError("bad provider should not be called")


def state():
    out = PlotcharState.defaults()
    out.pcseti("TE", 1)
    out.pcseti("QU", 0)
    out.pcseti("FN", 21)
    out.pcseti("MA", 0)
    return out


def real_string(st, body):
    code = chr(st.nfcc) if st.nfcc >= 0 else ":"
    return f"{code}A{code}{body}"


def add_result(root, result):
    for poly in result.polylines:
        xs = [point[0] for point in poly.points]
        ys = [point[1] for point in poly.points]
        root.add_child(
            build_polyline(
                xs,
                ys,
                resources={"gsLineColor": "black", "gsLineThicknessF": 1.2},
            )
        )


def main():
    st = state()
    code = chr(st.nfcc) if st.nfcc >= 0 else ":"
    body = f"A{code}G{code}BC{code}R{code}D"

    good_glyph_provider = DemoSourceMappedLegacyGlyphProvider()
    greek_provider = LegacyTraceDrawProvider(
        glyph_provider=good_glyph_provider,
    )

    result = render_plchhq_real_string_to_ndc_polylines(
        chrs=real_string(st, body),
        state=st,
        xpos=0.12,
        ypos=0.45,
        size=0.035,
        angle=360.0,
        cntr=-1.0,
        greek_draw_provider=greek_provider,
    )

    if not good_glyph_provider.steps:
        raise AssertionError("legacy glyph provider did not receive traced steps")

    print("traced steps:")
    for step in good_glyph_provider.steps:
        print(
            f"  {step.char!r} font={step.font_family} "
            f"size={step.size_level} case={step.case_mode} INDA={step.inda_index}"
        )

    try:
        bad_provider = LegacyTraceDrawProvider(
            glyph_provider=BadLegacyGlyphProvider(),
        )
        bad_provider.draw_for_request(
            GreekDrawRequest(
                chrs=real_string(st, body),
                state=st,
                xpos=0.12,
                ypos=0.45,
                size=0.035,
                angle=360.0,
                cntr=-1.0,
            )
        )
    except PlotcharUnsupportedError as exc:
        print("bad legacy glyph provider guarded:", exc)
    else:
        raise AssertionError("non-source-mapped legacy glyph provider should be guarded")

    root = HluPrimitive()
    add_result(root, result)

    out = Path("outputs/figures/demo_plotchar_greek_legacy_trace_draw_seam.svg")
    save_svg(root, out, width=900, height=360, background="white")

    print("result text:", result.text)
    print("result metrics:", result.metrics)
    print(f"wrote {out}")
    print("✅ Greek legacy trace draw seam demo passed")


if __name__ == "__main__":
    main()
