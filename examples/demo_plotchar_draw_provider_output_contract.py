from climara.graphics._plotchar_mapped_draw_provider import (
    MappedDrawPolyline,
    MappedDrawResult,
)
from climara.graphics._plotchar_metrics import build_plotchar_extent_metrics
from climara.graphics._plotchar_state import PlotcharState, PlotcharUnsupportedError
from climara.graphics._plotchar_svg_runtime import render_plchhq_real_string_to_ndc_polylines


class GoodMappedProvider:
    source_mapped = True
    source_map_reference = "docs/ncl_plotchar_mapped_draw_imap_source_map.md"

    def draw_for_request(self, request):
        x = float(request.xpos)
        y = float(request.ypos)

        return MappedDrawResult(
            polylines=(
                MappedDrawPolyline(
                    points=((x, y), (x + 0.10, y + 0.05)),
                ),
            ),
            metrics=build_plotchar_extent_metrics(
                dl=0.0,
                dr=0.10,
                db=0.0,
                dt=0.05,
            ),
            text="GOOD_MAPPED_PROVIDER",
            font_number=21,
            glyph_count=1,
        )


class BadMetricProvider(GoodMappedProvider):
    def draw_for_request(self, request):
        result = super().draw_for_request(request)
        return MappedDrawResult(
            polylines=result.polylines,
            metrics=build_plotchar_extent_metrics(
                dl=-0.1,
                dr=0.10,
                db=0.0,
                dt=0.05,
            ),
            text=result.text,
            font_number=result.font_number,
            glyph_count=result.glyph_count,
        )


class BadPolylineProvider(GoodMappedProvider):
    def draw_for_request(self, request):
        result = super().draw_for_request(request)
        return MappedDrawResult(
            polylines=(
                MappedDrawPolyline(
                    points=((0.0, 0.0),),
                ),
            ),
            metrics=result.metrics,
            text=result.text,
            font_number=result.font_number,
            glyph_count=result.glyph_count,
        )


class BadGlyphCountProvider(GoodMappedProvider):
    def draw_for_request(self, request):
        result = super().draw_for_request(request)
        return MappedDrawResult(
            polylines=result.polylines,
            metrics=result.metrics,
            text=result.text,
            font_number=result.font_number,
            glyph_count=-1,
        )


def state():
    out = PlotcharState.defaults()
    out.pcseti("TE", 1)
    out.pcseti("QU", 0)
    out.pcseti("FN", 21)
    out.pcseti("MA", 1)
    return out


def real_string(st, text):
    code = chr(st.nfcc) if st.nfcc >= 0 else ":"
    return f"{code}A{code}{text}"


def run(provider):
    st = state()

    return render_plchhq_real_string_to_ndc_polylines(
        chrs=real_string(st, "ABC"),
        state=st,
        xpos=0.2,
        ypos=0.5,
        size=0.035,
        angle=360.0,
        cntr=-1.0,
        mapped_draw_provider=provider,
    )


def expect_guard(label, provider):
    try:
        run(provider)
    except PlotcharUnsupportedError as exc:
        print(f"{label} guarded:")
        print(f"  {exc}")
        return

    raise AssertionError(f"{label} should have been guarded")


def main():
    good = run(GoodMappedProvider())

    if good.glyph_count != 1:
        raise AssertionError("good provider should pass output contract")

    expect_guard("bad metric", BadMetricProvider())
    expect_guard("bad polyline", BadPolylineProvider())
    expect_guard("bad glyph_count", BadGlyphCountProvider())

    print()
    print("good result metrics:", good.metrics)
    print("good result glyph_count:", good.glyph_count)
    print("✅ Plotchar draw-provider output contract demo passed")


if __name__ == "__main__":
    main()
