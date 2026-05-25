from __future__ import annotations

from pathlib import Path


def _field(offset: float) -> list[list[float]]:
    rows: list[list[float]] = []
    for j in range(8):
        row: list[float] = []
        for i in range(10):
            row.append(float(i - j) + offset)
        rows.append(row)
    return rows


def _make_plots(cgr, wks, colors):
    plots = []
    for idx, offset in enumerate([-1.0, 0.0, 1.0, 2.0], start=1):
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
            },
        )
        plots.append(plot)
    return plots


def main() -> None:
    import climara.graphics as cgr

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

    out_base = Path("outputs") / "figures" / "panel_rowspec_ncl_semantics_smoke"

    wks = cgr.gsn_open_wks(
        "svg",
        out_base,
        resources={
            "wkWidth": 1100,
            "wkHeight": 820,
            "wkBackgroundColor": "white",
        },
    )

    plots = _make_plots(cgr, wks, colors)
    wks.clear()

    panel = cgr.gsn_panel(
        wks,
        plots,
        [1, 2, 1],
        resources={
            "gsnPanelRowSpec": True,
            "gsnPanelMainString": "NCL row spec smoke",
            "gsnPanelMainFontHeightF": 0.026,
            "gsnPanelXWhiteSpacePercent": 1.0,
            "gsnPanelYWhiteSpacePercent": 1.0,
            "gsnPanelFigureStrings": ["(a)", "(b)", "(c)", "(d)"],
            "gsnPanelFigureStringsJust": "TopLeft",
            "gsnDraw": True,
            "gsnFrame": False,
        },
    )

    layout = panel.resources["layout"]
    rects = layout.rects

    if layout.nrows != 3:
        raise RuntimeError(f"row spec should create 3 rows, got {layout.nrows}")

    if layout.ncols != 2:
        raise RuntimeError(f"row spec max columns should be 2, got {layout.ncols}")

    if layout.row_spec != [1, 2, 1]:
        raise RuntimeError(f"row spec was not preserved: {layout.row_spec}")

    if len(rects) != 4:
        raise RuntimeError(f"expected 4 plot rectangles, got {len(rects)}")

    first_row_x = rects[0][0]
    second_row_left_x = rects[1][0]
    second_row_right_x = rects[2][0]
    third_row_x = rects[3][0]

    if not (second_row_left_x < first_row_x < second_row_right_x):
        raise RuntimeError("first row single panel was not centered relative to the two-panel row")

    if abs(first_row_x - third_row_x) > 1.0e-9:
        raise RuntimeError("single-panel rows should have the same centered x position")

    if not (rects[0][1] > rects[1][1] > rects[3][1]):
        raise RuntimeError("row order should proceed from top to bottom")

    output = cgr.frame(wks)

    text = output.read_text(encoding="utf-8")
    required = [
        "<svg",
        "NCL row spec smoke",
        "Mode 1",
        "Mode 4",
        "(a)",
        "(d)",
    ]
    missing = [item for item in required if item not in text]
    if missing:
        raise RuntimeError(f"NCL row spec SVG missing: {missing}")

    print(f"✅ NCL panel row spec smoke passed: {output}")
    print(f"✅ nrows/ncols: {layout.nrows} x {layout.ncols}")
    print(f"✅ row_spec: {layout.row_spec}")
    print(f"✅ scale: {layout.scale:.6f}")
    print(f"✅ bounds: {layout.bounds}")
    print(f"✅ whitespace: {layout.whitespace}")
    print(f"✅ rects: {layout.rects}")
    print(f"✅ frame_count: {wks.frame_count}")


if __name__ == "__main__":
    main()
