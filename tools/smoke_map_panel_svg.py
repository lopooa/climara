from __future__ import annotations

from pathlib import Path


def main() -> None:
    import climara.graphics as cgr

    out_base = Path("outputs") / "figures" / "map_panel_svg_smoke"

    wks = cgr.gsn_open_wks(
        "svg",
        out_base,
        resources={
            "wkWidth": 1100,
            "wkHeight": 760,
            "wkBackgroundColor": "white",
        },
    )

    map_res = {
        "mpProjection": "Robinson",
        "mpFillColor": "#f9f9f9",
        "mpGeophysicalLineColor": "#222222",
        "mpGeophysicalLineThicknessF": 1.0,
    }

    plots = []
    for index in range(1, 5):
        plot = cgr.gsn_csm_map(wks, map_res)

        cgr.gsn_text_ndc(
            plot,
            f"map panel {index}",
            0.50,
            1.06,
            {
                "txFontHeightF": 0.016,
                "txFontColor": "#111111",
                "txJust": "CenterCenter",
            },
        )

        cgr.gsn_polyline_ndc(
            plot,
            [0.12, 0.30, 0.48, 0.66, 0.86],
            [0.25, 0.60, 0.42, 0.70, 0.36],
            {
                "gsLineColor": "#0055aa",
                "gsLineThicknessF": 1.8,
            },
        )

        cgr.gsn_polymarker_ndc(
            plot,
            [0.30, 0.48, 0.66],
            [0.60, 0.42, 0.70],
            {
                "gsMarkerColor": "#cc3300",
                "gsMarkerSizeF": 0.010,
            },
        )

        plots.append(plot)

    wks.clear()

    panel = cgr.gsn_panel(
        wks,
        plots,
        resources={
            "gsnPanelRows": 2,
            "gsnPanelColumns": 2,
            "gsnPanelLeft": 0.08,
            "gsnPanelRight": 0.94,
            "gsnPanelBottom": 0.10,
            "gsnPanelTop": 0.86,
            "gsnPanelXWhiteSpacePercent": 6,
            "gsnPanelYWhiteSpacePercent": 10,
            "box_color": "#eeeeee",
            "gsnDraw": True,
            "gsnFrame": False,
        },
    )

    cgr.gsn_text_ndc(
        wks,
        "gsn_csm_map -> gsn_panel -> SVG",
        0.50,
        0.95,
        {
            "txFontHeightF": 0.027,
            "txFontColor": "#111111",
            "txJust": "CenterCenter",
        },
    )

    output = cgr.frame(wks)

    text = output.read_text(encoding="utf-8")
    required = [
        "<svg",
        "<rect",
        "<polyline",
        "<circle",
        "<text",
        "map panel 1",
        "map panel 4",
        "gsn_csm_map",
    ]
    missing = [item for item in required if item not in text]
    if missing:
        raise RuntimeError(f"Map panel SVG missing required content: {missing}")

    print(f"✅ map panel SVG smoke passed: {output}")
    print(f"✅ panel layout: {panel.resources['layout'].nrows} rows x {panel.resources['layout'].ncols} columns")
    print(f"✅ panel children: {len(panel.children)}")
    print(f"✅ workstation children: {len(wks.children)}")
    print(f"✅ frame_count: {wks.frame_count}")


if __name__ == "__main__":
    main()
