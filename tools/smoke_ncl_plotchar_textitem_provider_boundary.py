from __future__ import annotations

from climara.graphics._ncl_plotchar_textitem import (
    NclPlotcharMeasurementContractError,
    build_ncl_plotchar_metrics_provider,
    build_ncl_plotchar_textitem_measurement_call,
    build_ncl_plotchar_textitem_state,
    ncl_textitem_principle_dimensions,
)
from climara.graphics._plotchar_metrics import (
    PlotcharExtentMetrics,
    build_plotchar_metrics_request,
    has_plotchar_metrics_engine,
)
from climara.graphics._plotchar_metrics_provider import PlotcharMetricsProviderError
from climara.graphics._text_bbox import build_text_item_bbox_request
from climara.graphics._text_bbox_plotchar_bridge import (
    build_plotchar_metrics_request_from_text_bbox_request,
)
from climara.graphics._text_semantics import (
    TEXT_QUALITY_LOW,
    TEXT_QUALITY_WORKSTATION,
    build_text_item_semantics,
    plotchar_real_size_from_text_semantics,
)


def almost_equal(value, expected, tol=1e-12):
    assert abs(value - expected) <= tol, (value, expected)


def main():
    semantics = build_text_item_semantics(
        "ABC",
        func_code="~",
        font=21,
        font_height=0.04,
        font_aspect=2.0,
        font_quality="High",
        constant_spacing=0.125,
    )
    bbox_request = build_text_item_bbox_request(semantics, x=0.2, y=0.8)
    plotchar_request = build_plotchar_metrics_request_from_text_bbox_request(bbox_request)

    state = build_ncl_plotchar_textitem_state(semantics)
    almost_equal(state.principle_height, 21.0)
    almost_equal(state.principle_width, 10.5)
    almost_equal(state.real_size, 0.04 * 1.125 / 2.0)
    almost_equal(state.constant_spacing, 0.125)
    assert state.text_extent_flag == 1
    assert state.func_code == "~"
    assert state.quality_index == 0
    assert state.font == 21
    assert state.effective_font == 21
    assert state.font_aspect == 2.0
    assert state.font_aspect_was_sanitized is False

    call = build_ncl_plotchar_textitem_measurement_call(plotchar_request)
    almost_equal(call.xpos, 0.5)
    almost_equal(call.ypos, 0.5)
    almost_equal(call.size, plotchar_real_size_from_text_semantics(semantics))
    almost_equal(call.angd, 360.0)
    almost_equal(call.cntr, -1.0)
    assert call.chrs == "~A~ABC"
    assert call.state == state

    h, w, sanitized = ncl_textitem_principle_dimensions(0.5)
    almost_equal(h, 10.5)
    almost_equal(w, 21.0)
    assert sanitized is False

    h, w, sanitized = ncl_textitem_principle_dimensions(-1.0)
    almost_equal(h, 21.0)
    almost_equal(w, 16.0)
    assert sanitized is True

    low = build_text_item_semantics("ABC", font=99, font_quality=TEXT_QUALITY_LOW)
    low_state = build_ncl_plotchar_textitem_state(low)
    assert low_state.quality_index == 2
    assert low_state.font == 99
    assert low_state.effective_font == 1

    workstation = build_text_item_semantics(
        "ABC",
        font_quality=TEXT_QUALITY_WORKSTATION,
    )
    try:
        build_ncl_plotchar_textitem_state(workstation)
    except NclPlotcharMeasurementContractError as exc:
        assert "Workstation" in str(exc)
    else:
        raise AssertionError("Workstation-quality Plotchar state must remain guarded")

    bad_request = build_plotchar_metrics_request(
        semantics,
        x=0.2,
        y=0.8,
        size=0.04,
        angle=45.0,
        cntr=0.0,
    )
    try:
        build_ncl_plotchar_textitem_measurement_call(bad_request)
    except NclPlotcharMeasurementContractError as exc:
        message = str(exc)
        assert "FigureAndSetTextBBInfo" in message
        assert "angle=45.0" in message
    else:
        raise AssertionError("Non-TextItem measurement calls must stay guarded")

    provider = build_ncl_plotchar_metrics_provider()
    try:
        provider.metrics_for_request(plotchar_request)
    except PlotcharMetricsProviderError as exc:
        assert "No live NCL Plotchar backend" in str(exc)
        assert "fixed-width" in str(exc)
    else:
        raise AssertionError("Provider without backend must not return heuristic metrics")

    captured = {}

    def backend(call):
        captured["call"] = call
        return {"DL": 0.01, "DR": 0.03, "DB": 0.004, "DT": 0.02}

    provider = build_ncl_plotchar_metrics_provider(backend=backend)
    metrics = provider.metrics_for_request(plotchar_request)
    assert captured["call"] == call
    assert isinstance(metrics, PlotcharExtentMetrics)
    almost_equal(metrics.dl, 0.01)
    almost_equal(metrics.dr, 0.03)
    almost_equal(metrics.db, 0.004)
    almost_equal(metrics.dt, 0.02)

    assert isinstance(has_plotchar_metrics_engine(), bool)

    print("✅ NCL Plotchar TextItem provider boundary smoke passed")


if __name__ == "__main__":
    main()
