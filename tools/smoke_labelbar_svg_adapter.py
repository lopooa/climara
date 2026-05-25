from climara.graphics._labelbar_object import HluLabelBar, build_hlu_labelbar
from climara.graphics._labelbar_svg_adapter import (
    labelbar_to_svg_primitives,
    ndc_to_svg_point,
)


def close(a, b):
    assert abs(a - b) < 1.0e-12, (a, b)


def close_point(point, expected):
    close(point.x, expected[0])
    close(point.y, expected[1])


def main():
    p = ndc_to_svg_point(0.1, 0.8, 1000.0, 760.0)
    close_point(p, (100.0, 152.0))

    obj = build_hlu_labelbar(
        rect=(0.1, 0.8, 0.8, 0.3),
        colors=("c0", "c1", "c2", "c3"),
        labels=("A", "B", "C"),
        resources={"EndStyle": "IncludeOuterBoxes"},
    )

    geom = obj.compute_geometry()
    prim = labelbar_to_svg_primitives(obj, 1000.0, 1000.0)

    assert len(prim.polygons) == 4
    assert len(prim.lines) == 3
    assert len(prim.texts) == 3
    assert prim.orientation == geom.orientation
    assert prim.label_alignment == geom.label_alignment
    assert prim.label_position == geom.label_position

    first_poly = prim.polygons[0]
    assert first_poly.fill == "c0"
    close_point(
        first_poly.points[0],
        (geom.adj_bar.l * 1000.0, (1.0 - geom.adj_bar.b) * 1000.0),
    )
    close_point(
        first_poly.points[2],
        (geom.box_locs[1] * 1000.0, (1.0 - geom.adj_bar.t) * 1000.0),
    )

    first_line = prim.lines[0]
    close(first_line.p1.x, geom.box_locs[1] * 1000.0)
    close(first_line.p1.y, (1.0 - geom.adj_bar.b) * 1000.0)
    close(first_line.p2.x, geom.box_locs[1] * 1000.0)
    close(first_line.p2.y, (1.0 - geom.adj_bar.t) * 1000.0)

    first_text = prim.texts[0]
    assert first_text.text == "A"
    close(first_text.x, geom.label_text_positions[0].x * 1000.0)
    close(first_text.y, (1.0 - geom.label_text_positions[0].y) * 1000.0)
    close(first_text.angle, geom.label_angle)

    ext = build_hlu_labelbar(
        rect=(0.1, 0.8, 0.8, 0.3),
        colors=("e0", "e1", "e2", "e3"),
        labels=("min", "a", "b", "c", "max"),
        resources={
            "EndStyle": "IncludeMinMaxLabels",
            "lbBoxEndCapStyle": "TriangleBothEnds",
        },
    )
    ext_geom = ext.compute_geometry()
    ext_prim = labelbar_to_svg_primitives(ext, 1000.0, 1000.0)

    assert len(ext_prim.polygons) == 4
    assert len(ext_prim.lines) == 3
    assert len(ext_prim.texts) == 5
    assert ext_prim.texts[0].text == "min"
    assert ext_prim.texts[-1].text == "max"
    close(ext_prim.texts[0].x, ext_geom.label_text_positions[0].x * 1000.0)
    close(ext_prim.texts[-1].x, ext_geom.label_text_positions[-1].x * 1000.0)

    vertical = HluLabelBar(
        rect=(0.2, 0.9, 0.2, 0.6),
        colors=("v0", "v1", "v2"),
        labels=("V0", "V1", "V2"),
        resources={
            "lbBoxCount": 3,
            "lbOrientation": "Vertical",
            "lbLabelAlignment": "BoxCenters",
            "lbLabelAngleF": -30.0,
        },
    )
    vgeom = vertical.compute_geometry()
    vprim = labelbar_to_svg_primitives(vertical, 1000.0, 1000.0)

    assert len(vprim.polygons) == 3
    assert len(vprim.lines) == 2
    assert len(vprim.texts) == 3
    first_vline = vprim.lines[0]
    close(first_vline.p1.x, vgeom.adj_bar.l * 1000.0)
    close(first_vline.p1.y, (1.0 - vgeom.box_locs[1]) * 1000.0)
    close(first_vline.p2.x, vgeom.adj_bar.r * 1000.0)
    close(first_vline.p2.y, (1.0 - vgeom.box_locs[1]) * 1000.0)

    assert vprim.texts[0].text == "V0"
    close(vprim.texts[0].x, vgeom.label_text_positions[0].x * 1000.0)
    close(vprim.texts[0].y, (1.0 - vgeom.label_text_positions[0].y) * 1000.0)
    close(vprim.texts[0].angle, 330.0)

    class LegacyLevelLabelBar:
        rect = (0.1, 0.8, 0.8, 0.3)
        colors = ("l0", "l1", "l2")
        labels = ()
        resources = {
            "lbOrientation": "Horizontal",
            "lbBoxCount": 3,
            "lbLabelAlignment": "InteriorEdges",
            "levels": (-5, 0),
        }

    legacy = LegacyLevelLabelBar()
    legacy_prim = labelbar_to_svg_primitives(legacy, 1000.0, 1000.0)
    assert [item.text for item in legacy_prim.texts] == ["-5", "0"]

    class LegacyLbLevelsLabelBar:
        rect = (0.1, 0.8, 0.8, 0.3)
        colors = ("q0", "q1", "q2")
        labels = ()
        resources = {
            "lbOrientation": "Horizontal",
            "lbBoxCount": 3,
            "lbLabelAlignment": "InteriorEdges",
            "lbLevels": ("A", "F"),
        }

    legacy_lb = LegacyLbLevelsLabelBar()
    legacy_lb_prim = labelbar_to_svg_primitives(legacy_lb, 1000.0, 1000.0)
    assert [item.text for item in legacy_lb_prim.texts] == ["A", "F"]

    print("✅ LabelBar SVG adapter smoke passed")
    print("✅ NDC LabelBar geometry converts to SVG primitive coordinates without touching renderer")


if __name__ == "__main__":
    main()
