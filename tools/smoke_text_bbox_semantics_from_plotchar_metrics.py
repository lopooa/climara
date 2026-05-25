from climara.graphics._plotchar_metrics import PlotcharExtentMetrics
from climara.graphics._text_bbox import TEXT_BBOX_COORD_NDC, build_text_item_bbox_request
from climara.graphics._text_bbox_semantics import (
    compute_text_bbox_from_plotchar_metrics,
    sanitize_plotchar_metrics,
    text_real_position_from_plotchar_metrics,
)
from climara.graphics._text_semantics import build_text_item_semantics


def almost_equal(value, expected, tol=1e-12):
    assert abs(value - expected) <= tol, (value, expected)


def assert_point(actual, expected):
    almost_equal(actual[0], expected[0])
    almost_equal(actual[1], expected[1])


def main():
    metrics = PlotcharExtentMetrics(
        dl=0.1,
        dr=0.3,
        db=0.05,
        dt=0.15,
    )

    center = build_text_item_bbox_request(
        build_text_item_semantics(
            "Demo",
            direction="Across",
            func_code="~",
            just="CenterCenter",
            angle=0,
            font=21,
            font_color="black",
            font_height=0.02,
        ),
        x=0.5,
        y=0.5,
    )

    real_x, real_y = text_real_position_from_plotchar_metrics(
        center,
        metrics,
    )

    almost_equal(real_x, 0.4)
    almost_equal(real_y, 0.45)

    result = compute_text_bbox_from_plotchar_metrics(
        center,
        metrics,
    )

    assert result.bbox.coordinate_space == TEXT_BBOX_COORD_NDC
    almost_equal(result.real_x, 0.4)
    almost_equal(result.real_y, 0.45)
    almost_equal(result.bbox.l, 0.3)
    almost_equal(result.bbox.r, 0.7)
    almost_equal(result.bbox.b, 0.4)
    almost_equal(result.bbox.t, 0.6)
    almost_equal(result.bbox.width, 0.4)
    almost_equal(result.bbox.height, 0.2)

    expected_corners = (
        (0.3, 0.4),
        (0.3, 0.6),
        (0.7, 0.6),
        (0.7, 0.4),
    )

    for actual, expected in zip(result.corners.points, expected_corners):
        assert_point(actual, expected)

    top_right = build_text_item_bbox_request(
        build_text_item_semantics(
            "Demo",
            direction="Across",
            func_code="~",
            just="TopRight",
            angle=0,
            font=21,
            font_color="black",
            font_height=0.02,
        ),
        x=0.5,
        y=0.5,
    )

    tr_x, tr_y = text_real_position_from_plotchar_metrics(
        top_right,
        metrics,
    )

    almost_equal(tr_x, 0.2)
    almost_equal(tr_y, 0.35)

    sanitized_large_dl = sanitize_plotchar_metrics(
        PlotcharExtentMetrics(
            dl=20.0,
            dr=0.0,
            db=0.0,
            dt=0.0,
        )
    )

    almost_equal(sanitized_large_dl.dl, 0.0001)
    almost_equal(sanitized_large_dl.dr, 0.0)
    almost_equal(sanitized_large_dl.db, 0.0001)
    almost_equal(sanitized_large_dl.dt, 0.0001)

    sanitized_zero_horizontal = sanitize_plotchar_metrics(
        PlotcharExtentMetrics(
            dl=0.0,
            dr=0.0,
            db=0.1,
            dt=0.2,
        )
    )

    almost_equal(sanitized_zero_horizontal.dl, 0.0001)
    almost_equal(sanitized_zero_horizontal.dr, 0.0001)
    almost_equal(sanitized_zero_horizontal.db, 0.1)
    almost_equal(sanitized_zero_horizontal.dt, 0.2)

    sanitized_zero_vertical = sanitize_plotchar_metrics(
        PlotcharExtentMetrics(
            dl=0.1,
            dr=0.2,
            db=0.0,
            dt=0.0,
        )
    )

    almost_equal(sanitized_zero_vertical.dl, 0.1)
    almost_equal(sanitized_zero_vertical.dr, 0.2)
    almost_equal(sanitized_zero_vertical.db, 0.0001)
    almost_equal(sanitized_zero_vertical.dt, 0.0001)

    rotated = compute_text_bbox_from_plotchar_metrics(
        build_text_item_bbox_request(
            build_text_item_semantics(
                "Demo",
                direction="Across",
                func_code="~",
                just="CenterCenter",
                angle=90,
                font=21,
                font_color="black",
                font_height=0.02,
            ),
            x=0.5,
            y=0.5,
        ),
        metrics,
    )

    almost_equal(rotated.bbox.width, 0.2)
    almost_equal(rotated.bbox.height, 0.4)

    print("✅ TextBBox semantics from Plotchar metrics smoke passed")


if __name__ == "__main__":
    main()
