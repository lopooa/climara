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


def main() -> None:
    import climara.graphics as cgr

    out_base = Path("outputs") / "figures" / "panel_labelbar_ncl_contour_info_smoke"

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

    levels = [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]
    labels = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K"]

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
    for idx, offset in enumerate([-1.0, 0.0, 1.0, 2.0], start=1):
        plot = cgr.gsn_csm_contour_map(
            wks,
            _field(offset),
            {
                "plot_type": "contour",
                "cnFillOn": True,
                "cnLinesOn": True,
                "cnLevelSelectionMode": "ManualLevels",
                "cnMinLevelValF": -5,
                "cnMaxLevelValF": 5,
                "cnLevelSpacingF": 1,
                "cnFillPalette": colors,
                "cnFillColors": colors,
                "cnLevels": levels,
                "cnFillPatterns": [0 for _ in colors],
                "cnFillScales": [1.0 for _ in colors],
                "cnMonoFillPattern": False,
                "cnMonoFillScale": False,
                "cnMonoFillColor": False,
                "cnLabelBarEndStyle": "IncludeOuterBoxes",
                "lbBoxEndCapStyle": "RectangleEnds",
                "lbLabelAlignment": "InteriorEdges",
                "lbLabelStrings": labels,
                "tiMainString": f"Mode {idx}",
                "gsnLeftString": "OBS",
            },
        )
        plots.append(plot)

    wks.clear()

    panel = cgr.gsn_panel(
        wks,
        plots,
        (2, 2),
        resources={
            "gsnPanelMainString": "panel labelbar NCL contour info smoke",
            "gsnPanelMainFontHeightF": 0.026,
            "gsnPanelLabelBar": True,
            "gsnPanelXWhiteSpacePercent": 1.0,
            "gsnPanelYWhiteSpacePercent": 1.0,
            "gsnDraw": True,
            "gsnFrame": False,
        },
    )

    labelbar = panel.resources.get("labelbar")
    if labelbar is None:
        raise RuntimeError("shared labelbar was not created")

    res = labelbar.resources

    if list(res.get("colors", [])) != colors:
        raise RuntimeError("labelbar colors were not taken from cnFillColors")

    if list(res.get("levels", [])) != levels:
        raise RuntimeError("labelbar levels were not taken from cnLevels")

    if list(res.get("labels", [])) != labels:
        raise RuntimeError("labelbar labels were not taken from lbLabelStrings")

    if res.get("lbLabelAlignment") != "InteriorEdges":
        raise RuntimeError("lbLabelAlignment was not propagated")

    if res.get("lbBoxEndCapStyle") != "RectangleEnds":
        raise RuntimeError("lbBoxEndCapStyle was not propagated")

    if res.get("EndStyle") != "IncludeOuterBoxes":
        raise RuntimeError("cnLabelBarEndStyle was not propagated")

    if res.get("SubsetStuff") is not True:
        raise RuntimeError("SubsetStuff should be True for contour plot labelbar info")

    output = cgr.frame(wks)
    text = output.read_text(encoding="utf-8")

    required = [
        "<svg",
        "panel labelbar NCL contour info smoke",
        "Mode 1",
        "Mode 4",
        "A",
        "F",
        "J",
    ]
    missing = [item for item in required if item not in text]
    if missing:
        raise RuntimeError(f"NCL contour labelbar SVG missing: {missing}")

    print(f"✅ panel labelbar NCL contour info smoke passed: {output}")
    print("✅ cnFillColors -> shared labelbar colors")
    print("✅ cnLevels -> shared labelbar levels")
    print("✅ lbLabelStrings -> shared labelbar labels")
    print(f"✅ labelbar rect: {labelbar.rect}")
    print(f"✅ frame_count: {wks.frame_count}")


if __name__ == "__main__":
    main()
