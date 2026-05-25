from __future__ import annotations

from pathlib import Path


def _make_demo_plot(cgr, title: str, x0: float, y0: float):
    plot = cgr.HluObject(name=title)

    plot.add_child(
        cgr.HluPolygon(
            x=[x0, x0 + 0.18, x0 + 0.18, x0],
            y=[y0, y0, y0 + 0.12, y0 + 0.12],
            resources={
                "gsFillColor": "#f7f7f7",
                "gsLineColor": "#333333",
                "gsLineThicknessF": 1.0,
            },
        )
    )

    plot.add_child(
        cgr.HluPolyline(
            x=[x0 + 0.02, x0 + 0.06, x0 + 0.10, x0 + 0.14, x0 + 0.17],
            y=[y0 + 0.03, y0 + 0.09, y0 + 0.05, y0 + 0.10, y0 + 0.07],
            resources={
                "gsLineColor": "#0055aa",
                "gsLineThicknessF": 2.0,
            },
        )
    )

    plot.add_child(
        cgr.HluTextItem(
            text=title,
            x=x0 + 0.09,
            y=y0 + 0.15,
            resources={
                "txFontHeightF": 0.018,
                "txFontColor": "#111111",
                "txJust": "CenterCenter",
            },
        )
    )

    return plot


def main() -> None:
    import climara.graphics as cgr

    out_base = Path("outputs") / "figures" / "panel_svg_smoke"

    wks = cgr.gsn_open_wks(
        "svg",
        out_base,
        resources={
            "wkWidth": 1000,
            "wkHeight": 760,
            "wkBackgroundColor": "white",
        },
    )

    plots = [
        _make_demo_plot(cgr, "panel 1", 0.15, 0.58),
        _make_demo_plot(cgr, "panel 2", 0.55, 0.58),
        _make_demo_plot(cgr, "panel 3", 0.15, 0.25),
        _make_demo_plot(cgr, "panel 4", 0.55, 0.25),
    ]

    panel = cgr.gsn_panel(
        wks,
        plots,
        resources={
            "gsnPanelRows": 2,
            "gsnPanelColumns": 2,
            "gsnPanelLeft": 0.08,
            "gsnPanelRight": 0.94,
            "gsnPanelBottom": 0.10,
            "gsnPanelTop": 0.88,
            "gsnPanelXWhiteSpacePercent": 6,
            "gsnPanelYWhiteSpacePercent": 8,
            "box_color": "#dddddd",
            "gsnDraw": True,
            "gsnFrame": False,
        },
    )

    cgr.gsn_text_ndc(
        wks,
        "gsn_panel -> workstation -> SVG",
        0.50,
        0.95,
        {
            "txFontHeightF": 0.028,
            "txFontColor": "#111111",
            "txJust": "CenterCenter",
        },
    )

    output = cgr.frame(wks)

    if not output.exists():
        raise RuntimeError(f"Panel SVG was not created: {output}")

    text = output.read_text(encoding="utf-8")
    required = [
        "<svg",
        "<rect",
        "<polygon",
        "<polyline",
        "<text",
        "panel 1",
        "panel 4",
        "gsn_panel",
    ]
    missing = [item for item in required if item not in text]
    if missing:
        raise RuntimeError(f"Panel SVG missing required content: {missing}")

    layout = panel.resources["layout"]

    print(f"✅ panel SVG smoke passed: {output}")
    print(f"✅ panel layout: {layout.nrows} rows x {layout.ncols} columns")
    print(f"✅ panel items: {len(panel.children)}")
    print(f"✅ workstation children: {len(wks.children)}")
    print(f"✅ frame_count: {wks.frame_count}")


if __name__ == "__main__":
    main()
