from __future__ import annotations

from dataclasses import dataclass

from ._plotchar_legacy_digitization import (
    LegacyDigitizationKey,
    legacy_digitization_index,
)
from ._plotchar_state import PlotcharState, PlotcharUnsupportedError


@dataclass(frozen=True)
class LegacyDigitizationStep:
    char: str
    font_family: str
    size_level: str
    case_mode: str
    inda_index: int


def _command_value_optional_int(token: str, command: str) -> int:
    raw = token[1:].strip()
    if raw == "":
        return 0

    try:
        value = int(raw)
    except ValueError as exc:
        raise PlotcharUnsupportedError(
            f"Legacy digitization command {command!r} received non-integer value {raw!r}."
        ) from exc

    if value < 0:
        raise PlotcharUnsupportedError(
            f"Legacy digitization command {command!r} received negative count {value}."
        )

    return value


def _body_from_real_string(chrs: str, state: PlotcharState) -> tuple[str, str]:
    code = chr(state.nfcc) if state.nfcc >= 0 else ":"
    text = str(chrs)

    across = f"{code}A{code}"
    down = f"{code}D{code}"

    if text.startswith(down):
        raise PlotcharUnsupportedError(
            "Legacy digitization trace currently supports Across strings only. Down-text remains guarded."
        )

    if text.startswith(across):
        return text[len(across):], code

    raise PlotcharUnsupportedError(
        "Legacy digitization trace expects a PLCHHQ real_string with Across prefix."
    )


def trace_legacy_digitization_steps(
    chrs: str,
    state: PlotcharState,
) -> tuple[LegacyDigitizationStep, ...]:
    body, code = _body_from_real_string(chrs, state)

    font_family = "roman"
    size_level = "principal"
    case_mode = "upper"

    previous_case_mode: str | None = None
    case_countdown = 0

    steps: list[LegacyDigitizationStep] = []

    def emit_char(char: str) -> None:
        nonlocal case_mode, previous_case_mode, case_countdown

        if case_mode == "upper":
            rendered_char = char.upper()
        elif case_mode == "lower":
            rendered_char = char.lower()
        else:
            rendered_char = char

        steps.append(
            LegacyDigitizationStep(
                char=rendered_char,
                font_family=font_family,
                size_level=size_level,
                case_mode=case_mode,
                inda_index=legacy_digitization_index(
                    rendered_char,
                    font_family=font_family,
                    size_level=size_level,
                    case_mode=case_mode,
                ),
            )
        )

        if case_countdown > 0:
            case_countdown -= 1
            if case_countdown == 0:
                case_mode = previous_case_mode or case_mode
                previous_case_mode = None

    i = 0
    while i < len(body):
        char = body[i]

        if char != code:
            emit_char(char)
            i += 1
            continue

        j = body.find(code, i + 1)
        if j < 0:
            emit_char(char)
            i += 1
            continue

        token = body[i + 1:j]
        if token == "":
            emit_char(code)
            i = j + 1
            continue

        command = token[0].upper()

        if command == "R":
            font_family = "roman"
        elif command == "G":
            font_family = "greek"
        elif command == "P":
            size_level = "principal"
        elif command == "I":
            size_level = "indexical"
        elif command == "K":
            size_level = "cartographic"
        elif command == "U":
            previous_case_mode = case_mode
            case_mode = "upper"
            case_countdown = _command_value_optional_int(token, command)
        elif command == "L":
            previous_case_mode = case_mode
            case_mode = "lower"
            case_countdown = _command_value_optional_int(token, command)
        else:
            raise PlotcharUnsupportedError(
                f"Legacy digitization trace does not yet map command {token!r}. "
                "Only R/G/P/I/K/U/L are supported in this trace stage."
            )

        i = j + 1

    return tuple(steps)


__all__ = [
    "LegacyDigitizationStep",
    "trace_legacy_digitization_steps",
]
