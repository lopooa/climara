from pathlib import Path

from climara.graphics._plotchar_greek_draw_provider import (
    GreekDrawPolyline,
    GreekDrawResult,
)
from climara.graphics._plotchar_metrics import build_plotchar_extent_metrics
from climara.graphics._plotchar_state import PlotcharState, PlotcharUnsupportedError
from climara.graphics._plotchar_svg_runtime import render_plchhq_real_string_to_ndc_polylines
from climara.graphics._primitive import HluPrimitive, build_polyline
from climara.graphics._render_svg import save_svg


class DemoSourceMappedGreekDrawProvider:
    source_mapped = True
    source_map_reference = "docs/ncl_plotchar_greek_ifgr_digitization_source_map.md"

    def __init__(self):
        self.calls = []

    def draw_for_request(self, request):
        self.calls.append(request)

        x = float(request.xpos)
        y = float(request.ypos)

        return GreekDrawResult(
            polylines=(
                GreekDrawPolyline(
                    points=(
                        (x, y),
                        (x + 0.08, y + 0.08),
                        (x + 0.16, y),
                    )
                ),
                GreekDrawPolyline(
                    points=(
                        (x + 0.04, y + 0.035),
                        (x + 0.12, y + 0.035),
                    )
                ),
            ),
            metrics=build_plotchar_extent_metrics(
                dl=0.0,
                dr=0.16,
                db=0.0,
                dt=0.08,
            ),
            text="GREEK_DRAW_PROVIDER_DEMO",
            font_number=21,
            glyph_count=0,
        )


class BadGreekDrawProvider:
    source_mapped = False
    source_map_reference = ""

    def draw_for_request(self, request):
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
    body = f"A{code}G{code}BC"

    try:
        render_plchhq_real_string_to_ndc_polylines(
            chrs=real_string(st, body),
            state=st,
            xpos=0.18,
            ypos=0.52,
            size=0.035,
            angle=360.0,
            cntr=-1.0,
        )
    except PlotcharUnsupportedError as exc:
        print("G default guarded:", exc)
    else:
        raise AssertionError("G Greek should remain guarded without provider")

    try:
        render_plchhq_real_string_to_ndc_polylines(
            chrs=real_string(st, body),
            state=st,
            xpos=0.18,
            ypos=0.52,
            size=0.035,
            angle=360.0,
            cntr=-1.0,
            greek_draw_provider=BadGreekDrawProvider(),
        )
    except PlotcharUnsupportedError as exc:
        print("bad Greek provider guarded:", exc)
    else:
        raise AssertionError("non-source-mapped Greek provider should be guarded")

    provider = DemoSourceMappedGreekDrawProvider()
    result = render_plchhq_real_string_to_ndc_polylines(
        chrs=real_string(st, body),
        state=st,
        xpos=0.18,
        ypos=0.52,
        size=0.035,
        angle=360.0,
        cntr=-1.0,
        greek_draw_provider=provider,
    )

    if len(provider.calls) != 1:
        raise AssertionError("source-mapped Greek draw provider was not called exactly once")

    root = HluPrimitive()
    add_result(root, result)

    out = Path("outputs/figures/demo_plotchar_greek_draw_provider_seam.svg")
    save_svg(root, out, width=900, height=360, background="white")

    print("provider calls:", len(provider.calls))
    print("result text:", result.text)
    print("result metrics:", result.metrics)
    print(f"wrote {out}")
    print("✅ G Greek draw-provider seam demo passed")


if __name__ == "__main__":
    main()
