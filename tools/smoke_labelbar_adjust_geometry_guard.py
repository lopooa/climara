from climara.graphics._labelbar_adjust import (
    adjust_labelbar_geometry_for_text,
    build_labelbar_adjust_geometry_request,
    has_labelbar_adjust_geometry_engine,
)
from climara.graphics._labelbar_object import HluLabelBar
from climara.graphics._text_bbox import build_text_bbox

from _smoke_labelbar_adjust_helpers import assert_adjust_result


def main():
    labelbar = HluLabelBar(
        colors=["#2166ac", "#67a9cf", "#fddbc7", "#b2182b"],
        labels=["A", "B", "C", "D"],
        resources={"lbTitleString": "AdjustGeometry guard", "lbTitlePosition": "Top"},
    )

    geometry = labelbar.compute_geometry()
    title_bbox = build_text_bbox(l=0.2, r=0.8, b=0.85, t=0.9)
    label_bbox = build_text_bbox(l=0.1, r=0.9, b=0.05, t=0.15)

    request = build_labelbar_adjust_geometry_request(
        geometry,
        title_bbox=title_bbox,
        label_bbox=label_bbox,
    )

    assert has_labelbar_adjust_geometry_engine() is False
    result = adjust_labelbar_geometry_for_text(request)
    assert_adjust_result(result)

    print("✅ LabelBar AdjustGeometry supplied-bbox execution guard smoke passed")


if __name__ == "__main__":
    main()
