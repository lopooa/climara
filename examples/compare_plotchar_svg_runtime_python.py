from pathlib import Path

from climara.graphics._primitive import HluPrimitive
from climara.graphics._render_svg import save_svg
from climara.graphics._text_item import build_text_item


def add_plotchar(root, text, y, *, height=0.036):
    root.add_child(
        build_text_item(
            text,
            0.08,
            y,
            resources={
                "txJust": "CenterLeft",
                "txFont": 21,
                "txFontHeightF": height,
                "txFontColor": "black",
                "txFontThicknessF": 1.0,
                "txFuncCode": "~",
                "climaraTextEngine": "plotchar",
                "climaraPlotcharBBoxOn": False,
                "climaraPlotcharFillOn": False,
                "climaraPlotcharOutlineOn": True,
                "climaraPlotcharStrokeWidthScale": 1.25,
            },
        )
    )


def main():
    root = HluPrimitive()

    add_plotchar(root, "Python Plotchar reference", 0.91, height=0.044)
    add_plotchar(root, "Plain: ABC abc 123", 0.78)
    add_plotchar(root, "Subscript: H~B~2~N~O", 0.65)
    add_plotchar(root, "Superscript: x~S~2~N~ + y~S~2~N~", 0.52)
    add_plotchar(root, "Move: A~H15~B~V10~C", 0.39)
    add_plotchar(root, "Zoom: A~X130~B~Y80~C~Z100~", 0.26)
    add_plotchar(root, "Carriage: Line1~C~Line2", 0.13)

    out = Path("outputs/figures/compare_plotchar_svg_runtime_python.svg")
    save_svg(root, out, width=1024, height=1024, background="white")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
