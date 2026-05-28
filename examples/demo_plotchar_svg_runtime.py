from pathlib import Path

from climara.graphics._plotchar_fontcap import load_fontcap
from climara.graphics._primitive import HluPrimitive
from climara.graphics._render_svg import save_svg
from climara.graphics._text_item import build_text_item


def find_font_switch_demo(base_font=21):
    base = load_fontcap(base_font)

    preferred = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    candidates = [
        1, 2, 3, 4, 5, 6, 7, 8, 9,
        10, 11, 12, 13, 14, 15, 16, 17,
        18, 19, 20, 22, 25, 26, 29, 30,
        33, 34, 35, 36, 37,
    ]

    for other_font in candidates:
        if other_font == base_font:
            continue

        try:
            other = load_fontcap(other_font)
        except Exception:
            continue

        shared = []
        for char in preferred:
            code = ord(char)
            if code in base.glyphs and code in other.glyphs:
                shared.append(char)

        if len(shared) >= 2:
            return other_font, "".join(shared[:4])

    return None, ""


def add_plotchar(root, text, y, *, font=21, height=0.040, bbox=True):
    root.add_child(
        build_text_item(
            text,
            0.06,
            y,
            resources={
                "txJust": "CenterLeft",
                "txFont": font,
                "txFontHeightF": height,
                "txFontColor": "black",
                "txFontThicknessF": 1.0,
                "txFuncCode": "~",
                "climaraTextEngine": "plotchar",
                "climaraPlotcharBBoxOn": bbox,
                "climaraPlotcharBBoxColor": "red",
                "climaraPlotcharBBoxThicknessF": 0.8,
            },
        )
    )


def add_status_text(root, text, y):
    root.add_child(
        build_text_item(
            text,
            0.06,
            y,
            resources={
                "txJust": "CenterLeft",
                "txFontHeightF": 0.026,
                "txFontColor": "black",
            },
        )
    )


def main():
    root = HluPrimitive()

    switch_font, shared = find_font_switch_demo(21)

    add_plotchar(root, "Plotchar SVG runtime", 0.90, height=0.050)
    add_plotchar(root, "Plain: ABC abc 123", 0.79)
    add_plotchar(root, "Subscript: H~B~2~N~O", 0.68)
    add_plotchar(root, "Superscript: x~S~2~N~ + y~S~2~N~", 0.57)

    if switch_font is None:
        add_status_text(
            root,
            "Font switch guarded: no shared ASCII glyphs found between font21 and local candidate fontcaps.",
            0.46,
        )
        print("font switch guarded: no safe shared glyphs found; not faking missing fontcap glyphs")
    else:
        add_plotchar(
            root,
            f"Font switch: FONT21 ~F{switch_font}~{shared} ~F21~FONT21",
            0.46,
        )
        print(f"font switch demo uses font{switch_font} with shared glyphs: {shared!r}")

    add_plotchar(root, "Move: A~H15~B~V10~C", 0.35)
    add_plotchar(root, "Zoom: A~X130~B~Y80~C~Z100~", 0.24)
    add_plotchar(root, "Carriage: Line1~C~Line2", 0.13)

    root.add_child(
        build_text_item(
            "Fallback SVG text",
            0.06,
            0.045,
            resources={
                "txJust": "CenterLeft",
                "txFontHeightF": 0.030,
                "txFontColor": "black",
            },
        )
    )

    out = Path("outputs/figures/demo_plotchar_svg_runtime.svg")
    save_svg(root, out, width=1500, height=820, background="white")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
