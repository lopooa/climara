from math import isfinite

from climara.graphics._labelbar_adjust import adjust_labelbar_geometry_for_text
from climara.graphics._labelbar_adjust_writeback_semantics import (
    compute_labelbar_adjust_writeback_semantics,
)

from _smoke_labelbar_adjust_helpers import (
    assert_adjust_result,
    make_labelbar,
    make_supplied_metrics_bundle,
)


def almost_equal(value, expected, tol=1e-12):
    assert abs(value - expected) <= tol, (value, expected)


def main():
    labelbar = make_labelbar("adjust_writeback_semantics")
    geometry = labelbar.compute_geometry()
    bundle = make_supplied_metrics_bundle(labelbar)
    semantics = compute_labelbar_adjust_writeback_semantics(
        bundle.adjust_request,
        justification="CenterCenter",
    )
    perim = semantics.perimeter_semantics

    assert len(semantics.final_box_locs) == len(geometry.box_locs)
    assert len(semantics.final_label_locs) == len(geometry.label_locs)

    for original, final in zip(geometry.box_locs, semantics.final_box_locs):
        almost_equal(final, original - perim.major_offset)

    for original, final in zip(geometry.label_locs, semantics.final_label_locs):
        almost_equal(final, original - perim.major_offset)

    assert semantics.final_label_const_pos is not None
    assert semantics.final_title_x is not None
    assert semantics.final_title_y is not None

    for value in (
        *semantics.final_box_locs,
        *semantics.final_label_locs,
        semantics.final_label_const_pos,
        semantics.final_title_x,
        semantics.final_title_y,
    ):
        assert isfinite(value), value

    result = adjust_labelbar_geometry_for_text(bundle.adjust_request)
    assert_adjust_result(result)

    print("✅ LabelBar AdjustGeometry write-back semantics smoke passed")


if __name__ == "__main__":
    main()
