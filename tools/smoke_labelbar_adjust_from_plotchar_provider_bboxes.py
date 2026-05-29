from __future__ import annotations

from dataclasses import fields, is_dataclass

from climara.graphics._labelbar_adjust import has_labelbar_adjust_geometry_engine
from climara.graphics._labelbar_adjust_pipeline import (
    build_labelbar_adjust_pipeline_from_supplied_plotchar_metrics,
)
from climara.graphics._labelbar_adjust_plotchar_provider import (
    build_labelbar_adjust_pipeline_from_ncl_plotchar_backend_bboxes,
    build_labelbar_adjust_pipeline_from_plotchar_provider_bboxes,
    compute_labelbar_adjusted_geometry_from_plotchar_provider_bboxes,
)
from climara.graphics._labelbar_bbox_plotchar_provider import (
    compute_labelbar_text_bbox_from_plotchar_provider,
)
from climara.graphics._labelbar_object import HluLabelBar
from climara.graphics._labelbar_text_bbox import build_labelbar_text_bbox_requests
from climara.graphics._multitext_bbox_plotchar_provider import (
    compute_multitext_bbox_from_plotchar_provider,
)
from climara.graphics._plotchar_metrics import (
    PlotcharExtentMetrics,
    has_plotchar_metrics_engine,
)
from climara.graphics._plotchar_metrics_provider import PlotcharMetricsProviderError
from climara.graphics._text_bbox import has_text_bbox_engine
from climara.graphics._text_bbox_plotchar_provider import (
    compute_text_item_bbox_from_plotchar_provider,
)


def almost_equal(value, expected, tol=1e-12):
    assert abs(value - expected) <= tol, (value, expected)


def assert_bbox_equal(actual, expected, tol=1e-12):
    almost_equal(actual.l, expected.l, tol)
    almost_equal(actual.r, expected.r, tol)
    almost_equal(actual.b, expected.b, tol)
    almost_equal(actual.t, expected.t, tol)
    assert actual.coordinate_space == expected.coordinate_space


def assert_ncl_geometry_value_equal(actual, expected, tol=1e-12, path="geometry"):
    if isinstance(actual, float) or isinstance(expected, float):
        almost_equal(float(actual), float(expected), tol)
        return

    if is_dataclass(actual) and is_dataclass(expected):
        assert type(actual) is type(expected), (path, type(actual), type(expected))
        for field in fields(actual):
            assert_ncl_geometry_value_equal(
                getattr(actual, field.name),
                getattr(expected, field.name),
                tol,
                f"{path}.{field.name}",
            )
        return

    if isinstance(actual, tuple) or isinstance(expected, tuple):
        assert isinstance(actual, tuple), (path, type(actual))
        assert isinstance(expected, tuple), (path, type(expected))
        assert len(actual) == len(expected), (path, len(actual), len(expected))
        for index, (got, want) in enumerate(zip(actual, expected)):
            assert_ncl_geometry_value_equal(got, want, tol, f"{path}[{index}]")
        return

    assert actual == expected, (path, actual, expected)


def assert_geometry_equal(actual, expected, tol=1e-12):
    assert_ncl_geometry_value_equal(actual, expected, tol)

