from __future__ import annotations

from climara.graphics._ncl_plotchar_textitem import build_ncl_plotchar_metrics_provider
from climara.graphics._plotchar_metrics import PlotcharExtentMetrics
from climara.graphics._plotchar_metrics_provider import PlotcharMetricsProviderError
from climara.graphics._text_bbox import (
    build_text_item_bbox_request,
    compute_text_item_bbox,
    has_text_bbox_engine,
)
from climara.graphics._text_bbox_plotchar_provider import (
    compute_text_item_bbox_from_ncl_plotchar_backend,
    compute_text_item_bbox_from_plotchar_provider,
)
from climara.graphics._text_bbox_semantics import compute_text_bbox_from_plotchar_metrics
from climara.graphics._text_semantics import build_text_item_semantics


def almost_equal(value, expected, tol=1e-12):
    assert abs(value - expected) <= tol, (value, expected)


def assert_bbox_equal(actual, expected, tol=1e-12):
    almost_equal(actual.l, expected.l, tol)
    almost_equal(actual.r, expected.r, tol)
    almost_equal(actual.b, expected.b, tol)
    almost_equal(actual.t, expected.t, tol)
    assert actual.coordinate_space == expected.coordinate_space


class CapturingBackend:
    def __init__(self, metrics):
        self.metrics = metrics
        self.calls = []

    def metrics_for_call(self, call):
        self.calls.append(call)
        return self.metrics


def main():
    metrics = PlotcharExtentMetrics(dl=0.08, dr=0.12, db=0.025, dt=0.055)
    semantics = build_text_item_semantics(
        "NCL",
        just="CenterCenter",
        angle=27.0,
        font_height=0.04,
        font_aspect=1.5,
        func_code="~",
        font=21,
        constant_spacing=0.0,
    )
    request = build_text_item_bbox_request(semantics, x=0.33, y=0.66)

    backend = CapturingBackend(metrics)
    provider = build_ncl_plotchar_metrics_provider(backend=backend)

    explicit = compute_text_item_bbox_from_plotchar_provider(request, provider)
    expected = compute_text_bbox_from_plotchar_metrics(request, metrics)

    assert_bbox_equal(explicit.bbox, expected.bbox)
    almost_equal(explicit.real_x, expected.real_x)
    almost_equal(explicit.real_y, expected.real_y)
    assert explicit.corners == expected.corners
    assert explicit.sanitized_metrics == expected.sanitized_metrics

    assert len(backend.calls) == 1
    call = backend.calls[0]
    almost_equal(call.xpos, 0.5)
    almost_equal(call.ypos, 0.5)
    almost_equal(call.angd, 360.0)
    almost_equal(call.cntr, -1.0)
    assert call.chrs == semantics.real_string
    assert call.state.text_extent_flag == 1
    assert call.state.func_code == "~"
    assert call.state.effective_font == 21

    raw_width = metrics.dl + metrics.dr
    raw_height = metrics.db + metrics.dt
    assert explicit.bbox.width > raw_width
    assert explicit.bbox.height > raw_height

    backend2 = CapturingBackend(metrics)
    via_backend = compute_text_item_bbox_from_ncl_plotchar_backend(request, backend2)
    assert_bbox_equal(via_backend.bbox, expected.bbox)
    assert len(backend2.calls) == 1

    guarded_provider = build_ncl_plotchar_metrics_provider()
    try:
        compute_text_item_bbox_from_plotchar_provider(request, guarded_provider)
    except PlotcharMetricsProviderError as exc:
        message = str(exc)
        assert "No live NCL Plotchar backend" in message
        assert "fixed-width" in message
    else:
        raise AssertionError("Missing explicit provider backend must stay guarded")

    if has_text_bbox_engine():
        default_bbox = compute_text_item_bbox(request)
        assert default_bbox.width > 0.0
        assert default_bbox.height > 0.0
        assert default_bbox.coordinate_space == expected.bbox.coordinate_space
    else:
        try:
            compute_text_item_bbox(request)
        except NotImplementedError as exc:
            assert "not implemented" in str(exc).lower() or "blocked" in str(exc).lower()
        else:
            raise AssertionError(
                "Default TextItem bbox engine must stay guarded when Python Plotchar mainline is unavailable"
            )

    print("✅ TextItem bbox from Plotchar provider smoke passed")


if __name__ == "__main__":
    main()
