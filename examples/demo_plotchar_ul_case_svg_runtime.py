from pathlib import Path

from climara.graphics._primitive import HluPrimitive
from climara.graphics._render_svg import save_svg
from climara.graphics._text_item import build_text_item


def add_plotchar(root, text, y):
    root.add_child(
        build_text_item(
            text,
            0.08,
            y,
            resources={
                "txJust": "CenterLeft",
                "txFont": 21,
                "txFontHeightF": 0.045,
                "txFontColor": "black",
                "txFontThicknessF": 1.0,
                "txFuncCode": "~",
                "climaraTextEngine": "plotchar",
                "climaraPlotcharFillOn": False,
                "climaraPlotcharOutlineOn": True,
                "climaraPlotcharBBoxOn": True,
                "climaraPlotcharBBoxSource": "metrics",
                "climaraPlotcharBBoxColor": "blue",
                "climaraPlotcharBBoxThicknessF": 0.8,
            },
        )
    )


def main():
    root = HluPrimitive()

    add_plotchar(root, "plain: abc ABC", 0.78)
    add_plotchar(root, "upper persistent: ~U~abc ABC", 0.58)
    add_plotchar(root, "lower persistent: ~L~abc ABC", 0.38)
    add_plotchar(root, "counted upper: ~U3~abcdef", 0.18)

    out = Path("outputs/figures/demo_plotchar_ul_case_svg_runtime.svg")
    save_svg(root, out, width=1200, height=600, background="white")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
