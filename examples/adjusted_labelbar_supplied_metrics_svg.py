from __future__ import annotations

import os
from pathlib import Path

from climara.graphics import HluLabelBar, PlotcharExtentMetrics


def build_demo_labelbar() -> HluLabelBar:
    return HluLabelBar(
        name="adjusted_labelbar_supplied_metrics_demo",
        rect=(0.15, 0.78, 0.70, 0.20),
        colors=["#2166ac", "#67a9cf", "#fddbc7", "#b2182b"],
        labels=["Cold", "Cool", "Warm", "Hot"],
        resources={
            "lbTitleString": "Adjusted LabelBar demo",
            "lbTitlePosition": "Top",
            "lbTitleDirection": "Across",
            "lbTitleJust": "CenterCenter",
            "lbTitleAngleF": 0,
            "lbTitleFuncCode": "~",
            "lbTitleFontHeightF": 0.035,
            "lbLabelDirection": "Across",
            "lbLabelJust": "CenterCenter",
            "lbLabelAngleF": 0,
            "lbLabelFuncCode": "~",
            "lbLabelFontHeightF": 0.025,
            "lbJustification": "CenterCenter",
            "lbBoxLinesOn": True,
            "lbBoxSeparatorLinesOn": True,
        },
    )


def main(output_dir: str | os.PathLike[str] | None = None) -> Path:
    labelbar = build_demo_labelbar()

    bundle = labelbar.build_uniform_plotchar_metrics_bundle(
        title=PlotcharExtentMetrics(
            dl=0.18,
            dr=0.22,
            db=0.035,
            dt=0.075,
        ),
        label=PlotcharExtentMetrics(
            dl=0.035,
            dr=0.035,
            db=0.012,
            dt=0.026,
        ),
    )

    if output_dir is None:
        output_dir = os.environ.get(
            "CLIMARA_EXAMPLE_OUTPUT_DIR",
            "outputs/examples",
        )

    output_path = Path(output_dir) / "adjusted_labelbar_supplied_metrics.svg"

    return labelbar.save_adjusted_svg_from_plotchar_metrics_bundle(
        bundle,
        output_path,
        width=900,
        height=320,
    )


if __name__ == "__main__":
    path = main()
    print(path)