def main():
    labelbar = HluLabelBar(
        rect=(0.18, 0.22, 0.64, 0.16),
        colors=("#2166ac", "#67a9cf", "#fddbc7", "#b2182b"),
        labels=("Cold", "Cool", "Warm", "Hot", "Very hot"),
        resources={
            "lbTitleString": "Provider-adjusted LabelBar",
            "lbTitleOn": True,
            "lbTitlePosition": "Top",
            "lbTitleDirection": "Across",
            "lbTitleFuncCode": "~",
            "lbTitleJust": "CenterCenter",
            "lbTitleAngleF": 0.0,
            "lbTitleFontHeightF": 0.035,
            "lbLabelDirection": "Across",
            "lbLabelFuncCode": "~",
            "lbLabelJust": "CenterCenter",
            "lbLabelFontHeightF": 0.022,
            "lbLabelFontAspectF": 1.3125,
            "lbAutoManage": True,
            "lbJustification": "CenterCenter",
        },
    )

    requests = build_labelbar_text_bbox_requests(labelbar)
    assert requests.title is not None
    assert len(requests.labels.items) > 0

    title_metrics = PlotcharExtentMetrics(dl=0.18, dr=0.22, db=0.035, dt=0.07)
    label_metrics = tuple(
        PlotcharExtentMetrics(
            dl=0.025 + 0.002 * index,
            dr=0.03 + 0.002 * index,
            db=0.006,
            dt=0.018,
        )
        for index, _ in enumerate(requests.labels.items)
    )

    by_real_string = {requests.title.semantics.real_string: title_metrics}
    by_real_string.update(
        {
            item.semantics.real_string: metrics
            for item, metrics in zip(requests.labels.items, label_metrics)
        }
    )
    seen = []

    def provider(plotchar_request):
        seen.append(plotchar_request.semantics.real_string)
        return by_real_string[plotchar_request.semantics.real_string]

    text_bboxes = compute_labelbar_text_bbox_from_plotchar_provider(labelbar, provider)
    expected_title = compute_text_item_bbox_from_plotchar_provider(
        requests.title,
        provider,
    )
    expected_labels = compute_multitext_bbox_from_plotchar_provider(
        requests.labels,
        provider,
    )

    assert text_bboxes.title is not None
    assert text_bboxes.labels is not None
    assert_bbox_equal(text_bboxes.title.bbox, expected_title.bbox)
    assert_bbox_equal(text_bboxes.labels.bbox, expected_labels.bbox)
    assert len(text_bboxes.labels.child_text_bboxes) == len(requests.labels.items)

    pipeline = build_labelbar_adjust_pipeline_from_plotchar_provider_bboxes(
        labelbar,
        provider,
    )
    supplied = build_labelbar_adjust_pipeline_from_supplied_plotchar_metrics(
        labelbar,
        title_metrics=title_metrics,
        label_metrics=label_metrics,
    )

    assert pipeline.source_object is labelbar
    assert pipeline.provider_adjust_request.text_bboxes.title is not None
    assert pipeline.provider_adjust_request.text_bboxes.labels is not None
    assert_bbox_equal(
        pipeline.provider_adjust_request.adjust_request.title_bbox,
        supplied.supplied_metrics_request.adjust_request.title_bbox,
    )
    assert_bbox_equal(
        pipeline.provider_adjust_request.adjust_request.label_bbox,
        supplied.supplied_metrics_request.adjust_request.label_bbox,
    )
    assert_geometry_equal(pipeline.geometry, supplied.geometry)

    geometry = compute_labelbar_adjusted_geometry_from_plotchar_provider_bboxes(
        labelbar,
        provider,
    )
    assert_geometry_equal(geometry, pipeline.geometry)

    class Backend:
        def __init__(self):
            self.calls = []

        def metrics_for_call(self, call):
            self.calls.append(call)
            if call.chrs == requests.title.semantics.real_string:
                return title_metrics
            return by_real_string[call.chrs]

    backend = Backend()
    backend_pipeline = build_labelbar_adjust_pipeline_from_ncl_plotchar_backend_bboxes(
        labelbar,
        backend,
    )
    assert len(backend.calls) == 1 + len(requests.labels.items)
    for call in backend.calls:
        almost_equal(call.xpos, 0.5)
        almost_equal(call.ypos, 0.5)
        almost_equal(call.angd, 360.0)
        almost_equal(call.cntr, -1.0)
        assert call.state.text_extent_flag == 1
    assert_geometry_equal(backend_pipeline.geometry, supplied.geometry)

    try:
        build_labelbar_adjust_pipeline_from_ncl_plotchar_backend_bboxes(
            labelbar,
            backend=None,
        )
    except PlotcharMetricsProviderError as exc:
        message = str(exc)
        assert "No live NCL Plotchar backend" in message
        assert "fixed-width" in message
    else:
        raise AssertionError("LabelBar provider path must not invent metrics without backend")

    assert isinstance(has_plotchar_metrics_engine(), bool)
    assert isinstance(has_text_bbox_engine(), bool)
    assert has_labelbar_adjust_geometry_engine() is False

    assert requests.title.semantics.real_string in seen
    for item in requests.labels.items:
        assert item.semantics.real_string in seen

    print("✅ LabelBar AdjustGeometry from Plotchar provider bboxes smoke passed")


if __name__ == "__main__":
    main()
