from __future__ import annotations

from pathlib import Path


def _field(offset: float) -> list[list[float]]:
    rows: list[list[float]] = []
    for j in range(10):
        row: list[float] = []
        for i in range(14):
            value = ((i - 6.5) / 2.8) - ((j - 4.5) / 3.5) + offset
            row.append(value)
        rows.append(row)
    return rows


def main() -> None:
    import climara.graphics as cgr

    out_base = Path("outputs") / "figures" / "panel_main_string_svg_smoke"

    wks = cgr.gsn_open_wks(
        "svg",
        out_base,
        resources={
            "wkWidth": 1100,
            "wkHeight": 760,
            "wkBackgroundColor": "white",
        },
    )

    levels = [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]
    colors = [
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
    ]

    plots = []
    for idx, offset in enumerate([-1.2, -0.2, 0.8, 1.8], start=1):
        plot = cgr.gsn_csm_contour_map(
            wks,
            _field(offset),
            {
                "cnFillOn": True,
                "cnLinesOn": True,
                "cnLevelSelectionMode": "ManualLevels",
                "cnMinLevelValF": -5,
                "cnMaxLevelValF": 5,
                "cnLevelSpacingF": 1,
                "cnFillPalette": colors,
                "tiMainString": f"Mode {idx}",
                "gsnLeftString": "OBS",
                "gsnRightString": f"{1979 + idx}-{1988 + idx}",
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
            "gsnPanelBottom": 0.17,
            "gsnPanelTop": 0.86,
            "gsnPanelXWhiteSpacePercent": 6,
            "gsnPanelYWhiteSpacePercent": 12,
            "gsnPanelLabelBar": True,
            "lbLevels": levels,
            "lbFillColors": colors,
            "lbLabelFontHeightF": 0.012,
            "lbTickLengthF": 0.008,
            "lbLabelGapF": 0.008,
            "pmLabelBarWidthF": 0.56,
            "pmLabelBarHeightF": 0.035,
            "gsnPanelLabelBarBottom": 0.055,
            "gsnPanelMainString": "panel main string smoke",
            "gsnPanelMainFontHeightF": 0.027,
            "gsnPanelMainPosYF": 0.90,
            "gsnPanelMainPosXF": 0.50,
            "box_color": "#e6e6e6",
            "gsnDraw": True,
            "gsnFrame": False,
        },
    )

    main_string = panel.resources.get("main_string")
    if main_string is None:
        raise RuntimeError("panel main string was not attached to panel resources.")

    if abs(main_string.y - 0.90) > 1e-9:
        raise RuntimeError("gsnPanelMainPosYF was not used.")

    if abs(main_string.x - 0.50) > 1e-9:
        raise RuntimeError("gsnPanelMainPosXF was not used.")

    if abs(float(main_string.resources["txFontHeightF"]) - 0.027) > 1e-9:
        raise RuntimeError("gsnPanelMainFontHeightF was not mapped to txFontHeightF.")

    output = cgr.frame(wks)

    text = output.read_text(encoding="utf-8")
    required = [
        "<svg",
        "panel main string smoke",
        "Mode 1",
        "Mode 4",
        "-5",
        "0",
        "5",
    ]
    missing = [item for item in required if item not in text]
    if missing:
        raise RuntimeError(f"panel main string SVG missing: {missing}")

    print(f"✅ panel main string smoke passed: {output}")
    print("✅ gsnPanelMainString uses NCL gsnPanelMainPosYF/gsnPanelMainPosXF resource names")
    print(f"✅ panel layout: {panel.resources['layout'].nrows} rows x {panel.resources['layout'].ncols} columns")
    print(f"✅ panel children: {len(panel.children)}")
    print(f"✅ frame_count: {wks.frame_count}")


if __name__ == "__main__":
    main()
