from __future__ import annotations

from climara.graphics._plotchar_function_code import (
    decode_plain_plotchar_body_with_literal_escapes,
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
    assert decode_plain_plotchar_body_with_literal_escapes("ABC", func_code="~") == "ABC"
    assert decode_plain_plotchar_body_with_literal_escapes("A~~B", func_code="~") == "A~B"
    assert decode_plain_plotchar_body_with_literal_escapes("::::", func_code=":") == "::"

    escaped = parse_textitem_plotchar_real_string(
        "~A~A~~B",
        func_code="~",
        default_font_number=21,
    )
    assert escaped.text == "A~B"
    assert escaped.prefix == "~A~"
    assert escaped.direction_code == "A"
    assert [event.kind for event in escaped.events] == ["text"]

    down = parse_textitem_plotchar_real_string(
        "~D~ABC",
        func_code="~",
        default_font_number=21,
    )
    assert down.text == "ABC"
    assert down.prefix == "~D~"
    assert down.direction_code == "D"
    assert [event.kind for event in down.events] == ["down", "text"]

    font_change = parse_textitem_plotchar_real_string(
        "~A~A~F22~B~F~C",
        func_code="~",
        default_font_number=21,
    )
    assert font_change.text == "ABC"
    assert [segment.text for segment in font_change.segments] == ["A", "B", "C"]
    assert [segment.font_number for segment in font_change.segments] == [21, 22, 21]

    script = parse_textitem_plotchar_real_string(
        "~A~A~S~B~E~C",
        func_code="~",
        default_font_number=21,
    )
    assert script.text == "ABC"
    assert [event.kind for event in script.events] == [
        "text",
        "superscript",
        "text",
        "end_script",
        "text",
    ]

    subscript = parse_textitem_plotchar_real_string(
        "~A~A~B~C~N~D",
        func_code="~",
        default_font_number=21,
    )
    assert subscript.text == "ACD"
    assert [event.kind for event in subscript.events] == [
        "text",
        "subscript",
        "text",
        "normal_script",
        "text",
    ]

    down_body = parse_textitem_plotchar_real_string(
        "~A~A~D2~BC~A~D",
        func_code="~",
        default_font_number=21,
    )
    assert down_body.text == "ABCD"
    assert [event.kind for event in down_body.events] == [
        "text",
        "down",
        "text",
        "across",
        "text",
    ]

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

    print("✅ Python Plotchar function-code literal escape smoke passed")


if __name__ == "__main__":
    main()
