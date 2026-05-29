from pathlib import Path

from climara.graphics._primitive import HluPrimitive, build_polyline
from climara.graphics._render_svg import save_svg
from climara.graphics._text_item import build_text_item


def add_anchor(root, x, y, size=0.018):
    root.add_child(
        build_polyline(
            [x - size, x + size],
            [y, y],
            resources={"gsLineColor": "red", "gsLineThicknessF": 1.0},
        )
    )
    root.add_child(
        build_polyline(
            [x, x],
            [y - size, y + size],
            resources={"gsLineColor": "red", "gsLineThicknessF": 1.0},
        )
    )


def add_text(root, label, x, y, cntr):
    add_anchor(root, x, y)

    root.add_child(
        build_text_item(
            label,
            x,
            y,
            resources={
                "txJust": "CenterLeft",
                "txFont": 21,
                "txFontHeightF": 0.036,
                "txFontColor": "black",
                "txFontThicknessF": 1.0,
                "txFuncCode": "~",
                "climaraTextEngine": "plotchar",
                "climaraPlotcharCntr": cntr,
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

    add_text(root, "CNTR -1", 0.18, 0.72, -1.0)
    add_text(root, "CNTR 0", 0.50, 0.72, 0.0)
    add_text(root, "CNTR 1", 0.82, 0.72, 1.0)

    add_text(root, "H~B~2~N~O -1", 0.18, 0.42, -1.0)
    add_text(root, "H~B~2~N~O 0", 0.50, 0.42, 0.0)
    add_text(root, "H~B~2~N~O 1", 0.82, 0.42, 1.0)

    out = Path("outputs/figures/demo_plotchar_svg_cntr_runtime.svg")
    save_svg(root, out, width=1400, height=700, background="white")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
