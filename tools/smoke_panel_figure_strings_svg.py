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


def _make_plots(cgr, wks, colors):
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
    return plots


def _figure_string_children(plot):
    return [
        child for child in getattr(plot, "children", [])
        if getattr(child, "resources", {}).get("climaraPanelFigureString") is True
    ]


def main() -> None:
    import climara.graphics as cgr
    import climara.graphics._render_svg as svg

    out_base = Path("outputs") / "figures" / "panel_figure_strings_svg_smoke"

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
        resources={
            "gsnPanelRows": 2,
            "gsnPanelColumns": 2,
            "gsnPanelLeft": 0.08,
            "gsnPanelRight": 0.94,
            "gsnPanelBottom": 0.17,
            "gsnPanelTop": 0.86,
            "gsnPanelXWhiteSpacePercent": 6,
            "gsnPanelYWhiteSpacePercent": 12,
            "gsnPanelFigureStrings": ["(a)", "(b)", "(c)", "(d)"],
            "gsnPanelFigureStringsJust": "TopLeft",
            "gsnPanelFigureStringsFontHeightF": 0.014,
            "gsnPanelFigureStringsFontColor": "#111111",
            "gsnPanelMainString": "panel figure strings smoke",
            "gsnPanelMainFontHeightF": 0.027,
            "gsnDraw": True,
            "gsnFrame": False,
        },
    )

    for plot in plots:
        figure_items = _figure_string_children(plot)
        if len(figure_items) != 1:
            raise RuntimeError("each plot must receive exactly one figure string item")

        item = figure_items[0]
        res = item.resources

        if res.get("climaraTextRegion") != "data":
            raise RuntimeError("figure string must be attached to the data region")

        if res.get("amZone") != 0:
            raise RuntimeError("figure string must use amZone=0")

        if res.get("amJust") != "topleft":
            raise RuntimeError("gsnPanelFigureStringsJust was not converted to amJust=topleft")

        regions = svg._plot_regions(plot)
        local_x, local_y, text_just = svg._panel_figure_string_position(item, regions["data"])

        if not (0.0 <= local_x <= 0.08):
            raise RuntimeError(f"TopLeft local x is not using NCL am offset: {local_x}")

        if not (0.92 <= local_y <= 1.0):
            raise RuntimeError(f"TopLeft local y is not using NCL am offset: {local_y}")

        if text_just != "TopLeft":
            raise RuntimeError(f"text just should be TopLeft, got {text_just}")

    output = cgr.frame(wks)

    text = output.read_text(encoding="utf-8")
    required = [
        "<svg",
        "panel figure strings smoke",
        "(a)",
        "(b)",
        "(c)",
        "(d)",
        "Mode 1",
        "Mode 4",
    ]
    missing = [item for item in required if item not in text]
    if missing:
        raise RuntimeError(f"panel figure strings SVG missing: {missing}")

    print(f"✅ panel figure strings smoke passed: {output}")
    print("✅ gsnPanelFigureStrings follows NCL amZone/amJust/amParallelPosF/amOrthogonalPosF semantics")
    print(f"✅ panel layout: {panel.resources['layout'].nrows} rows x {panel.resources['layout'].ncols} columns")
    print(f"✅ frame_count: {wks.frame_count}")


if __name__ == "__main__":
    main()
