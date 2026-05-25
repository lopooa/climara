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

    out_base = Path("outputs") / "figures" / "panel_ncl_layout_semantics_smoke"

    wks = cgr.gsn_open_wks(
        "svg",
        out_base,
        resources={
            "wkWidth": 1100,
            "wkHeight": 760,
            "wkBackgroundColor": "white",
        },
    )

    plots = _make_plots(cgr, wks, colors)
    wks.clear()

    panel = cgr.gsn_panel(
        wks,
        plots,
        (2, 2),
        resources={
            "gsnPanelMainString": "NCL layout semantics smoke",
            "gsnPanelMainFontHeightF": 0.027,
            "gsnPanelXWhiteSpacePercent": 1.0,
            "gsnPanelYWhiteSpacePercent": 1.0,
            "gsnPanelFigureStrings": ["(a)", "(b)", "(c)", "(d)"],
            "gsnPanelFigureStringsJust": "TopLeft",
            "gsnPanelLabelBar": True,
            "lbLevels": [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5],
            "lbFillColors": colors,
            "gsnDraw": True,
            "gsnFrame": False,
        },
    )

    layout = panel.resources["layout"]

    if layout.nrows != 2 or layout.ncols != 2:
        raise RuntimeError("NCL dims=(2,2) was not used.")

    if layout.bounds[0] != 0.0 or layout.bounds[1] != 1.0:
        raise RuntimeError("NCL default panel left/right bounds were not used.")

    expected_top = 0.96 - 0.027
    if abs(layout.bounds[3] - expected_top) > 1e-9:
        raise RuntimeError("main string did not reserve panel top using NCL rule.")

    if len(layout.rects) != 4:
        raise RuntimeError("panel did not create four plot viewports.")

    if not (0.0 < layout.scale <= 1.0):
        raise RuntimeError("layout scale is outside expected range.")

    for plot in plots:
        res = plot.resources
        for key in ["vpXF", "vpYF", "vpWidthF", "vpHeightF"]:
            if key not in res:
                raise RuntimeError(f"plot missing viewport resource {key}")

    output = cgr.frame(wks)

    text = output.read_text(encoding="utf-8")
    required = [
        "<svg",
        "NCL layout semantics smoke",
        "Mode 1",
        "Mode 4",
        "(a)",
        "(d)",
        "-5",
        "0",
        "5",
    ]
    missing = [item for item in required if item not in text]
    if missing:
        raise RuntimeError(f"NCL panel layout SVG missing: {missing}")

    print(f"✅ NCL panel layout semantics smoke passed: {output}")
    print(f"✅ bounds: {layout.bounds}")
    print(f"✅ row_spec: {layout.row_spec}")
    print(f"✅ scale: {layout.scale:.6f}")
    print(f"✅ whitespace: {layout.whitespace}")
    print(f"✅ labelbar_rect: {layout.labelbar_rect}")
    print(f"✅ frame_count: {wks.frame_count}")


if __name__ == "__main__":
    main()
