from __future__ import annotations

from climara.graphics._multitext_bbox_plotchar_provider import (
    compute_multitext_bbox_from_ncl_plotchar_backend,
    compute_multitext_bbox_from_plotchar_provider,
)
from climara.graphics._multitext_semantics import build_multitext_semantics
from climara.graphics._plotchar_metrics import PlotcharExtentMetrics
from climara.graphics._plotchar_metrics_provider import PlotcharMetricsProviderError
from climara.graphics._text_bbox import (
    build_multitext_bbox_request_from_semantics,
    compute_multitext_bbox,
    has_text_bbox_engine,
)
from climara.graphics._text_bbox_plotchar_provider import (
    compute_text_item_bbox_from_plotchar_provider,
)


def almost_equal(value, expected, tol=1e-12):
    assert abs(value - expected) <= tol, (value, expected)


def main():
    semantics = build_multitext_semantics(
        ["A", "BB", "CCC"],
        func_code="~",
        just="CenterCenter",
        angle=0.0,
        font=21,
        font_height=0.03,
        font_aspect=1.5,
    )
    request = build_multitext_bbox_request_from_semantics(
        semantics,
        positions=((0.2, 0.2), (0.5, 0.35), (0.8, 0.5)),
    )

    by_real_string = {
        item.semantics.real_string: PlotcharExtentMetrics(
            dl=0.01 + index * 0.002,
            dr=0.02 + index * 0.003,
            db=0.004 + index * 0.001,
            dt=0.012 + index * 0.002,
        )
        for index, item in enumerate(request.items)
    }
    seen = []

    def provider(plotchar_request):
        seen.append(plotchar_request)
        return by_real_string[plotchar_request.semantics.real_string]

    result = compute_multitext_bbox_from_plotchar_provider(request, provider)
    assert len(result.child_text_bboxes) == len(request.items)
    assert [item.semantics.real_string for item in seen] == [
        item.semantics.real_string for item in request.items
    ]

    child_results = tuple(
        compute_text_item_bbox_from_plotchar_provider(item, provider)
        for item in request.items
    )
    almost_equal(result.bbox.l, min(child.bbox.l for child in child_results))
    almost_equal(result.bbox.r, max(child.bbox.r for child in child_results))
    almost_equal(result.bbox.b, min(child.bbox.b for child in child_results))
    almost_equal(result.bbox.t, max(child.bbox.t for child in child_results))

    class Backend:
        def __init__(self):
            self.calls = []

        def metrics_for_call(self, call):
            self.calls.append(call)
            return {"dl": 0.01, "dr": 0.02, "db": 0.004, "dt": 0.012}

    backend = Backend()
    backend_result = compute_multitext_bbox_from_ncl_plotchar_backend(request, backend)
    assert len(backend.calls) == len(request.items)
    assert len(backend_result.child_text_bboxes) == len(request.items)
    for call, item in zip(backend.calls, request.items):
        assert call.chrs == item.semantics.real_string
        almost_equal(call.xpos, 0.5)
        almost_equal(call.ypos, 0.5)
        almost_equal(call.angd, 360.0)
        almost_equal(call.cntr, -1.0)

    try:
        compute_multitext_bbox_from_ncl_plotchar_backend(request, backend=None)
    except PlotcharMetricsProviderError as exc:
        message = str(exc)
        assert "No live NCL Plotchar backend" in message
        assert "fixed-width" in message
    else:
        raise AssertionError("Missing NCL backend must stay guarded")

    if has_text_bbox_engine():
        default_bbox = compute_multitext_bbox(request)
        assert default_bbox.width > 0.0
        assert default_bbox.height > 0.0
        assert default_bbox.coordinate_space == result.bbox.coordinate_space
    else:
        try:
            compute_multitext_bbox(request)
        except NotImplementedError as exc:
            assert "not implemented" in str(exc).lower() or "blocked" in str(exc).lower()
        else:
            raise AssertionError(
                "Default MultiText bbox engine must stay guarded when Python Plotchar mainline is unavailable"
            )

    print("✅ MultiText bbox from Plotchar provider smoke passed")


if __name__ == "__main__":
    main()
