from math import isfinite

from climara.graphics._labelbar_bbox_semantics import (
    compute_labelbar_text_bbox_from_plotchar_metrics,
)
from climara.graphics._labelbar_object import HluLabelBar
from climara.graphics._labelbar_text_bbox import build_labelbar_text_bbox_requests
from climara.graphics._plotchar_metrics import PlotcharExtentMetrics
from climara.graphics._text_bbox import (
    TEXT_BBOX_COORD_NDC,
    TextBBoxNotImplementedError,
    compute_multitext_bbox,
    compute_text_item_bbox,
)


def almost_equal(value, expected, tol=1e-12):
    assert abs(value - expected) <= tol, (value, expected)


def assert_bbox_is_finite(box):
    assert box.coordinate_space == TEXT_BBOX_COORD_NDC
    for value in (box.l, box.r, box.b, box.t, box.width, box.height):
        assert isfinite(value), value
    assert box.width >= 0.0
    assert box.height >= 0.0


def main():
    labelbar = HluLabelBar(
        name="labelbar_supplied_metrics",
        colors=["#2166ac", "#67a9cf", "#fddbc7", "#b2182b"],
        labels=["A", "B", "C", "D"],
        resources={
            "lbTitleString": "BBox title",
            "lbTitlePosition": "Top",
            "lbTitleDirection": "Across",
            "lbTitleJust": "CenterCenter",
            "lbTitleAngleF": 0,
            "lbTitleFuncCode": "@",
            "lbTitleFontHeightF": 0.04,
            "lbLabelDirection": "Across",
            "lbLabelJust": "CenterCenter",
            "lbLabelAngleF": 0,
            "lbLabelFuncCode": "%",
            "lbLabelFontHeightF": 0.03,
        },
    )

    requests = build_labelbar_text_bbox_requests(labelbar)

    assert requests.title is not None
    assert len(requests.labels.items) > 0

    title_metrics = PlotcharExtentMetrics(
        dl=0.12,
        dr=0.18,
        db=0.03,
        dt=0.07,
    )

    label_metrics = tuple(
        PlotcharExtentMetrics(
            dl=0.02,
            dr=0.02,
            db=0.01,
            dt=0.02,
        )
        for _ in requests.labels.items
    )

    result = compute_labelbar_text_bbox_from_plotchar_metrics(
        labelbar,
        title_metrics=title_metrics,
        label_metrics=label_metrics,
    )

    assert result.title is not None
    assert result.labels is not None

    assert_bbox_is_finite(result.title.bbox)
    assert_bbox_is_finite(result.labels.bbox)

    almost_equal(result.title.bbox.width, 0.30)
    almost_equal(result.title.bbox.height, 0.10)

    assert len(result.labels.child_text_bboxes) == len(requests.labels.items)

    for child in result.labels.child_text_bboxes:
        assert_bbox_is_finite(child.bbox)
        almost_equal(child.bbox.width, 0.04)
        almost_equal(child.bbox.height, 0.03)

    try:
        compute_text_item_bbox(requests.title)
    except TextBBoxNotImplementedError:
        pass
    else:
        raise AssertionError("live TextItem bbox engine must remain guarded")

    try:
        compute_multitext_bbox(requests.labels)
    except TextBBoxNotImplementedError:
        pass
    else:
        raise AssertionError("live MultiText bbox engine must remain guarded")

    no_title = HluLabelBar(
        colors=["#2166ac", "#67a9cf"],
        labels=["A", "B"],
        resources={
            "lbTitleOn": False,
        },
    )

    no_title_requests = build_labelbar_text_bbox_requests(no_title)
    no_title_label_metrics = tuple(
        PlotcharExtentMetrics(dl=0.01, dr=0.01, db=0.01, dt=0.01)
        for _ in no_title_requests.labels.items
    )

    no_title_result = compute_labelbar_text_bbox_from_plotchar_metrics(
        no_title,
        label_metrics=no_title_label_metrics,
    )

    assert no_title_result.title is None
    assert no_title_result.labels is not None

    try:
        compute_labelbar_text_bbox_from_plotchar_metrics(
            no_title,
            title_metrics=title_metrics,
            label_metrics=no_title_label_metrics,
        )
    except ValueError as exc:
        assert "has no title request" in str(exc)
    else:
        raise AssertionError("supplying title metrics for a no-title LabelBar should fail")

    try:
        compute_labelbar_text_bbox_from_plotchar_metrics(
            labelbar,
            title_metrics=title_metrics,
            label_metrics=label_metrics[:1],
        )
    except ValueError as exc:
        assert "one metrics object for each TextItem request" in str(exc)
    else:
        raise AssertionError("mismatched label metrics should fail")

    print("✅ LabelBar text bbox semantics from supplied Plotchar metrics smoke passed")


if __name__ == "__main__":
    main()
