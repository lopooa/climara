from climara.graphics._labelbar_adjust import adjust_labelbar_geometry_for_text
from climara.graphics._labelbar_adjust_semantics import (
    compute_labelbar_adjust_box_semantics,
)

from _smoke_labelbar_adjust_helpers import (
    assert_adjust_result,
    assert_finite_bbox,
    contains,
    make_labelbar,
    make_supplied_metrics_bundle,
)


def main():
    bundle = make_supplied_metrics_bundle(make_labelbar("adjust_box_semantics"))
    semantics = compute_labelbar_adjust_box_semantics(bundle.adjust_request)

    assert_finite_bbox(semantics.labelbar_bbox)
    assert_finite_bbox(semantics.bar_and_labels_bbox)
    assert_finite_bbox(semantics.adjusted_bar_bbox)
    contains(semantics.labelbar_bbox, semantics.adjusted_bar_bbox)
    contains(semantics.labelbar_bbox, semantics.bar_and_labels_bbox)

    assert semantics.adjusted_label_bbox is not None
    assert semantics.adjusted_title_bbox is not None
    assert_finite_bbox(semantics.adjusted_label_bbox)
    assert_finite_bbox(semantics.adjusted_title_bbox)
    contains(semantics.labelbar_bbox, semantics.adjusted_label_bbox)
    contains(semantics.labelbar_bbox, semantics.adjusted_title_bbox)

    result = adjust_labelbar_geometry_for_text(bundle.adjust_request)
    assert_adjust_result(result)

    print("✅ LabelBar AdjustGeometry supplied-bbox box semantics smoke passed")


if __name__ == "__main__":
    main()
