from __future__ import annotations

from climara.graphics._text_bbox import build_text_item_bbox_request, compute_text_item_bbox
from climara.graphics._text_semantics import build_text_item_semantics


def assert_guarded(message_part: str, func) -> None:
    try:
        func()
    except Exception as exc:
        message = str(exc)
        assert message_part in message, message
    else:
        raise AssertionError(f"Expected guarded failure containing {message_part!r}")


def compute_text(text: str, *, font=21, font_quality="High"):
    semantics = build_text_item_semantics(
        text,
        direction="Across",
        func_code="~",
        just="CenterCenter",
        angle=0.0,
        font=font,
        font_height=0.03,
        font_quality=font_quality,
    )
    request = build_text_item_bbox_request(semantics, x=0.5, y=0.5)
    return compute_text_item_bbox(request)


def main():
    high = compute_text("ABC", font=21, font_quality="High")
    assert high.width > 0.0
    assert high.height > 0.0

    for quality in ("Medium", "Low"):
        assert_guarded(
            "high-quality fontcap branch",
            lambda quality=quality: compute_text("ABC", font=21, font_quality=quality),
        )

    assert_guarded(
        "Workstation",
        lambda: compute_text("ABC", font=21, font_quality="Workstation"),
    )

    assert_guarded(
        "PWRITX",
        lambda: compute_text("ABC", font=0, font_quality="High"),
    )

    print("✅ Python Plotchar quality/PWRITX guard smoke passed")


if __name__ == "__main__":
    main()
