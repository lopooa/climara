from pathlib import Path

from climara.graphics._primitive import HluPrimitive
from climara.graphics._render_svg import save_svg
from climara.graphics._text_item import build_text_item
from climara.graphics._plotchar_state import PlotcharUnsupportedError


def main():
    root = HluPrimitive()

    root.add_child(
        build_text_item(
            "font0 should guard",
            0.10,
            0.55,
            resources={
                "txJust": "CenterLeft",
                "txFont": 0,
                "txFontHeightF": 0.050,
                "txFontColor": "black",
                "txFuncCode": "~",
                "climaraTextEngine": "plotchar",
                "climaraPlotcharFillOn": False,
                "climaraPlotcharOutlineOn": True,
                "climaraPlotcharBBoxOn": True,
            },
        )
    )

    try:
        save_svg(
            root,
            Path("outputs/figures/demo_plotchar_pwritx_svg_draw_guard.svg"),
            width=900,
            height=360,
            background="white",
        )
    except PlotcharUnsupportedError as exc:
        print("PWRITX/font0 SVG draw remains guarded:")
        print(exc)
    else:
        raise AssertionError(
            "font0/PWRITX SVG draw should remain guarded until the non-fontcap digitization branch is implemented"
        )

    print("✅ PWRITX/font0 SVG draw guard demo passed")


if __name__ == "__main__":
    main()
