from __future__ import annotations

import argparse

from climara.graphics._ncl_plotchar_real_library import (
    build_validated_ncl_plotchar_ctypes_backend,
    configured_ncl_plotchar_library_status_report,
    finite_nonnegative_metrics,
    validate_configured_ncl_plotchar_library,
)
from climara.graphics._ncl_plotchar_textitem import build_ncl_plotchar_metrics_provider
from climara.graphics._text_bbox import build_text_item_bbox_request
from climara.graphics._text_bbox_plotchar_bridge import (
    build_plotchar_metrics_request_from_text_bbox_request,
)
from climara.graphics._text_bbox_plotchar_provider import (
    compute_text_item_bbox_from_plotchar_provider,
)
from climara.graphics._text_semantics import build_text_item_semantics


def run_real_backend_smoke() -> None:
    backend = build_validated_ncl_plotchar_ctypes_backend()
    provider = build_ncl_plotchar_metrics_provider(backend=backend)

    semantics = build_text_item_semantics(
        "ABC",
        func_code="~",
        font=21,
        font_height=0.035,
        font_aspect=1.3125,
        font_quality="High",
    )
    request = build_text_item_bbox_request(semantics, x=0.4, y=0.6)
    plotchar_request = build_plotchar_metrics_request_from_text_bbox_request(request)
    metrics = provider.metrics_for_request(plotchar_request)

    if not finite_nonnegative_metrics(metrics):
        raise AssertionError(f"real Plotchar metrics are not finite/nonnegative: {metrics!r}")
    if float(metrics.dl) + float(metrics.dr) <= 0.0:
        raise AssertionError(f"real Plotchar width extent is not positive: {metrics!r}")
    if float(metrics.db) + float(metrics.dt) <= 0.0:
        raise AssertionError(f"real Plotchar height extent is not positive: {metrics!r}")

    bbox = compute_text_item_bbox_from_plotchar_provider(request, provider)
    if float(bbox.width) <= 0.0 or float(bbox.height) <= 0.0:
        raise AssertionError(f"real TextItem bbox is not positive: {bbox!r}")

    print("REAL BACKEND OK: NCAR/NCL Plotchar shared library produced DL/DR/DB/DT")
    print(f"metrics: {metrics}")
    print(f"bbox: {bbox}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require", action="store_true")
    parser.add_argument("--run-real-smoke", action="store_true")
    args = parser.parse_args()

    print(configured_ncl_plotchar_library_status_report())
    validation = validate_configured_ncl_plotchar_library()

    if args.require and not validation.ok:
        raise SystemExit(2)

    if args.run_real_smoke:
        if not validation.ok:
            raise SystemExit(
                "Cannot run real Plotchar smoke because the configured shared library "
                "did not validate."
            )
        run_real_backend_smoke()


if __name__ == "__main__":
    main()
