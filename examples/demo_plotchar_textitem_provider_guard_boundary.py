from pathlib import Path

from climara.graphics._plotchar_greek_draw_provider import GreekDrawPolyline, GreekDrawResult
from climara.graphics._plotchar_metrics import build_plotchar_extent_metrics
from climara.graphics._plotchar_pwritx_draw_provider import PwritxDrawPolyline, PwritxDrawResult
from climara.graphics._plotchar_state import PlotcharUnsupportedError
from climara.graphics._primitive import HluPrimitive
from climara.graphics._render_svg import save_svg
from climara.graphics._text_item import build_text_item


class GoodGreekProvider:
    source_mapped = True
    source_map_reference = "docs/ncl_plotchar_greek_ifgr_digitization_source_map.md"

    def draw_for_request(self, request):
        x = float(request.xpos)
        y = float(request.ypos)

        polyline = GreekDrawPolyline(
            points=(
                (x, y),
                (x + 0.10, y + 0.08),
                (x + 0.20, y),
            )
        )

        return GreekDrawResult(
            polylines=(polyline,),
            metrics=build_plotchar_extent_metrics(
                dl=0.0,
                dr=0.20,
                db=0.0,
                dt=0.08,
            ),
            text="GOOD_GREEK_PROVIDER",
            font_number=21,
            glyph_count=0,
        )


class GoodPwritxProvider:
    source_mapped = True
    source_map_reference = "docs/ncl_plotchar_pwritx_formula_audit.md"

    def draw_for_request(self, request):
        x = float(request.xpos)
        y = float(request.ypos)
        w = 0.22
        h = 0.08

        polyline = PwritxDrawPolyline(
            points=(
                (x, y),
                (x + w, y),
                (x + w, y + h),
                (x, y + h),
                (x, y),
            )
        )

        return PwritxDrawResult(
            polylines=(polyline,),
            metrics=build_plotchar_extent_metrics(
                dl=0.0,
                dr=w,
                db=0.0,
                dt=h,
            ),
            text="GOOD_PWRITX_PROVIDER",
            font_number=0,
            glyph_count=0,
        )


class BadProvider:
    source_mapped = False
    source_map_reference = ""

    def draw_for_request(self, request):
        raise AssertionError("bad provider should not be called")


def make_text(text, y, extra):
    resources = {
        "txJust": "CenterLeft",
        "txFontHeightF": 0.050,
        "txFontColor": "black",
        "txFuncCode": "~",
        "climaraTextEngine": "plotchar",
        "climaraPlotcharFillOn": False,
        "climaraPlotcharOutlineOn": True,
        "climaraPlotcharBBoxOn": True,
        "climaraPlotcharBBoxSource": "metrics",
        "climaraPlotcharBBoxColor": "blue",
        "climaraPlotcharBBoxThicknessF": 0.8,
    }
    resources.update(extra)

    return build_text_item(
        text,
        0.10,
        y,
        resources=resources,
    )


def expect_guard(label, child):
    root = HluPrimitive()
    root.add_child(child)

    try:
        save_svg(
            root,
            Path("outputs/figures/_should_not_exist.svg"),
            width=700,
            height=300,
            background="white",
        )
    except PlotcharUnsupportedError as exc:
        print(f"{label} guarded:")
        print(f"  {exc}")
        return

    raise AssertionError(f"{label} should have been guarded")


def main():
    expect_guard(
        "G without provider",
        make_text(
            "Greek default guard: A~G~BC",
            0.50,
            {"txFont": 21},
        ),
    )

    expect_guard(
        "G with bad provider",
        make_text(
            "Greek bad provider: A~G~BC",
            0.50,
            {
                "txFont": 21,
                "climaraPlotcharGreekDrawProvider": BadProvider(),
            },
        ),
    )

    expect_guard(
        "font0 without provider",
        make_text(
            "font0 default guard",
            0.50,
            {"txFont": 0},
        ),
    )

    expect_guard(
        "font0 with bad provider",
        make_text(
            "font0 bad provider",
            0.50,
            {
                "txFont": 0,
                "climaraPlotcharPwritxDrawProvider": BadProvider(),
            },
        ),
    )

    root = HluPrimitive()

    root.add_child(
        make_text(
            "Greek good provider: A~G~BC",
            0.68,
            {
                "txFont": 21,
                "climaraPlotcharGreekDrawProvider": GoodGreekProvider(),
            },
        )
    )

    root.add_child(
        make_text(
            "font0 good provider",
            0.34,
            {
                "txFont": 0,
                "climaraPlotcharPwritxDrawProvider": GoodPwritxProvider(),
            },
        )
    )

    out = Path("outputs/figures/demo_plotchar_textitem_provider_guard_boundary.svg")
    save_svg(root, out, width=1000, height=560, background="white")

    print(f"wrote {out}")
    print("✅ TextItem provider guard boundary demo passed")


if __name__ == "__main__":
    main()
