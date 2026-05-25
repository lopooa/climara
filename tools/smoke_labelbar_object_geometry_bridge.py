from climara.graphics._labelbar_geometry import compute_labelbar_geometry
from climara.graphics._labelbar_object import HluLabelBar, build_hlu_labelbar
from climara.graphics._labelbar_semantics import (
    LABEL_ALIGNMENT_BOX_CENTERS,
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


def same_geometry(a, b):
    assert a.orientation == b.orientation
    assert a.label_position == b.label_position
    assert a.label_alignment == b.label_alignment
    assert a.label_stride == b.label_stride
    assert a.label_draw_count == b.label_draw_count
    assert a.visible_label_strings == b.visible_label_strings
    close_tuple(a.label_locs, b.label_locs)
    close(a.label_const_pos, b.label_const_pos)
    close_tuple((a.bar.l, a.bar.r, a.bar.b, a.bar.t), (b.bar.l, b.bar.r, b.bar.b, b.bar.t))
    close_tuple((a.labels_area.l, a.labels_area.r, a.labels_area.b, a.labels_area.t), (b.labels_area.l, b.labels_area.r, b.labels_area.b, b.labels_area.t))


def main():
    hlu_default = HluLabelBar(resources={"lbBoxCount": 4})
    hlu_geom = hlu_default.compute_geometry()
    standalone_hlu_geom = compute_labelbar_geometry(hlu_default)
    same_geometry(hlu_geom, standalone_hlu_geom)

    assert hlu_geom.orientation == ORIENTATION_VERTICAL
    assert hlu_geom.label_position == "Right"
    assert hlu_geom.label_alignment == LABEL_ALIGNMENT_BOX_CENTERS
    assert hlu_geom.visible_label_strings == ("Label_0", "Label_1", "Label_2", "Label_3")

    gsn_created = build_hlu_labelbar(
        rect=(0.1, 0.8, 0.8, 0.3),
        colors=("c0", "c1", "c2", "c3"),
        labels=("A", "B", "C"),
        resources={},
    )
    gsn_geom = gsn_created.compute_geometry()
    standalone_gsn_geom = compute_labelbar_geometry(gsn_created)
    same_geometry(gsn_geom, standalone_gsn_geom)

    assert gsn_geom.orientation == ORIENTATION_HORIZONTAL
    assert gsn_geom.label_position == "Bottom"
    assert gsn_geom.label_alignment == LABEL_ALIGNMENT_INTERIOR_EDGES
    assert gsn_geom.visible_label_strings == ("A", "B", "C")

    include_minmax = build_hlu_labelbar(
        rect=(0.1, 0.8, 0.8, 0.3),
        colors=("c0", "c1", "c2", "c3"),
        labels=("min", "a", "b", "c", "max"),
        resources={"EndStyle": "IncludeMinMaxLabels"},
    )
    minmax_geom = include_minmax.compute_geometry()

    assert minmax_geom.label_alignment == LABEL_ALIGNMENT_EXTERNAL_EDGES
    assert minmax_geom.visible_label_strings == ("min", "a", "b", "c", "max")
    close_tuple(minmax_geom.label_locs, (0.192, 0.346, 0.5, 0.654, 0.808))

    stride = build_hlu_labelbar(
        rect=(0.1, 0.8, 0.8, 0.3),
        colors=("s0", "s1", "s2", "s3", "s4"),
        labels=("S0", "S1", "S2", "S3", "S4"),
        resources={"lbLabelAlignment": "BoxCenters", "lbLabelStride": 2},
    )
    stride_geom = stride.compute_geometry()

    assert stride_geom.visible_label_strings == ("S0", "S2", "S4")
    close_tuple(stride_geom.label_locs, (0.192, 0.5, 0.808))

    print("✅ LabelBar object-geometry bridge smoke passed")
    print("✅ HluLabelBar.compute_geometry returns the audited NCL geometry layer")


if __name__ == "__main__":
    main()
