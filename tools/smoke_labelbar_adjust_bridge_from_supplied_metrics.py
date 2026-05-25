from climara.graphics._labelbar_adjust import (
    adjust_labelbar_geometry_for_text,
    has_labelbar_adjust_geometry_engine,
)
from climara.graphics._labelbar_adjust_bridge import (
    build_labelbar_adjust_request_from_supplied_plotchar_metrics,
)
from climara.graphics._labelbar_object import HluLabelBar
from climara.graphics._labelbar_text_bbox import build_labelbar_text_bbox_requests
from climara.graphics._plotchar_metrics import PlotcharExtentMetrics
from climara.graphics._text_bbox import TEXT_BBOX_COORD_NDC


def almost_equal(value, expected, tol=1e-12):
    assert abs(value - expected) <= tol, (value, expected)


def main():
    labelbar = HluLabelBar(
        name="adjust_bridge_labelbar",
        colors=["#2166ac", "#67a9cf", "#fddbc7", "#b2182b"],
        labels=["A", "B", "C", "D"],
        resources={
            "lbTitleString": "Adjust bridge",
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
    assert requests.labels.items

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

    bundle = build_labelbar_adjust_request_from_supplied_plotchar_metrics(
        labelbar,
        title_metrics=title_metrics,
        label_metrics=label_metrics,
    )

    assert bundle.text_bboxes.title is not None
    assert bundle.text_bboxes.labels is not None

    assert bundle.adjust_request.geometry == labelbar.compute_geometry()
    assert bundle.adjust_request.title_bbox is bundle.text_bboxes.title.bbox
    assert bundle.adjust_request.label_bbox is bundle.text_bboxes.labels.bbox

    assert bundle.adjust_request.title_bbox.coordinate_space == TEXT_BBOX_COORD_NDC
    assert bundle.adjust_request.label_bbox.coordinate_space == TEXT_BBOX_COORD_NDC

    almost_equal(bundle.adjust_request.title_bbox.width, 0.30)
    almost_equal(bundle.adjust_request.title_bbox.height, 0.10)

    assert has_labelbar_adjust_geometry_engine() is False

    adjust_result = adjust_labelbar_geometry_for_text(bundle.adjust_request)
    assert adjust_result.final_view_bbox.width >= 0.0
    assert adjust_result.final_view_bbox.height >= 0.0
    no_title = HluLabelBar(
        colors=["#2166ac", "#67a9cf"],
        labels=["A", "B"],
        resources={
            "lbTitleOn": False,
        },
    )

    no_title_requests = build_labelbar_text_bbox_requests(no_title)

    no_title_label_metrics = tuple(
        PlotcharExtentMetrics(
            dl=0.01,
            dr=0.01,
            db=0.01,
            dt=0.01,
        )
        for _ in no_title_requests.labels.items
    )

    no_title_bundle = build_labelbar_adjust_request_from_supplied_plotchar_metrics(
        no_title,
        label_metrics=no_title_label_metrics,
    )

    assert no_title_bundle.text_bboxes.title is None
    assert no_title_bundle.adjust_request.title_bbox is None
    assert no_title_bundle.adjust_request.label_bbox is not None

    print("✅ LabelBar supplied-metrics AdjustGeometry request bridge smoke passed")


if __name__ == "__main__":
    main()
