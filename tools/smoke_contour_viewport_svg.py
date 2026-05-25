from __future__ import annotations

from pathlib import Path


def _field(offset: float) -> list[list[float]]:
    rows: list[list[float]] = []
    for j in range(12):
        row: list[float] = []
        for i in range(18):
            value = ((i - 8.5) / 3.0) - ((j - 5.5) / 4.0) + offset
            row.append(value)
        rows.append(row)
    return rows


def main() -> None:
    import climara.graphics as cgr

    out_base = Path("outputs") / "figures" / "contour_viewport_svg_smoke"

    wks = cgr.gsn_open_wks(
        "svg",
        out_base,
        resources={
            "wkWidth": 1100,
            "wkHeight": 760,
            "wkBackgroundColor": "white",
        },
    )

    res = {
        "cnFillOn": True,
        "cnLinesOn": True,
        "cnLevelSelectionMode": "ManualLevels",
        "cnMinLevelValF": -5,
        "cnMaxLevelValF": 5,
        "cnLevelSpacingF": 1,
        "cnFillPalette": [
            "#313695",
            "#4575b4",
            "#74add1",
            "#abd9e9",
            "#e0f3f8",
            "#ffffbf",
            "#fee090",
            "#fdae61",
            "#f46d43",
            "#d73027",
            "#a50026",
        ],
    }

    plots = []
    for index, offset in enumerate([-1.5, -0.5, 0.5, 1.5], start=1):
        plot = cgr.gsn_csm_contour_map(wks, _field(offset), res)
        cgr.gsn_text_ndc(
            plot,
            f"panel {index}",
            0.50,
            1.06,
            {
                "txFontHeightF": 0.016,
                "txFontColor": "#111111",
                "txJust": "CenterCenter",
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
            "gsnPanelBottom": 0.11,
            "gsnPanelTop": 0.86,
            "gsnPanelXWhiteSpacePercent": 6,
            "gsnPanelYWhiteSpacePercent": 10,
            "box_color": "#e5e5e5",
            "gsnDraw": True,
            "gsnFrame": False,
        },
    )

    cgr.gsn_text_ndc(
        wks,
        "viewport-aware plot children",
        0.50,
        0.95,
        {
            "txFontHeightF": 0.027,
            "txFontColor": "#111111",
            "txJust": "CenterCenter",
        },
    )

    cgr.add_labelbar(
        wks,
        levels=[-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5],
        colors=res["cnFillPalette"],
        resources={
            "rect": (0.22, 0.045, 0.56, 0.035),
            "lbOrientation": "horizontal",
        },
    )

    output = cgr.frame(wks)

    text = output.read_text(encoding="utf-8")
    required = [
        "<svg",
        "<rect",
        "<text",
        "panel 1",
        "panel 4",
        "viewport-aware",
    ]
    missing = [item for item in required if item not in text]
    if missing:
        raise RuntimeError(f"Viewport SVG missing required content: {missing}")

    print(f"✅ viewport contour SVG smoke passed: {output}")
    print(f"✅ panel layout: {panel.resources['layout'].nrows} rows x {panel.resources['layout'].ncols} columns")
    print(f"✅ panel children: {len(panel.children)}")
    print(f"✅ workstation children: {len(wks.children)}")
    print(f"✅ frame_count: {wks.frame_count}")


if __name__ == "__main__":
    main()
