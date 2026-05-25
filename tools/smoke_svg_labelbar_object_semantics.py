from pathlib import Path

from climara.graphics._labelbar_object import build_hlu_labelbar
from climara.graphics import _render_svg


def almost_equal_tuple(actual, expected):
    assert len(actual) == len(expected), (actual, expected)
    for a, e in zip(actual, expected):
        assert abs(a - e) < 1.0e-12, (actual, expected)


def main():
    stride_obj = build_hlu_labelbar(
        colors=("c0", "c1", "c2", "c3", "c4"),
        labels=("L0", "L1", "L2", "L3", "L4"),
        resources={
            "lbLabelStride": 2,
            "lbLabelAlignment": "BoxCenters",
        },
    )

    assert _render_svg._labelbar_labels(stride_obj) == ["L0", "L2", "L4"]
    almost_equal_tuple(
        _render_svg._labelbar_label_positions(stride_obj, len(stride_obj.visible_label_strings)),
        (0.1, 0.5, 0.9),
    )

    external_edges_obj = build_hlu_labelbar(
        colors=("c0", "c1", "c2", "c3"),
        labels=("A", "B", "C", "D", "E"),
        resources={
            "EndStyle": "IncludeMinMaxLabels",
        },
    )

    assert _render_svg._labelbar_labels(external_edges_obj) == ["A", "B", "C", "D", "E"]
    almost_equal_tuple(
        _render_svg._labelbar_label_positions(
            external_edges_obj,
            len(external_edges_obj.visible_label_strings),
        ),
        (0.1, 0.3, 0.5, 0.7, 0.9),
    )

    fallback_positions = _render_svg._labelbar_label_positions(3)
    almost_equal_tuple(fallback_positions, (0.0, 0.5, 1.0))

    source = Path("src/climara/graphics/_render_svg.py").read_text(encoding="utf-8")
    assert "visible_label_strings" in source
    assert "label_axis_positions" in source

    print("✅ SVG LabelBar renderer helper smoke passed")
    print("✅ helper functions read HluLabelBar object-level label semantics")


if __name__ == "__main__":
    main()
