from climara.graphics._labelbar_object import HluLabelBar, build_hlu_labelbar
from climara.graphics._labelbar_semantics import (
    LABEL_ALIGNMENT_BOX_CENTERS,
    LABEL_ALIGNMENT_EXTERNAL_EDGES,
    LABEL_ALIGNMENT_INTERIOR_EDGES,
)


def almost_equal_tuple(actual, expected):
    assert len(actual) == len(expected), (actual, expected)
    for a, e in zip(actual, expected):
        assert abs(a - e) < 1.0e-12, (actual, expected)


def main():
    direct = HluLabelBar()
    assert direct.orientation == "Vertical"
    assert direct.label_alignment == LABEL_ALIGNMENT_BOX_CENTERS
    assert direct.box_count == 16
    assert direct.auto_manage is True
    assert direct.rect == (0.1, 0.1, 0.8, 0.3)

    created = build_hlu_labelbar(
        rect=(0.25, 0.02, 0.5, 0.08),
        colors=("red", "white", "blue", "black"),
        labels=("A", "B", "C"),
        resources={},
    )
    assert created.orientation == "Horizontal"
    assert created.label_alignment == LABEL_ALIGNMENT_INTERIOR_EDGES
    assert created.box_count == 4
    assert created.auto_manage is False
    assert created.labels == ("A", "B", "C")
    assert created.fill_colors == ("red", "white", "blue", "black")
    almost_equal_tuple(created.label_axis_positions, (0.25, 0.5, 0.75))

    include_minmax = build_hlu_labelbar(
        colors=(1, 2, 3, 4),
        labels=("min", "a", "b", "max"),
        resources={"EndStyle": "IncludeMinMaxLabels"},
    )
    assert include_minmax.label_alignment == LABEL_ALIGNMENT_EXTERNAL_EDGES
    assert include_minmax.box_count == 4
    almost_equal_tuple(include_minmax.label_axis_positions, (0.1, 0.3, 0.5, 0.7, 0.9))

    exclude_subset = build_hlu_labelbar(
        colors=("outer_left", "inner_a", "inner_b", "outer_right"),
        labels=("A", "B", "C", "D", "E"),
        resources={"EndStyle": "ExcludeOuterBoxes", "SubsetStuff": True},
    )
    assert exclude_subset.label_alignment == LABEL_ALIGNMENT_EXTERNAL_EDGES
    assert exclude_subset.box_count == 2
    assert exclude_subset.fill_colors == ("inner_a", "inner_b")
    almost_equal_tuple(exclude_subset.label_axis_positions, (1.0 / 6.0, 0.5, 5.0 / 6.0))

    explicit = build_hlu_labelbar(
        colors=(1, 2, 3),
        labels=("A", "B", "C"),
        resources={
            "EndStyle": "IncludeMinMaxLabels",
            "lbLabelAlignment": "InteriorEdges",
            "lbOrientation": "Vertical",
            "vpXF": 0.2,
            "vpYF": 0.8,
            "vpWidthF": 0.1,
            "vpHeightF": 0.6,
        },
    )
    assert explicit.label_alignment == LABEL_ALIGNMENT_INTERIOR_EDGES
    assert explicit.orientation == "Vertical"
    assert explicit.rect == (0.2, 0.8, 0.1, 0.6)

    positional = build_hlu_labelbar(
        (0.1, 0.2, 0.3, 0.4),
        ("c1", "c2"),
        ("L1",),
        {"EndStyle": "IncludeOuterBoxes"},
    )
    assert positional.rect == (0.1, 0.2, 0.3, 0.4)
    assert positional.label_alignment == LABEL_ALIGNMENT_INTERIOR_EDGES

    stride = build_hlu_labelbar(
        colors=("c0", "c1", "c2", "c3", "c4"),
        labels=("L0", "L1", "L2", "L3", "L4"),
        resources={"lbLabelStride": 2, "lbLabelAlignment": "BoxCenters"},
    )
    assert stride.label_count == 5
    assert stride.label_indices == (0, 2, 4)
    assert stride.label_draw_count == 3
    assert stride.visible_label_strings == ("L0", "L2", "L4")
    almost_equal_tuple(stride.label_axis_positions, (0.1, 0.5, 0.9))

    fallback_labels = HluLabelBar(
        colors=("a", "b", "c"),
        labels=("only_first",),
        resources={"lbBoxCount": 3},
    )
    assert fallback_labels.label_indices == (0, 1, 2)
    assert fallback_labels.visible_label_strings == ("only_first", "Label_1", "Label_2")

    default_labels = HluLabelBar(resources={"lbBoxCount": 3})
    assert default_labels.visible_label_strings == ("Label_0", "Label_1", "Label_2")

    wrapper_sources = build_hlu_labelbar(
        resources={
            "colors": tuple("ABCDEFGHIJK"),
            "labels": tuple("ABCDEFGHIJK"),
            "levels": tuple(range(-5, 6)),
            "lbFillColors": (),
            "lbLabelStrings": (),
            "lbBoxCount": 16,
        },
    )
    assert wrapper_sources.box_count == 11
    assert wrapper_sources.fill_colors == tuple("ABCDEFGHIJK")
    assert wrapper_sources.labels == tuple("ABCDEFGHIJK")
    assert wrapper_sources.label_strings == tuple("ABCDEFGHIJK")
    assert wrapper_sources.resources["lbFillColors"] == tuple("ABCDEFGHIJK")
    assert wrapper_sources.resources["lbLabelStrings"] == tuple("ABCDEFGHIJK")
    assert wrapper_sources.resources["colors"] == tuple("ABCDEFGHIJK")
    assert wrapper_sources.resources["labels"] == tuple("ABCDEFGHIJK")
    assert wrapper_sources.visible_label_strings[:3] == ("A", "B", "C")

    resource_rect = build_hlu_labelbar(
        resources={
            "rect": (0.25, 0.08455882352941176, 0.5, 0.08088235294117646),
            "colors": ("r0", "r1", "r2"),
            "labels": ("R0", "R1"),
            "lbLabelAlignment": "InteriorEdges",
        },
    )
    assert resource_rect.rect == (0.25, 0.08455882352941176, 0.5, 0.08088235294117646)
    assert resource_rect.resources["rect"] == resource_rect.rect
    assert resource_rect.resources["vpXF"] == resource_rect.rect[0]
    assert resource_rect.resources["vpYF"] == resource_rect.rect[1]
    assert resource_rect.resources["vpWidthF"] == resource_rect.rect[2]
    assert resource_rect.resources["vpHeightF"] == resource_rect.rect[3]

    explicit_rect_wins = build_hlu_labelbar(
        rect=(0.1, 0.4, 0.8, 0.3),
        resources={
            "rect": (0.25, 0.08455882352941176, 0.5, 0.08088235294117646),
            "colors": ("e0", "e1"),
            "labels": ("E0",),
        },
    )
    assert explicit_rect_wins.rect == (0.1, 0.4, 0.8, 0.3)

    level_label_source = build_hlu_labelbar(
        resources={
            "colors": ("c0", "c1", "c2", "c3"),
            "levels": (-5, 0, 5),
            "lbLabelAlignment": "InteriorEdges",
        },
    )
    assert level_label_source.box_count == 4
    assert level_label_source.label_strings == ("-5", "0", "5")
    assert level_label_source.labels == ("-5", "0", "5")
    assert level_label_source.visible_label_strings == ("-5", "0", "5")

    lb_level_label_source = build_hlu_labelbar(
        resources={
            "colors": ("q0", "q1", "q2"),
            "lbLevels": ("low", "mid"),
            "lbLabelAlignment": "InteriorEdges",
        },
    )
    assert lb_level_label_source.label_strings == ("low", "mid")
    assert lb_level_label_source.visible_label_strings == ("low", "mid")

    print("✅ HluLabelBar object semantics smoke passed")
    print("✅ build_hlu_labelbar now uses audited NCL/GSN LabelBar semantics")


if __name__ == "__main__":
    main()
