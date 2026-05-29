from pathlib import Path

from climara.graphics._plotchar_mapped_draw_provider import (
    MappedDrawPolyline,
    MappedDrawResult,
)
from climara.graphics._plotchar_metrics import build_plotchar_extent_metrics
from climara.graphics._plotchar_state import PlotcharUnsupportedError
from climara.graphics._primitive import HluPrimitive
from climara.graphics._render_svg import save_svg
from climara.graphics._text_item import build_text_item


class DemoMappedProvider:
    source_mapped = True
    source_map_reference = "docs/ncl_plotchar_mapped_draw_imap_source_map.md"

    def __init__(self):
        self.calls = []

    def draw_for_request(self, request):
        self.calls.append(request)

        x = float(request.xpos)
        y = float(request.ypos)

        return MappedDrawResult(
            polylines=(
                MappedDrawPolyline(
                    points=(
                        (x, y),
                        (x + 0.07, y + 0.08),
                        (x + 0.14, y + 0.02),
                        (x + 0.21, y + 0.11),
                        (x + 0.28, y + 0.04),
                    )
                ),
            ),
            metrics=build_plotchar_extent_metrics(
                dl=0.0,
                dr=0.28,
                db=0.0,
                dt=0.11,
            ),
            text="TEXTITEM_MAPPED_PROVIDER_DEMO",
            font_number=21,
            glyph_count=0,
        )


class BadMappedProvider:
    source_mapped = False
    source_map_reference = ""

    def draw_for_request(self, request):
        raise AssertionError("bad provider should not be called")


def make_text(label, y, extra):
    resources = {
        "txJust": "CenterLeft",
        "txFont": 21,
        "txFontHeightF": 0.050,
        "txFontColor": "black",
        "txFuncCode": "~",
        "climaraTextEngine": "plotchar",
        "climaraPlotcharMapMode": 1,
        "climaraPlotcharFillOn": False,
        "climaraPlotcharOutlineOn": True,
        "climaraPlotcharBBoxOn": True,
        "climaraPlotcharBBoxSource": "metrics",
        "climaraPlotcharBBoxColor": "blue",
        "climaraPlotcharBBoxThicknessF": 0.8,
    }
    resources.update(extra)

    return build_text_item(
        label,
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
            Path("outputs/figures/_mapped_should_not_render.svg"),
            width=900,
            height=360,
            background="white",
        )
    except PlotcharUnsupportedError as exc:
        print(f"{label} guarded:")
        print(f"  {exc}")
        return

    raise AssertionError(f"{label} should have been guarded")


def main():
    expect_guard(
        "mapped TextItem without provider",
        make_text(
            "mapped default guard",
            0.50,
            {},
        ),
    )

    expect_guard(
        "mapped TextItem bad provider",
        make_text(
            "mapped bad provider",
            0.50,
            {
                "climaraPlotcharMappedDrawProvider": BadMappedProvider(),
            },
        ),
    )

    provider = DemoMappedProvider()

    root = HluPrimitive()
    root.add_child(
        make_text(
            "mapped good provider",
            0.50,
            {
                "climaraPlotcharMappedDrawProvider": provider,
            },
        )
    )

    out = Path("outputs/figures/demo_plotchar_textitem_mapped_provider_seam.svg")
    save_svg(root, out, width=1000, height=420, background="white")

    if len(provider.calls) != 1:
        raise AssertionError("mapped TextItem provider should be called exactly once")

    print("provider calls:", len(provider.calls))
    print("request map mode:", provider.calls[0].state.imap)
    print(f"wrote {out}")
    print("✅ TextItem mapped provider seam demo passed")


if __name__ == "__main__":
    main()
