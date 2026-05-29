from __future__ import annotations

from climara.graphics._plotchar_function_code import (
    normalize_plotchar_func_code,
    parse_textitem_plotchar_real_string,
)
from climara.graphics._plotchar_state import PlotcharUnsupportedError


def assert_raises(message_part: str, func):
    try:
        func()
    except PlotcharUnsupportedError as exc:
        message = str(exc)
        assert message_part in message, message
    else:
        raise AssertionError(f"Expected PlotcharUnsupportedError containing {message_part!r}")


def main():
    parsed = parse_textitem_plotchar_real_string(
        "~A~ABC",
        func_code="~",
        default_font_number=21,
    )
    assert parsed.text == "ABC"
    assert parsed.direction_code == "A"
    assert parsed.prefix == "~A~"

    parsed = parse_textitem_plotchar_real_string(
        "~D~ABC",
        func_code="~",
        default_font_number=21,
    )
    assert parsed.text == "ABC"
    assert parsed.direction_code == "D"
    assert parsed.prefix == "~D~"
    assert [event.kind for event in parsed.events] == ["down", "text"]

    parsed = parse_textitem_plotchar_real_string(
        "~A~A~~B",
        func_code="~",
        default_font_number=21,
    )
    assert parsed.text == "A~B"

    parsed = parse_textitem_plotchar_real_string(
        "~A~A~F22~B",
        func_code="~",
        default_font_number=21,
    )
    assert parsed.text == "AB"

    parsed = parse_textitem_plotchar_real_string(
        "~A~A~S~B~E~C",
        func_code="~",
        default_font_number=21,
    )
    assert parsed.text == "ABC"
    assert [event.kind for event in parsed.events] == [
        "text",
        "superscript",
        "text",
        "end_script",
        "text",
    ]

    parsed = parse_textitem_plotchar_real_string(
        "~A~A~B~C~N~D",
        func_code="~",
        default_font_number=21,
    )
    assert parsed.text == "ACD"
    assert [event.kind for event in parsed.events] == [
        "text",
        "subscript",
        "text",
        "normal_script",
        "text",
    ]

    parsed = parse_textitem_plotchar_real_string(
        "~A~A~D2~BC~A~D",
        func_code="~",
        default_font_number=21,
    )
    assert parsed.text == "ABCD"
    assert [event.kind for event in parsed.events] == [
        "text",
        "down",
        "text",
        "across",
        "text",
    ]

    assert normalize_plotchar_func_code(-1) == ":"
    assert normalize_plotchar_func_code("") == "~"
    assert normalize_plotchar_func_code("~extra") == "~"

    assert_raises(
        "direction prefixes",
        lambda: parse_textitem_plotchar_real_string(
            "ABC",
            func_code="~",
            default_font_number=21,
        ),
    )

    assert_raises(
        "got command 'R'",
        lambda: parse_textitem_plotchar_real_string(
            "~A~A~R~C",
            func_code="~",
            default_font_number=21,
        ),
    )

    assert_raises(
        "Unterminated inline Plotchar function-code sequence",
        lambda: parse_textitem_plotchar_real_string(
            "~A~ABC~",
            func_code="~",
            default_font_number=21,
        ),
    )

    print("✅ Python Plotchar function-code guard smoke passed")


if __name__ == "__main__":
    main()
