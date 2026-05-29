from __future__ import annotations

from climara.graphics._plotchar_function_code import (
    parse_plotchar_decimal_integer,
    parse_textitem_plotchar_real_string,
)
from climara.graphics._plotchar_state import PlotcharUnsupportedError


def assert_integer(text: str, start: int, value, next_index: int, had_integer: bool):
    parsed = parse_plotchar_decimal_integer(text, start)
    assert parsed.value == value, parsed
    assert parsed.next_index == next_index, parsed
    assert parsed.had_integer is had_integer, parsed


def assert_raises(message_part: str, func):
    try:
        func()
    except PlotcharUnsupportedError as exc:
        message = str(exc)
        assert message_part in message, message
    else:
        raise AssertionError(f"Expected PlotcharUnsupportedError containing {message_part!r}")


def main():
    assert_integer("22~", 0, 22, 2, True)
    assert_integer("+22~", 0, 22, 3, True)
    assert_integer("-22~", 0, -22, 3, True)
    assert_integer("0~", 0, 0, 1, True)
    assert_integer("F22~", 1, 22, 3, True)
    assert_integer("~", 0, None, 0, False)
    assert_integer("ABC", 0, None, 0, False)
    assert_integer("ABC", 2, None, 2, False)

    assert_raises(
        "sign with no following decimal digit",
        lambda: parse_plotchar_decimal_integer("+~", 0),
    )
    assert_raises(
        "sign with no following decimal digit",
        lambda: parse_plotchar_decimal_integer("-~", 0),
    )

    parsed = parse_textitem_plotchar_real_string(
        "~A~A~F+22~B",
        func_code="~",
        default_font_number=21,
    )
    assert parsed.text == "AB"
    assert [segment.text for segment in parsed.segments] == ["A", "B"]
    assert [segment.font_number for segment in parsed.segments] == [21, 22]

    parsed = parse_textitem_plotchar_real_string(
        "~A~A~F-22~B",
        func_code="~",
        default_font_number=21,
    )
    assert parsed.text == "AB"
    assert [segment.font_number for segment in parsed.segments] == [21, 22]

    parsed = parse_textitem_plotchar_real_string(
        "~A~A~F0~B",
        func_code="~",
        default_font_number=21,
    )
    assert parsed.text == "AB"
    assert [segment.font_number for segment in parsed.segments] == [21, 0]

    parsed = parse_textitem_plotchar_real_string(
        "~A~A~F23~B",
        func_code="~",
        default_font_number=21,
    )
    assert parsed.text == "AB"
    assert [segment.font_number for segment in parsed.segments] == [21, 1]

    parsed = parse_textitem_plotchar_real_string(
        "~A~A~F~B",
        func_code="~",
        default_font_number=21,
    )
    assert parsed.text == "AB"
    assert [segment.font_number for segment in parsed.segments] == [21, 21]

    assert_raises(
        "sign with no following decimal digit",
        lambda: parse_textitem_plotchar_real_string(
            "~A~A~F+~B",
            func_code="~",
            default_font_number=21,
        ),
    )

    print("✅ Python Plotchar PCGTDI decimal parser smoke passed")


if __name__ == "__main__":
    main()
