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
                "txFontHeightF": 0.055,
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

    add_plotchar(root, "principal: ABC", 0.78)
    add_plotchar(root, "indexical: A~I~BC~P~DE", 0.55)
    add_plotchar(root, "cartographic: A~K~BC~P~DE", 0.32)
    add_plotchar(root, "mixed: A~I~B~K~C~P~D", 0.12)

    out = Path("outputs/figures/demo_plotchar_pik_size_level_svg_runtime.svg")
    save_svg(root, out, width=1200, height=650, background="white")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
