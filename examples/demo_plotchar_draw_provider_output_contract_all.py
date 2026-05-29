from climara.graphics._plotchar_greek_draw_provider import (
    GreekDrawPolyline,
    GreekDrawResult,
)
from climara.graphics._plotchar_mapped_draw_provider import (
    MappedDrawPolyline,
    MappedDrawResult,
)
from climara.graphics._plotchar_metrics import build_plotchar_extent_metrics
from climara.graphics._plotchar_pwritx_draw_provider import (
    PwritxDrawPolyline,
    PwritxDrawResult,
)
from climara.graphics._plotchar_state import PlotcharState, PlotcharUnsupportedError
from climara.graphics._plotchar_svg_runtime import render_plchhq_real_string_to_ndc_polylines


def real_string(st, body):
    code = chr(st.nfcc) if st.nfcc >= 0 else ":"
    return f"{code}A{code}{body}"


def base_state(font=21, map_mode=0):
    st = PlotcharState.defaults()
    st.pcseti("TE", 1)
    st.pcseti("QU", 0)
    st.pcseti("FN", font)
    st.pcseti("MA", map_mode)
    return st


def good_metrics():
    return build_plotchar_extent_metrics(
        dl=0.0,
        dr=0.10,
        db=0.0,
        dt=0.06,
    )


def bad_metrics():
    return build_plotchar_extent_metrics(
        dl=-0.01,
        dr=0.10,
        db=0.0,
        dt=0.06,
    )


class GoodGreekProvider:
    source_mapped = True
    source_map_reference = "docs/ncl_plotchar_greek_ifgr_digitization_source_map.md"

    def draw_for_request(self, request):
        x = float(request.xpos)
        y = float(request.ypos)

        return GreekDrawResult(
            polylines=(
                GreekDrawPolyline(
                    points=((x, y), (x + 0.05, y + 0.06), (x + 0.10, y)),
                ),
            ),
            metrics=good_metrics(),
            text="GOOD_GREEK",
            font_number=21,
            glyph_count=1,
        )


class BadGreekProvider(GoodGreekProvider):
    def draw_for_request(self, request):
        result = super().draw_for_request(request)

        return GreekDrawResult(
            polylines=result.polylines,
            metrics=bad_metrics(),
            text=result.text,
            font_number=result.font_number,
            glyph_count=result.glyph_count,
        )


class GoodPwritxProvider:
    source_mapped = True
    source_map_reference = "docs/ncl_plotchar_pwritx_formula_audit.md"

    def draw_for_request(self, request):
        x = float(request.xpos)
        y = float(request.ypos)

        return PwritxDrawResult(
            polylines=(
                PwritxDrawPolyline(
                    points=((x, y), (x + 0.10, y), (x + 0.10, y + 0.06), (x, y + 0.06), (x, y)),
                ),
            ),
            metrics=good_metrics(),
            text="GOOD_PWRITX",
            font_number=0,
            glyph_count=1,
        )


class BadPwritxProvider(GoodPwritxProvider):
    def draw_for_request(self, request):
        result = super().draw_for_request(request)

        return PwritxDrawResult(
            polylines=(
                PwritxDrawPolyline(
                    points=((0.0, 0.0),),
                ),
            ),
            metrics=result.metrics,
            text=result.text,
            font_number=result.font_number,
            glyph_count=result.glyph_count,
        )


class GoodMappedProvider:
    source_mapped = True
    source_map_reference = "docs/ncl_plotchar_mapped_draw_imap_source_map.md"

    def draw_for_request(self, request):
        x = float(request.xpos)
        y = float(request.ypos)

        return MappedDrawResult(
            polylines=(
                MappedDrawPolyline(
                    points=((x, y), (x + 0.05, y + 0.06), (x + 0.10, y + 0.02)),
                ),
            ),
            metrics=good_metrics(),
            text="GOOD_MAPPED",
            font_number=21,
            glyph_count=1,
        )


class BadMappedProvider(GoodMappedProvider):
    def draw_for_request(self, request):
        result = super().draw_for_request(request)

        return MappedDrawResult(
            polylines=result.polylines,
            metrics=result.metrics,
            text=result.text,
            font_number=result.font_number,
            glyph_count=-1,
        )


def run_greek(provider):
    st = base_state(font=21, map_mode=0)
    code = chr(st.nfcc) if st.nfcc >= 0 else ":"

    return render_plchhq_real_string_to_ndc_polylines(
        chrs=real_string(st, f"A{code}G{code}BC"),
        state=st,
        xpos=0.20,
        ypos=0.50,
        size=0.035,
        angle=360.0,
        cntr=-1.0,
        greek_draw_provider=provider,
    )


def run_pwritx(provider):
    st = base_state(font=0, map_mode=0)

    return render_plchhq_real_string_to_ndc_polylines(
        chrs=real_string(st, "ABC"),
        state=st,
        xpos=0.20,
        ypos=0.50,
        size=0.035,
        angle=360.0,
        cntr=-1.0,
        pwritx_draw_provider=provider,
    )


def run_mapped(provider):
    st = base_state(font=21, map_mode=1)

    return render_plchhq_real_string_to_ndc_polylines(
        chrs=real_string(st, "ABC"),
        state=st,
        xpos=0.20,
        ypos=0.50,
        size=0.035,
        angle=360.0,
        cntr=-1.0,
        mapped_draw_provider=provider,
    )


def expect_guard(label, func):
    try:
        func()
    except PlotcharUnsupportedError as exc:
        print(f"{label} guarded:")
        print(f"  {exc}")
        return

    raise AssertionError(f"{label} should have been guarded")


def main():
    good_greek = run_greek(GoodGreekProvider())
    good_pwritx = run_pwritx(GoodPwritxProvider())
    good_mapped = run_mapped(GoodMappedProvider())

    if good_greek.glyph_count != 1:
        raise AssertionError("good Greek provider should pass output contract")

    if good_pwritx.glyph_count != 1:
        raise AssertionError("good PWRITX provider should pass output contract")

    if good_mapped.glyph_count != 1:
        raise AssertionError("good mapped provider should pass output contract")

    expect_guard(
        "bad Greek metrics",
        lambda: run_greek(BadGreekProvider()),
    )

    expect_guard(
        "bad PWRITX polyline",
        lambda: run_pwritx(BadPwritxProvider()),
    )

    expect_guard(
        "bad mapped glyph_count",
        lambda: run_mapped(BadMappedProvider()),
    )

    print()
    print("good Greek metrics:", good_greek.metrics)
    print("good PWRITX metrics:", good_pwritx.metrics)
    print("good mapped metrics:", good_mapped.metrics)
    print("✅ all Plotchar draw-provider output contract demos passed")


if __name__ == "__main__":
    main()
