from pathlib import Path

from climara.graphics._primitive import HluPrimitive, build_polyline
from climara.graphics._render_svg import save_svg
from climara.graphics._text_item import build_text_item


def add_anchor(root, x, y, size=0.018):
    root.add_child(
        build_polyline(
            [x - size, x + size],
            [y, y],
            resources={
                "gsLineColor": "red",
                "gsLineThicknessF": 1.0,
            },
        )
    )
    root.add_child(
        build_polyline(
            [x, x],
            [y - size, y + size],
            resources={
                "gsLineColor": "red",
                "gsLineThicknessF": 1.0,
            },
        )
    )


def add_plotchar(root, text, x, y, just, angle=0.0):
    add_anchor(root, x, y)

    root.add_child(
        build_text_item(
            text,
            x,
            y,
            resources={
                "txJust": just,
                "txFont": 21,
                "txFontHeightF": 0.034,
                "txFontColor": "black",
                "txFontThicknessF": 1.0,
                "txFuncCode": "~",
                "txAngleF": angle,
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

    add_plotchar(root, "BottomLeft", 0.18, 0.78, "BottomLeft")
    add_plotchar(root, "CenterCenter", 0.50, 0.78, "CenterCenter")
    add_plotchar(root, "TopRight", 0.82, 0.78, "TopRight")

    add_plotchar(root, "BottomCenter", 0.18, 0.50, "BottomCenter")
    add_plotchar(root, "CenterRight", 0.50, 0.50, "CenterRight")
    add_plotchar(root, "TopLeft", 0.82, 0.50, "TopLeft")

    add_plotchar(root, "Rotated Center", 0.32, 0.22, "CenterCenter", angle=45.0)
    add_plotchar(root, "Rotated Left", 0.68, 0.22, "CenterLeft", angle=45.0)

    out = Path("outputs/figures/demo_plotchar_svg_just_runtime.svg")
    save_svg(root, out, width=1200, height=850, background="white")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
