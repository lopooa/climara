import numpy as np
import climara.graphics as cgr
from climara.graphics._labelbar_svg_adapter import labelbar_to_svg_primitives


def main():
    lon = np.linspace(0, 357.5, 8)
    lat = np.linspace(-90, 90, 5)
    data = np.arange(lat.size * lon.size, dtype=float).reshape(lat.size, lon.size)

    plots = []
    for index in range(4):
        plot = cgr.gsn_csm_contour_map(
            None,
            data + index,
            {
                "cnFillOn": True,
                "cnLinesOn": False,
                "cnFillColors": list("ABCDEFGHIJK"),
                "cnLevels": list(range(-5, 6)),
                "lbLabelStrings": list("ABCDEFGHIJK"),
                "gsnDraw": False,
                "gsnFrame": False,
            },
        )
        plots.append(plot)

    panel = cgr.gsn_panel(
        None,
        plots,
        (2, 2),
        resources={
            "gsnPanelLabelBar": True,
            "gsnDraw": False,
            "gsnFrame": False,
        },
    )

    lb = panel.resources["labelbar"]
    geom = lb.compute_geometry()
    prim = labelbar_to_svg_primitives(lb, 1100.0, 760.0)

    print("labelbar type:", type(lb))
    print("rect:", lb.rect)
    print("perim:", (geom.perim.l, geom.perim.r, geom.perim.b, geom.perim.t))
    print("inside:", 0 <= geom.perim.b <= 1 and 0 <= geom.perim.t <= 1)

    print("box_count:", lb.box_count)
    print("label_alignment:", lb.label_alignment)
    print("EndStyle:", lb.resources.get("EndStyle"))
    print("cnLabelBarEndStyle:", lb.resources.get("cnLabelBarEndStyle"))

    print("fill_colors:", lb.fill_colors)
    print("labels:", lb.labels)
    print("label_strings:", lb.label_strings)
    print("visible_label_strings:", lb.visible_label_strings)
    print("resources levels:", lb.resources.get("levels"))

    print("primitive texts:", tuple(item.text for item in prim.texts))
    print("primitive polygon count:", len(prim.polygons))
    print("primitive line count:", len(prim.lines))

    assert lb.fill_colors, "fill_colors is empty"
    assert lb.labels, "labels is empty"
    assert lb.label_strings, "label_strings is empty"
    assert 0 <= geom.perim.b <= 1 and 0 <= geom.perim.t <= 1, "LabelBar perim outside NDC canvas"

    print("✅ compact panel labelbar source check passed")


if __name__ == "__main__":
    main()
