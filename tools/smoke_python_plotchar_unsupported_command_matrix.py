from __future__ import annotations

from climara.graphics._plotchar_function_code import parse_textitem_plotchar_real_string
from climara.graphics._plotchar_state import PlotcharUnsupportedError


IMPLEMENTED_COMMANDS = set("ABCDEFHIKLNPSUVXYZ")
UNSUPPORTED_COMMANDS = [
    letter for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if letter not in IMPLEMENTED_COMMANDS
]


def assert_unsupported_command_guarded(letter: str) -> None:
    try:
        parse_textitem_plotchar_real_string(
            f"~A~A~{letter}~B",
            func_code="~",
            default_font_number=21,
        )
    except PlotcharUnsupportedError as exc:
        message = str(exc)
        assert f"got command '{letter}'" in message, message
    else:
        raise AssertionError(f"Unsupported function-code command {letter!r} parsed unexpectedly")


def main() -> None:
    if not UNSUPPORTED_COMMANDS:
        raise AssertionError("Unsupported command matrix is unexpectedly empty")

    for letter in UNSUPPORTED_COMMANDS:
        assert_unsupported_command_guarded(letter)

    # A few implemented commands should parse, to make sure this smoke is not
    # accidentally using the wrong function-code syntax.
    parse_textitem_plotchar_real_string("~A~A~B~C~N~D", func_code="~", default_font_number=21)
    parse_textitem_plotchar_real_string("~A~A~S~C~E~D", func_code="~", default_font_number=21)
    parse_textitem_plotchar_real_string("~A~A~D2~BC~A~D", func_code="~", default_font_number=21)

    print("✅ Python Plotchar unsupported command matrix smoke passed")


if __name__ == "__main__":
    main()
