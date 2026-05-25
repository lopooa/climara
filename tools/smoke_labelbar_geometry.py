from climara.graphics._labelbar_geometry import compute_labelbar_geometry
from climara.graphics._labelbar_object import HluLabelBar, build_hlu_labelbar
from climara.graphics._labelbar_semantics import (
    LABEL_ALIGNMENT_EXTERNAL_EDGES,
    LABEL_ALIGNMENT_INTERIOR_EDGES,
    ORIENTATION_HORIZONTAL,
    ORIENTATION_VERTICAL,
)


def close(a, b):
    assert abs(a - b) < 1.0e-12, (a, b)


def close_tuple(actual, expected):
    assert len(actual) == len(expected), (actual, expected)
    for a, e in zip(actual, expected):
        close(a, e)


def main():
    horizontal = build_hlu_labelbar(
        rect=(0.1, 0.8, 0.8, 0.3),
        colors=("c0", "c1", "c2", "c3"),
        labels=("A", "B", "C"),
        resources={"EndStyle": "IncludeOuterBoxes"},
    )
    geom = compute_labelbar_geometry(horizontal)

    assert geom.orientation == ORIENTATION_HORIZONTAL
    assert geom.label_position == "Bottom"
    assert geom.label_alignment == LABEL_ALIGNMENT_INTERIOR_EDGES
    assert geom.label_draw_count == 3

    close_tuple((geom.perim.l, geom.perim.r, geom.perim.b, geom.perim.t), (0.1, 0.9, 0.5, 0.8))
    close_tuple(
        (geom.adj_perim.l, geom.adj_perim.r, geom.adj_perim.b, geom.adj_perim.t),
        (0.115, 0.885, 0.515, 0.785),
    )
    close(geom.bar.height, 0.0891)
    close_tuple(geom.label_locs, (0.3075, 0.5, 0.6925))
    close(geom.label_const_pos, 0.6689)
    assert geom.visible_label_strings == ("A", "B", "C")

    external = build_hlu_labelbar(
        rect=(0.1, 0.8, 0.8, 0.3),
        colors=("c0", "c1", "c2", "c3"),
        labels=("L0", "L1", "L2", "L3", "L4"),
        resources={"EndStyle": "IncludeMinMaxLabels"},
    )
    ext_geom = compute_labelbar_geometry(external)
    assert ext_geom.label_alignment == LABEL_ALIGNMENT_EXTERNAL_EDGES
    close_tuple(ext_geom.label_locs, (0.192, 0.346, 0.5, 0.654, 0.808))
    assert ext_geom.visible_label_strings == ("L0", "L1", "L2", "L3", "L4")

    stride = build_hlu_labelbar(
        rect=(0.1, 0.8, 0.8, 0.3),
        colors=("c0", "c1", "c2", "c3", "c4"),
        labels=("S0", "S1", "S2", "S3", "S4"),
        resources={"lbLabelAlignment": "BoxCenters", "lbLabelStride": 2},
    )
    stride_geom = compute_labelbar_geometry(stride)
    close_tuple(stride_geom.label_locs, (0.192, 0.5, 0.808))
    assert stride_geom.visible_label_strings == ("S0", "S2", "S4")

    vertical = HluLabelBar(
        rect=(0.2, 0.9, 0.2, 0.6),
        colors=("v0", "v1", "v2", "v3"),
        labels=("V0", "V1", "V2", "V3"),
        resources={
            "lbBoxCount": 4,
            "lbOrientation": "Vertical",
            "lbLabelAlignment": "BoxCenters",
            "lbLabelPosition": "Right",
        },
    )
    vgeom = compute_labelbar_geometry(vertical)

    assert vgeom.orientation == ORIENTATION_VERTICAL
    assert vgeom.label_position == "Right"
    close_tuple((vgeom.perim.l, vgeom.perim.r, vgeom.perim.b, vgeom.perim.t), (0.2, 0.4, 0.3, 0.9))
    close_tuple(
        (vgeom.adj_perim.l, vgeom.adj_perim.r, vgeom.adj_perim.b, vgeom.adj_perim.t),
        (0.21, 0.39, 0.31, 0.89),
    )
    close_tuple(vgeom.label_locs, (0.3825, 0.5275, 0.6725, 0.8175))
    close(vgeom.label_const_pos, 0.2874)
    assert vgeom.visible_label_strings == ("V0", "V1", "V2", "V3")

    from climara.graphics._labelbar_geometry import compute_labelbar_box_polygons

    rect_polys = compute_labelbar_box_polygons(geom)
    assert len(rect_polys) == 4
    close_tuple(rect_polys[0][0], (0.115, geom.adj_bar.b))
    close_tuple(rect_polys[0][1], (0.3075, geom.adj_bar.b))
    close_tuple(rect_polys[0][2], (0.3075, geom.adj_bar.t))
    close_tuple(rect_polys[0][3], (0.115, geom.adj_bar.t))
    close_tuple(rect_polys[0][4], (0.115, geom.adj_bar.b))

    triangle_low = build_hlu_labelbar(
        rect=(0.1, 0.8, 0.8, 0.3),
        colors=("c0", "c1", "c2"),
        labels=("L0", "L1"),
        resources={
            "EndStyle": "IncludeOuterBoxes",
            "lbBoxEndCapStyle": "TriangleLowEnd",
        },
    )
    tri_low_geom = compute_labelbar_geometry(triangle_low)
    tri_low_polys = compute_labelbar_box_polygons(tri_low_geom)
    low_mid_y = (tri_low_geom.adj_bar.t + tri_low_geom.adj_bar.b) / 2.0
    close_tuple(tri_low_polys[0][0], (tri_low_geom.box_locs[0], low_mid_y))
    close_tuple(tri_low_polys[0][1], (tri_low_geom.box_locs[1], tri_low_geom.adj_bar.b))
    close_tuple(tri_low_polys[0][2], (tri_low_geom.box_locs[1], tri_low_geom.adj_bar.t))

    triangle_high_v = HluLabelBar(
        rect=(0.2, 0.9, 0.2, 0.6),
        colors=("v0", "v1", "v2"),
        labels=("V0", "V1", "V2"),
        resources={
            "lbBoxCount": 3,
            "lbOrientation": "Vertical",
            "lbLabelAlignment": "BoxCenters",
            "lbBoxEndCapStyle": "TriangleHighEnd",
        },
    )
    tri_high_geom = compute_labelbar_geometry(triangle_high_v)
    tri_high_polys = compute_labelbar_box_polygons(tri_high_geom)
    last = tri_high_polys[-1]
    high_mid_x = (tri_high_geom.adj_bar.l + tri_high_geom.adj_bar.r) / 2.0
    close_tuple(last[0], (tri_high_geom.adj_bar.l, tri_high_geom.box_locs[-2]))
    close_tuple(last[1], (tri_high_geom.adj_bar.r, tri_high_geom.box_locs[-2]))
    close_tuple(last[2], (high_mid_x, tri_high_geom.box_locs[-1]))

    major_extent = build_hlu_labelbar(
        rect=(0.1, 0.8, 0.8, 0.3),
        colors=("m0", "m1"),
        labels=("M0",),
        resources={
            "EndStyle": "IncludeOuterBoxes",
            "lbBoxMajorExtentF": 0.5,
        },
    )
    major_geom = compute_labelbar_geometry(major_extent)
    major_polys = compute_labelbar_box_polygons(major_geom)
    first_width = major_geom.box_locs[1] - major_geom.box_locs[0]
    close(major_polys[0][0][0], major_geom.box_locs[0] + first_width * 0.25)
    close(major_polys[0][1][0], major_geom.box_locs[1] - first_width * 0.25)

    assert geom.multi_text_orientation == "YConst"
    assert geom.label_keep_end_items is False
    assert geom.label_angle == 0.0
    close_tuple(
        (geom.label_text_positions[0].x, geom.label_text_positions[0].y),
        (geom.label_locs[0], geom.label_const_pos),
    )
    assert geom.label_text_positions[0].text == "A"

    assert ext_geom.multi_text_orientation == "YConst"
    assert ext_geom.label_keep_end_items is True
    close_tuple(
        (ext_geom.label_text_positions[0].x, ext_geom.label_text_positions[0].y),
        (ext_geom.label_locs[0], ext_geom.label_const_pos),
    )

    assert vgeom.multi_text_orientation == "XConst"
    assert vgeom.label_keep_end_items is False
    close_tuple(
        (vgeom.label_text_positions[0].x, vgeom.label_text_positions[0].y),
        (vgeom.label_const_pos, vgeom.label_locs[0]),
    )
    assert vgeom.label_text_positions[0].text == "V0"

    angle_obj = HluLabelBar(
        rect=(0.2, 0.9, 0.2, 0.6),
        colors=("a", "b"),
        labels=("A0", "A1"),
        resources={
            "lbBoxCount": 2,
            "lbOrientation": "Vertical",
            "lbLabelAngleF": -45.0,
        },
    )
    angle_geom = compute_labelbar_geometry(angle_obj)
    close(angle_geom.label_angle, 315.0)

    labels_off = build_hlu_labelbar(
        rect=(0.1, 0.8, 0.8, 0.3),
        colors=("o0", "o1", "o2", "o3"),
        labels=("O0", "O1", "O2"),
        resources={
            "EndStyle": "IncludeOuterBoxes",
            "lbLabelsOn": False,
        },
    )
    labels_off_geom = compute_labelbar_geometry(labels_off)
    assert labels_off_geom.label_draw_count == 0
    assert labels_off_geom.visible_label_strings == ()
    assert labels_off_geom.label_locs == ()
    assert labels_off_geom.label_text_positions == ()
    assert labels_off_geom.label_keep_end_items is False

    labels_off_polys = compute_labelbar_box_polygons(labels_off_geom)
    assert len(labels_off_polys) == 4

    print("✅ LabelBar NCL geometry smoke passed")
    print("✅ geometry layer follows SetLabelBarGeometry / SetBoxLocations / SetLabels / DrawFilledBoxes closed subset")


if __name__ == "__main__":
    main()
