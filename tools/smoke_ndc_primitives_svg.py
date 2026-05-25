from __future__ import annotations

from pathlib import Path


def main() -> None:
    import climara.graphics as cgr

    out_base = Path("outputs") / "figures" / "ndc_primitives_smoke"

    wks = cgr.gsn_open_wks(
        "svg",
        out_base,
        resources={
            "wkWidth": 900,
            "wkHeight": 650,
            "wkBackgroundColor": "white",
        },
    )

    cgr.gsn_polygon_ndc(
        wks,
        [0.08, 0.92, 0.92, 0.08],
        [0.12, 0.12, 0.86, 0.86],
        {
            "gsFillColor": "#f7f7f7",
            "gsLineColor": "#222222",
            "gsLineThicknessF": 1.2,
        },
    )

    cgr.gsn_polyline_ndc(
        wks,
        [0.14, 0.28, 0.42, 0.58, 0.74, 0.86],
        [0.28, 0.62, 0.44, 0.72, 0.48, 0.78],
        {
            "gsLineColor": "#0055aa",
            "gsLineThicknessF": 2.5,
        },
    )

    cgr.gsn_polymarker_ndc(
        wks,
        [0.28, 0.42, 0.58, 0.74],
        [0.62, 0.44, 0.72, 0.48],
        {
            "gsMarkerColor": "#cc3300",
            "gsMarkerSizeF": 0.011,
        },
    )

    cgr.gsn_text_ndc(
        wks,
        "NDC primitives -> workstation -> SVG",
        0.50,
        0.93,
        {
            "txFontHeightF": 0.028,
            "txFontColor": "#111111",
            "txJust": "CenterCenter",
        },
    )

    output = cgr.frame(wks)

    text = output.read_text(encoding="utf-8")
    required = ["<svg", "<polygon", "<polyline", "<circle", "<text", "NDC primitives"]
    missing = [item for item in required if item not in text]
    if missing:
        raise RuntimeError(f"SVG output missing required content: {missing}")

    print(f"✅ NDC primitive smoke passed: {output}")
    print(f"✅ children: {len(wks.children)}")
    print(f"✅ frame_count: {wks.frame_count}")


if __name__ == "__main__":
    main()
