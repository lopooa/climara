from math import inf, nan

from climara.graphics._plotchar_metrics import (
    build_plotchar_extent_metrics,
    compute_plotchar_extent_metrics,
    has_plotchar_metrics_engine,
)
from climara.graphics._plotchar_state import PlotcharUnsupportedError
from climara.graphics._text_bbox import build_text_item_bbox_request
from climara.graphics._text_bbox_plotchar_bridge import (
    build_plotchar_metrics_request_from_text_bbox_request,
)
from climara.graphics._text_semantics import build_text_item_semantics


def almost_equal(value, expected, tol=1e-12):
    assert abs(value - expected) <= tol, (value, expected)


def main():
    extents = build_plotchar_extent_metrics(
        dl=0.1,
        dr=0.3,
        db=0.05,
        dt=0.15,
    )

    almost_equal(extents.dl, 0.1)
    almost_equal(extents.dr, 0.3)
    almost_equal(extents.db, 0.05)
    almost_equal(extents.dt, 0.15)
    almost_equal(extents.width, 0.4)
    almost_equal(extents.height, 0.2)

    signed_extents = build_plotchar_extent_metrics(
        dl=0.2,
        dr=-0.1,
        db=0.3,
        dt=-0.1,
    )

    almost_equal(signed_extents.width, 0.1)
    almost_equal(signed_extents.height, 0.2)

    for bad_value in (nan, inf, -inf):
        try:
            build_plotchar_extent_metrics(
                dl=bad_value,
                dr=0.1,
                db=0.1,
                dt=0.1,
            )
        except ValueError as exc:
            assert "must be finite" in str(exc)
        else:
            raise AssertionError("non-finite Plotchar metric should fail")

    assert isinstance(has_plotchar_metrics_engine(), bool)

    semantics = build_text_item_semantics(
        "Demo",
        direction="Across",
        func_code="~",
        just="CenterCenter",
        angle=-45,
        font=21,
        font_color="black",
        font_height=0.025,
        font_quality="High",
    )
    request = build_text_item_bbox_request(semantics, x=0.5, y=0.5)
    plotchar_request = build_plotchar_metrics_request_from_text_bbox_request(request)
    computed = compute_plotchar_extent_metrics(plotchar_request)
    assert computed.width > 0.0
    assert computed.height > 0.0

    inline = build_text_item_semantics(
        "A~B",
        direction="Across",
        func_code="~",
        font=21,
        font_height=0.025,
        font_quality="High",
    )
    inline_request = build_text_item_bbox_request(inline, x=0.5, y=0.5)
    try:
        compute_plotchar_extent_metrics(
            build_plotchar_metrics_request_from_text_bbox_request(inline_request)
        )
    except PlotcharUnsupportedError as exc:
        assert "function-code" in str(exc)
    else:
        raise AssertionError("inline Plotchar function-code commands must remain guarded")

    print("✅ Plotchar metrics Python mainline guard smoke passed")


if __name__ == "__main__":
    main()
