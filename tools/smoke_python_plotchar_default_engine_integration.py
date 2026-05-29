from __future__ import annotations

from climara.graphics._plotchar_metrics import (
    compute_plotchar_extent_metrics,
    has_plotchar_metrics_engine,
)
from climara.graphics._plotchar_state import PlotcharUnsupportedError
from climara.graphics._text_bbox import (
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
    assert has_plotchar_metrics_engine() is True
    assert has_text_bbox_engine() is True

    across = build_text_item_semantics(
        "NCL",
        direction="Across",
        func_code="~",
        just="CenterCenter",
        angle=23.0,
        font=21,
        font_height=0.03,
        font_aspect=1.3125,
        font_quality="High",
    )
    across_request = build_text_item_bbox_request(across, x=0.45, y=0.55)
    plotchar_request = build_plotchar_metrics_request_from_text_bbox_request(across_request)
    metrics = compute_plotchar_extent_metrics(plotchar_request)

    assert metrics.width > 0.0
    assert metrics.height > 0.0

    across_bbox = compute_text_item_bbox(across_request)
    assert across_bbox.width > metrics.width
    assert across_bbox.height > metrics.height
    assert across_bbox.l < across_bbox.r
    assert across_bbox.b < across_bbox.t

    across2 = build_text_item_semantics(
        "ABC",
        direction="Across",
        func_code="~",
        just="CenterCenter",
        angle=0.0,
        font=21,
        font_height=0.025,
        font_quality="High",
    )
    across2_request = build_text_item_bbox_request(across2, x=0.70, y=0.55)
    across2_bbox = compute_text_item_bbox(across2_request)

    multi = build_multitext_bbox_request((across_request, across2_request))
    multi_bbox = compute_multitext_bbox(multi)
    assert multi_bbox.l <= min(across_bbox.l, across2_bbox.l)
    assert multi_bbox.r >= max(across_bbox.r, across2_bbox.r)

    down = build_text_item_semantics(
        "NCL",
        direction="Down",
        func_code="~",
        just="CenterCenter",
        angle=0.0,
        font=21,
        font_height=0.03,
        font_quality="High",
    )
    down_request = build_text_item_bbox_request(down, x=0.5, y=0.5)
    down_bbox = compute_text_item_bbox(down_request)

    assert down_bbox.width > 0.0
    assert down_bbox.height > 0.0
    assert down_bbox.l < down_bbox.r
    assert down_bbox.b < down_bbox.t

    # Unsupported inline function-code commands must still stay guarded.
    # R remains unsupported after the D/A stage.
    inline = build_text_item_semantics(
        "A~R~B",
        direction="Across",
        func_code="~",
        font=21,
        font_height=0.03,
        font_quality="High",
    )
    inline_request = build_text_item_bbox_request(inline, x=0.5, y=0.5)
    try:
        compute_text_item_bbox(inline_request)
    except PlotcharUnsupportedError as exc:
        assert "got command 'R'" in str(exc)
    else:
        raise AssertionError("Unsupported inline Plotchar command R must remain guarded")

    print("✅ Python Plotchar default TextItem/MultiText engine integration smoke passed")


if __name__ == "__main__":
    main()
