from __future__ import annotations

from pathlib import Path


def main() -> None:
    import climara.graphics as cgr

    out_base = Path("outputs") / "figures" / "map_grid_svg_smoke"

    wks = cgr.gsn_open_wks(
        "svg",
        out_base,
        resources={
            "wkWidth": 1000,
            "wkHeight": 680,
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
            "mpGridSpacingF": 0.25,
            "mpGridLineColor": "#888888",
            "mpGridLineThicknessF": 0.7,
            "mpGridLineDashPattern": "4 4",
            "tiMainString": "Map grid smoke",
            "gsnLeftString": "grid on",
            "gsnRightString": "SVG",
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
        "Map grid smoke",
        "grid on",
        "SVG",
    ]
    missing = [item for item in required if item not in text]
    if missing:
        raise RuntimeError(f"map grid SVG missing: {missing}")

    line_count = text.count("<line")
    if line_count < 4:
        raise RuntimeError(f"expected grid lines, found only {line_count}")

    print(f"✅ map grid smoke passed: {output}")
    print(f"✅ line elements: {line_count}")
    print(f"✅ frame_count: {wks.frame_count}")


if __name__ == "__main__":
    main()
