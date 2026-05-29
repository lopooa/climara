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

    add_plotchar(root, "plain: ABC", 0.86)
    add_plotchar(root, "hmove: A~H15~BC", 0.72)
    add_plotchar(root, "vmove: A~V10~BC", 0.58)
    add_plotchar(root, "xzoom: A~X130~BC", 0.44)
    add_plotchar(root, "yzoom: A~Y80~BC", 0.30)
    add_plotchar(root, "zzoom: A~Z130~BC", 0.16)
    add_plotchar(root, "carriage: Line1~C~Line2", 0.05)

    out = Path("outputs/figures/demo_plotchar_hvxyz_c_svg_runtime.svg")
    save_svg(root, out, width=1300, height=900, background="white")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
