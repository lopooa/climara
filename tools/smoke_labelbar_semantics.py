from climara.graphics._labelbar_semantics import (
    END_STYLE_EXCLUDE_OUTER_BOXES,
    END_STYLE_INCLUDE_MIN_MAX_LABELS,
    END_STYLE_INCLUDE_OUTER_BOXES,
    GSN_CREATE_LABELBAR_DEFAULTS,
    LABEL_ALIGNMENT_BOX_CENTERS,
    LABEL_ALIGNMENT_EXTERNAL_EDGES,
    LABEL_ALIGNMENT_INTERIOR_EDGES,
    NCL_LABELBAR_DEFAULTS,
    label_alignment_for_end_style,
    label_count_for_alignment,
    label_indices_for_stride,
    uniform_label_axis_positions,
)


def almost_equal_tuple(actual, expected):
    assert len(actual) == len(expected), (actual, expected)
    for a, e in zip(actual, expected):
        assert abs(a - e) < 1.0e-12, (actual, expected)


def main():
    assert NCL_LABELBAR_DEFAULTS["lbOrientation"] == "Vertical"
    assert NCL_LABELBAR_DEFAULTS["lbBoxMinorExtentF"] == 0.33
    assert NCL_LABELBAR_DEFAULTS["lbLabelOffsetF"] == 0.1
    assert NCL_LABELBAR_DEFAULTS["lbLabelAlignment"] == LABEL_ALIGNMENT_BOX_CENTERS
    assert NCL_LABELBAR_DEFAULTS["lbLabelStride"] == 1
    assert NCL_LABELBAR_DEFAULTS["lbBoxEndCapStyle"] == "RectangleEnds"

    assert GSN_CREATE_LABELBAR_DEFAULTS["lbOrientation"] == "Horizontal"
    assert GSN_CREATE_LABELBAR_DEFAULTS["lbAutoManage"] is False

    assert label_count_for_alignment(4, LABEL_ALIGNMENT_BOX_CENTERS) == 4
    assert label_count_for_alignment(4, LABEL_ALIGNMENT_INTERIOR_EDGES) == 3
    assert label_count_for_alignment(4, LABEL_ALIGNMENT_EXTERNAL_EDGES) == 5

    assert label_indices_for_stride(5, LABEL_ALIGNMENT_BOX_CENTERS, 2) == (0, 2, 4)
    assert label_indices_for_stride(4, LABEL_ALIGNMENT_INTERIOR_EDGES, 2) == (0, 2)
    assert label_indices_for_stride(4, LABEL_ALIGNMENT_EXTERNAL_EDGES, 2) == (0, 2, 4)

    almost_equal_tuple(
        uniform_label_axis_positions(4, LABEL_ALIGNMENT_BOX_CENTERS),
        (0.125, 0.375, 0.625, 0.875),
    )
    almost_equal_tuple(
        uniform_label_axis_positions(4, LABEL_ALIGNMENT_INTERIOR_EDGES),
        (0.25, 0.5, 0.75),
    )
    almost_equal_tuple(
        uniform_label_axis_positions(4, LABEL_ALIGNMENT_EXTERNAL_EDGES),
        (0.1, 0.3, 0.5, 0.7, 0.9),
    )

    assert label_alignment_for_end_style(None) == LABEL_ALIGNMENT_INTERIOR_EDGES
    assert label_alignment_for_end_style(END_STYLE_INCLUDE_OUTER_BOXES) == LABEL_ALIGNMENT_INTERIOR_EDGES
    assert label_alignment_for_end_style(END_STYLE_INCLUDE_MIN_MAX_LABELS) == LABEL_ALIGNMENT_EXTERNAL_EDGES
    assert label_alignment_for_end_style(END_STYLE_EXCLUDE_OUTER_BOXES) == LABEL_ALIGNMENT_EXTERNAL_EDGES

    print("✅ LabelBar NCL semantics smoke passed")
    print("✅ defaults and label-position helpers match audited source rules")


if __name__ == "__main__":
    main()
