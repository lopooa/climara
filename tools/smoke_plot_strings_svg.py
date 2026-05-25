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

    out_base = Path("outputs") / "figures" / "plot_strings_svg_smoke"

    wks = cgr.gsn_open_wks(
        "svg",
        out_base,
        resources={
            "wkWidth": 1100,
            "wkHeight": 760,
            "wkBackgroundColor": "white",
        },
    )

    plots = []
    for idx, offset in enumerate([-1.2, -0.2, 0.8, 1.8], start=1):
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
            "tiMainString": f"Mode {idx}",
            "gsnLeftString": "OBS",
            "gsnRightString": f"{1979 + idx}-{1988 + idx}",
        }

        plot = cgr.gsn_csm_contour_map(wks, _field(offset), res)
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
            "gsnPanelYWhiteSpacePercent": 12,
            "box_color": "#e6e6e6",
            "gsnDraw": True,
            "gsnFrame": False,
        },
    )

    cgr.gsn_text_ndc(
        wks,
        "plot strings smoke",
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
        "Mode 1",
        "Mode 4",
        "OBS",
        "1980-1989",
        "1983-1992",
        "plot strings smoke",
    ]
    missing = [item for item in required if item not in text]
    if missing:
        raise RuntimeError(f"plot strings SVG missing required content: {missing}")

    print(f"✅ plot strings smoke passed: {output}")
    print(f"✅ panel layout: {panel.resources['layout'].nrows} rows x {panel.resources['layout'].ncols} columns")
    print(f"✅ workstation children: {len(wks.children)}")
    print(f"✅ frame_count: {wks.frame_count}")


if __name__ == "__main__":
    main()
