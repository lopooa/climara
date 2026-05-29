from __future__ import annotations

import os

from climara.graphics._ncl_plotchar_live_engine import (
    configured_ncl_plotchar_backend_is_requested,
    has_configured_ncl_plotchar_live_engine,
    ncl_plotchar_live_engine_status,
)
from climara.graphics._ncl_plotchar_real_library import (
    NCL_PLOTCHAR_LIBRARY_DIRS_ENV,
    NCL_PLOTCHAR_LIBRARY_ENV,
)
from climara.graphics._plotchar_metrics import (
    PlotcharMetricsNotImplementedError,
    compute_plotchar_extent_metrics,
    has_plotchar_metrics_engine,
)
from climara.graphics._text_bbox import (
    TextBBoxNotImplementedError,
    build_multitext_bbox_request,
    build_text_item_bbox_request,
    compute_multitext_bbox,
    compute_text_item_bbox,
    has_text_bbox_engine,
)
from climara.graphics._text_bbox_plotchar_bridge import (
    build_plotchar_metrics_request_from_text_bbox_request,
)
from climara.graphics._text_semantics import build_text_item_semantics


def main():
    old_lib = os.environ.pop(NCL_PLOTCHAR_LIBRARY_ENV, None)
    old_dirs = os.environ.pop(NCL_PLOTCHAR_LIBRARY_DIRS_ENV, None)

    try:
        assert configured_ncl_plotchar_backend_is_requested() is False
        assert has_configured_ncl_plotchar_live_engine() is False
        assert isinstance(has_plotchar_metrics_engine(), bool)
        assert isinstance(has_text_bbox_engine(), bool)

        status = ncl_plotchar_live_engine_status()
        assert status.requested is False
        assert status.available is False
        assert "must not use fixed-width" in status.report

        semantics = build_text_item_semantics("ABC", func_code="~", font_height=0.035)
        text_request = build_text_item_bbox_request(semantics, x=0.4, y=0.6)
        plotchar_request = build_plotchar_metrics_request_from_text_bbox_request(text_request)

        try:
            compute_plotchar_extent_metrics(plotchar_request)
        except PlotcharMetricsNotImplementedError as exc:
            message = str(exc)
            assert "not implemented/guarded" in message
            assert "no real NCAR/NCL Plotchar shared library" in message
            assert "fixed-width" in message
            assert "SVG" in message
        else:
            raise AssertionError("Default Plotchar metrics must stay guarded without a real library")

        try:
            compute_text_item_bbox(text_request)
        except TextBBoxNotImplementedError as exc:
            message = str(exc)
            assert "no real NCAR/NCL Plotchar shared library" in message
            assert "DoPcCalc" in message
            assert "post-metric justification/rotation" in message
        else:
            raise AssertionError("Default TextItem bbox must stay guarded without a real library")

        multitext_request = build_multitext_bbox_request((text_request,))
        try:
            compute_multitext_bbox(multitext_request)
        except TextBBoxNotImplementedError as exc:
            message = str(exc)
            assert "no real NCAR/NCL Plotchar shared library" in message
            assert "MultiText.c child bbox aggregation" in message
        else:
            raise AssertionError("Default MultiText bbox must stay guarded without a real library")

        print("✅ Default live TextItem/MultiText engine gate smoke passed")
    finally:
        if old_lib is not None:
            os.environ[NCL_PLOTCHAR_LIBRARY_ENV] = old_lib
        if old_dirs is not None:
            os.environ[NCL_PLOTCHAR_LIBRARY_DIRS_ENV] = old_dirs


if __name__ == "__main__":
    main()
