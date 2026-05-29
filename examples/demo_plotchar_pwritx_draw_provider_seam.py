from pathlib import Path

from climara.graphics._plotchar_metrics import build_plotchar_extent_metrics
from climara.graphics._plotchar_pwritx_draw_provider import (
    PwritxDrawPolyline,
    PwritxDrawResult,
)
from climara.graphics._plotchar_state import PlotcharState, PlotcharUnsupportedError
from climara.graphics._plotchar_svg_runtime import render_plchhq_real_string_to_ndc_polylines
from climara.graphics._primitive import HluPrimitive, build_polyline
from climara.graphics._render_svg import save_svg


class DemoSourceMappedPwritxDrawProvider:
    source_mapped = True
    source_map_reference = "docs/ncl_plotchar_pwritx_formula_audit.md"

    def __init__(self):
        self.calls = []

    def draw_for_request(self, request):
        self.calls.append(request)

        x = float(request.xpos)
        y = float(request.ypos)
        w = 0.26
        h = 0.08

        return PwritxDrawResult(
            polylines=(
                PwritxDrawPolyline(
                    points=(
                        (x, y),
                        (x + w, y),
                        (x + w, y + h),
                        (x, y + h),
                        (x, y),
                    )
                ),
                PwritxDrawPolyline(
                    points=(
                        (x + 0.02, y + 0.02),
                        (x + w - 0.02, y + h - 0.02),
                    )
                ),
            ),
            metrics=build_plotchar_extent_metrics(
                dl=0.0,
                dr=w,
                db=0.0,
                dt=h,
            ),
            text="PWRITX_DRAW_PROVIDER_DEMO",
            font_number=0,
            glyph_count=0,
        )


class BadPwritxDrawProvider:
    source_mapped = False
    source_map_reference = ""

    def draw_for_request(self, request):
        raise AssertionError("bad provider should not be called")


def state():
    out = PlotcharState.defaults()
    out.pcseti("TE", 1)
    out.pcseti("QU", 1)
    out.pcseti("FN", 0)
    out.pcseti("MA", 0)
    return out


def real_string(st, text):
    code = chr(st.nfcc) if st.nfcc >= 0 else ":"
    return f"{code}A{code}{text}"


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
    provider = DemoSourceMappedPwritxDrawProvider()

    result = render_plchhq_real_string_to_ndc_polylines(
        chrs=real_string(st, "ABC"),
        state=st,
        xpos=0.18,
        ypos=0.52,
        size=0.035,
        angle=360.0,
        cntr=-1.0,
        pwritx_draw_provider=provider,
    )

    if len(provider.calls) != 1:
        raise AssertionError("source-mapped PWRITX draw provider was not called exactly once")

    if result.font_number != 0:
        raise AssertionError("PWRITX draw provider result should preserve font_number=0")

    try:
        render_plchhq_real_string_to_ndc_polylines(
            chrs=real_string(st, "ABC"),
            state=st,
            xpos=0.18,
            ypos=0.52,
            size=0.035,
            angle=360.0,
            cntr=-1.0,
            pwritx_draw_provider=BadPwritxDrawProvider(),
        )
    except PlotcharUnsupportedError as exc:
        print("bad draw provider guarded:", exc)
    else:
        raise AssertionError("non-source-mapped PWRITX draw provider should be guarded")

    root = HluPrimitive()
    add_result(root, result)

    out = Path("outputs/figures/demo_plotchar_pwritx_draw_provider_seam.svg")
    save_svg(root, out, width=900, height=360, background="white")

    print("provider calls:", len(provider.calls))
    print("result text:", result.text)
    print("result metrics:", result.metrics)
    print(f"wrote {out}")
    print("✅ PWRITX/font0 draw provider seam demo passed")


if __name__ == "__main__":
    main()
