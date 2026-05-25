from pathlib import Path
import sys

from climara.graphics._labelbar_object import HluLabelBar, build_hlu_labelbar
from climara.graphics._render_svg import save_svg


OUT = Path("outputs/figures")
OUT.mkdir(parents=True, exist_ok=True)


def run_case(name, labelbar):
    out = OUT / f"labelbar_position_{name}.svg"

    print(f"START {name}", flush=True)
    geom = labelbar.compute_geometry()
    print(
        f"  geom: orientation={geom.orientation}, "
        f"position={geom.label_position}, "
        f"labels={geom.visible_label_strings}",
        flush=True,
    )

    save_svg(labelbar, out, width=900, height=500)

    text = out.read_text(encoding="utf-8")
    print(
        f"  svg: bytes={len(text)}, "
        f"polygons={text.count('<polygon')}, "
        f"lines={text.count('<line')}, "
        f"texts={text.count('<text')}",
        flush=True,
    )

    if "<svg" not in text:
        raise RuntimeError(f"{name}: output is not SVG")

    for label in geom.visible_label_strings:
        if str(label) not in text:
            raise RuntimeError(f"{name}: missing label {label}")

    print(f"PASS {name}: {out}", flush=True)


def main():
    cases = []

    cases.append((
        "horizontal_bottom",
        build_hlu_labelbar(
            rect=(0.12, 0.82, 0.76, 0.20),
            colors=("#2166ac", "#67a9cf", "#f7f7f7", "#ef8a62"),
            labels=("HB0", "HB1", "HB2"),
            resources={
                "EndStyle": "IncludeOuterBoxes",
                "lbLabelPosition": "Bottom",
            },
        ),
    ))

    cases.append((
        "horizontal_top",
        build_hlu_labelbar(
            rect=(0.12, 0.82, 0.76, 0.20),
            colors=("#2166ac", "#67a9cf", "#f7f7f7", "#ef8a62"),
            labels=("HT0", "HT1", "HT2"),
            resources={
                "EndStyle": "IncludeOuterBoxes",
                "lbLabelPosition": "Top",
            },
        ),
    ))

    cases.append((
        "horizontal_center",
        build_hlu_labelbar(
            rect=(0.12, 0.82, 0.76, 0.20),
            colors=("#2166ac", "#67a9cf", "#f7f7f7", "#ef8a62"),
            labels=("HC0", "HC1", "HC2"),
            resources={
                "EndStyle": "IncludeOuterBoxes",
                "lbLabelPosition": "Center",
            },
        ),
    ))

    cases.append((
        "vertical_right",
        HluLabelBar(
            rect=(0.20, 0.88, 0.24, 0.62),
            colors=("#2166ac", "#f7f7f7", "#b2182b"),
            labels=("VR0", "VR1", "VR2"),
            resources={
                "lbBoxCount": 3,
                "lbOrientation": "Vertical",
                "lbLabelAlignment": "BoxCenters",
                "lbLabelPosition": "Right",
            },
        ),
    ))

    cases.append((
        "vertical_left",
        HluLabelBar(
            rect=(0.56, 0.88, 0.24, 0.62),
            colors=("#2166ac", "#f7f7f7", "#b2182b"),
            labels=("VL0", "VL1", "VL2"),
            resources={
                "lbBoxCount": 3,
                "lbOrientation": "Vertical",
                "lbLabelAlignment": "BoxCenters",
                "lbLabelPosition": "Left",
            },
        ),
    ))

    cases.append((
        "vertical_center",
        HluLabelBar(
            rect=(0.38, 0.88, 0.24, 0.62),
            colors=("#2166ac", "#f7f7f7", "#b2182b"),
            labels=("VC0", "VC1", "VC2"),
            resources={
                "lbBoxCount": 3,
                "lbOrientation": "Vertical",
                "lbLabelAlignment": "BoxCenters",
                "lbLabelPosition": "Center",
            },
        ),
    ))

    for name, labelbar in cases:
        run_case(name, labelbar)

    print("✅ LabelBar label-position full-render smoke passed", flush=True)


if __name__ == "__main__":
    main()
