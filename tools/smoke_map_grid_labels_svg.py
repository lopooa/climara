from __future__ import annotations

from pathlib import Path


def main() -> None:
    import climara.graphics as cgr

    out_base = Path("outputs") / "figures" / "map_grid_labels_svg_smoke"

    wks = cgr.gsn_open_wks(
        "svg",
        out_base,
        resources={
            "wkWidth": 1100,
            "wkHeight": 720,
            "wkBackgroundColor": "white",
        },
    )

    plot = cgr.gsn_csm_map(
        wks,
        {
            "mpProjection": "CylindricalEquidistant",
            "mpFillColor": "#f9f9f9",
            "mpGeophysicalLineColor": "#222222",
            "mpGeophysicalLineThicknessF": 1.0,
            "mpGridAndLimbOn": True,
            "mpGridLonSpacingF": 60,
            "mpGridLatSpacingF": 30,
            "mpGridLabelsOn": True,
            "mpGridLineColor": "#888888",
            "mpGridLineThicknessF": 0.7,
            "mpGridLineDashPattern": "4 4",
            "tmLabelFontHeightF": 0.012,
            "tmLabelGapF": 0.012,
            "tiMainString": "Map degree grid smoke",
            "gsnLeftString": "60° lon",
            "gsnRightString": "30° lat",
        },
    )

    cgr.gsn_polyline_ndc(
        plot,
        [0.12, 0.30, 0.48, 0.66, 0.86],
        [0.25, 0.60, 0.42, 0.70, 0.36],
        {
            "gsLineColor": "#0055aa",
            "gsLineThicknessF": 2.0,
        },
    )

    output = cgr.frame(wks)

    text = output.read_text(encoding="utf-8")
    required = [
        "<svg",
        "<rect",
        "<line",
        "<polyline",
        "stroke-dasharray",
        "Map degree grid smoke",
        "120°W",
        "60°W",
        "0°",
        "60°E",
        "120°E",
        "30°S",
        "30°N",
    ]
    missing = [item for item in required if item not in text]
    if missing:
        raise RuntimeError(f"map grid labels SVG missing: {missing}")

    line_count = text.count("<line")
    if line_count < 10:
        raise RuntimeError(f"expected grid lines, found only {line_count}")

    print(f"✅ map grid labels smoke passed: {output}")
    print(f"✅ line elements: {line_count}")
    print(f"✅ frame_count: {wks.frame_count}")


if __name__ == "__main__":
    main()
