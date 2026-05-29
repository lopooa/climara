from pathlib import Path

from climara.graphics._plotchar_greek_draw_provider import (
    GreekDrawPolyline,
    GreekDrawResult,
)
from climara.graphics._plotchar_metrics import build_plotchar_extent_metrics
from climara.graphics._plotchar_pwritx_draw_provider import (
    PwritxDrawPolyline,
    PwritxDrawResult,
)
from climara.graphics._primitive import HluPrimitive
from climara.graphics._render_svg import save_svg
from climara.graphics._text_item import build_text_item


class DemoGreekProvider:
    source_mapped = True
    source_map_reference = "docs/ncl_plotchar_greek_ifgr_digitization_source_map.md"

    def draw_for_request(self, request):
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
            text="GREEK_PROVIDER_DEMO",
            font_number=21,
            glyph_count=0,
        )


class DemoPwritxProvider:
    source_mapped = True
    source_map_reference = "docs/ncl_plotchar_pwritx_formula_audit.md"

    def draw_for_request(self, request):
        x = float(request.xpos)
        y = float(request.ypos)
        w = 0.25
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
            text="PWRITX_PROVIDER_DEMO",
            font_number=0,
            glyph_count=0,
        )


def add_text(root, text, y, resources):
    root.add_child(
        build_text_item(
            text,
            0.10,
            y,
            resources={
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
                **resources,
            },
        )
    )


def main():
    root = HluPrimitive()

    add_text(
        root,
        "TextItem Greek seam: A~G~BC",
        0.68,
        {
            "txFont": 21,
            "climaraPlotcharGreekDrawProvider": DemoGreekProvider(),
        },
    )

    add_text(
        root,
        "TextItem PWRITX seam",
        0.36,
        {
            "txFont": 0,
            "climaraPlotcharPwritxDrawProvider": DemoPwritxProvider(),
        },
    )

    out = Path("outputs/figures/demo_plotchar_textitem_provider_seams.svg")
    save_svg(root, out, width=1000, height=560, background="white")
    print(f"wrote {out}")
    print("✅ TextItem Greek/PWRITX provider seam demo passed")


if __name__ == "__main__":
    main()
