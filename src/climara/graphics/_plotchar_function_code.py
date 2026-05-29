from __future__ import annotations

from dataclasses import dataclass

from ._plotchar_state import PlotcharUnsupportedError, normalize_plotchar_font_number


@dataclass(frozen=True)
class PlotcharDecimalInteger:
    value: int | None
    next_index: int
    had_integer: bool


@dataclass(frozen=True)
class PlotcharTextSegment:
    text: str
    font_number: int


@dataclass(frozen=True)
class PlotcharTextEvent:
    kind: str
    text: str = ""
    font_number: int = 1
    value: int = 0
    use_q_unit: bool = False


@dataclass(frozen=True)
class PlotcharParsedText:
    text: str
    func_code: str
    direction_code: str
    prefix: str
    raw: str
    segments: tuple[PlotcharTextSegment, ...]
    events: tuple[PlotcharTextEvent, ...]


def normalize_plotchar_func_code(value: str | int) -> str:
    if isinstance(value, int):
        if value < 0:
            return ":"
        return chr(value)

    text = str(value)
    if not text:
        return "~"

    return text[0]


def parse_plotchar_decimal_integer(text: str, start: int) -> PlotcharDecimalInteger:
    if start < 0 or start > len(text):
        raise IndexError(f"start index out of range for PCGTDI parser: {start}")

    i = start
    sign = 1

    if i < len(text) and text[i] in "+-":
        sign = -1 if text[i] == "-" else 1

        if i + 1 >= len(text) or not text[i + 1].isdigit():
            raise PlotcharUnsupportedError(
                "PCGTDI-style signed integer parser encountered a sign with no "
                "following decimal digit. This ambiguous edge case remains guarded."
            )

        i += 1

    digit_start = i

    while i < len(text) and text[i].isdigit():
        i += 1

    if i == digit_start:
        return PlotcharDecimalInteger(value=None, next_index=start, had_integer=False)

    return PlotcharDecimalInteger(
        value=sign * int(text[digit_start:i]),
        next_index=i,
        had_integer=True,
    )


def _apply_case_mode(char: str, case_mode: str) -> str:
    if case_mode == "upper":
        return char.upper()
    if case_mode == "lower":
        return char.lower()
    return char


def _append_text_event(
    events: list[PlotcharTextEvent],
    text_parts: list[str],
    *,
    font_number: int,
) -> None:
    if not text_parts:
        return

    text = "".join(text_parts)
    if text:
        events.append(
            PlotcharTextEvent(
                kind="text",
                text=text,
                font_number=int(font_number),
            )
        )
    text_parts.clear()


def _read_optional_integer_and_q(
    body: str,
    index: int,
) -> tuple[int, int, bool]:
    parsed_integer = parse_plotchar_decimal_integer(body, index)
    value = int(parsed_integer.value) if parsed_integer.had_integer else 0
    i = parsed_integer.next_index if parsed_integer.had_integer else index

    use_q_unit = False
    if i < len(body) and body[i].upper() == "Q":
        use_q_unit = True
        i += 1

    return value, i, use_q_unit


def parse_plotchar_body_events(
    body: str,
    *,
    func_code: str | int,
    default_font_number: int,
) -> tuple[PlotcharTextEvent, ...]:
    code = normalize_plotchar_func_code(func_code)
    default_font = normalize_plotchar_font_number(default_font_number)
    current_font = default_font

    events: list[PlotcharTextEvent] = []
    text_parts: list[str] = []

    in_function_code = False
    i = 0

    case_mode = "upper"
    previous_case_mode = case_mode
    case_remaining: int | None = None

    def append_glyph_char(char: str) -> None:
        nonlocal case_mode, previous_case_mode, case_remaining

        text_parts.append(_apply_case_mode(char, case_mode))

        if case_remaining is not None and case_remaining > 0:
            case_remaining -= 1
            if case_remaining == 0:
                case_mode = previous_case_mode
                case_remaining = None

    while i < len(body):
        char = body[i]

        if not in_function_code:
            if char != code:
                append_glyph_char(char)
                i += 1
                continue

            if i + 1 < len(body) and body[i + 1] == code:
                append_glyph_char(code)
                i += 2
                continue

            in_function_code = True
            i += 1
            continue

        if char == code:
            in_function_code = False
            i += 1
            continue

        if char in " ,":
            i += 1
            continue

        command = char.upper()
        i += 1

        if command == "F":
            parsed_integer = parse_plotchar_decimal_integer(body, i)
            _append_text_event(events, text_parts, font_number=current_font)

            if not parsed_integer.had_integer:
                current_font = default_font
            else:
                current_font = normalize_plotchar_font_number(parsed_integer.value)
                i = parsed_integer.next_index

            continue

        if command in {"P", "I", "K"}:
            _append_text_event(events, text_parts, font_number=current_font)
            events.append(
                PlotcharTextEvent(
                    kind="size",
                    value={"P": 1, "I": 2, "K": 3}[command],
                    font_number=current_font,
                )
            )
            continue

        if command in {"B", "S"}:
            _append_text_event(events, text_parts, font_number=current_font)
            parsed_integer = parse_plotchar_decimal_integer(body, i)
            value = int(parsed_integer.value) if parsed_integer.had_integer else 0
            if parsed_integer.had_integer:
                i = parsed_integer.next_index

            events.append(
                PlotcharTextEvent(
                    kind="subscript" if command == "B" else "superscript",
                    value=value,
                    font_number=current_font,
                )
            )
            continue

        if command in {"E", "N"}:
            _append_text_event(events, text_parts, font_number=current_font)
            events.append(
                PlotcharTextEvent(
                    kind="end_script" if command == "E" else "normal_script",
                    font_number=current_font,
                )
            )
            continue

        if command == "D":
            _append_text_event(events, text_parts, font_number=current_font)
            parsed_integer = parse_plotchar_decimal_integer(body, i)
            if parsed_integer.had_integer:
                value = int(parsed_integer.value)
                i = parsed_integer.next_index
            else:
                value = -1

            events.append(
                PlotcharTextEvent(
                    kind="down",
                    value=value,
                    font_number=current_font,
                )
            )
            continue

        if command == "A":
            _append_text_event(events, text_parts, font_number=current_font)
            events.append(
                PlotcharTextEvent(
                    kind="across",
                    font_number=current_font,
                )
            )
            continue

        if command in {"U", "L"}:
            parsed_integer = parse_plotchar_decimal_integer(body, i)
            _append_text_event(events, text_parts, font_number=current_font)

            previous_case_mode = "lower" if command == "U" else "upper"
            case_mode = "upper" if command == "U" else "lower"

            if parsed_integer.had_integer:
                i = parsed_integer.next_index
                count = int(parsed_integer.value)

                if count > 0:
                    case_remaining = count
                else:
                    case_remaining = None
            else:
                case_remaining = None

            continue

        if command == "C":
            _append_text_event(events, text_parts, font_number=current_font)
            events.append(
                PlotcharTextEvent(
                    kind="carriage",
                    font_number=current_font,
                )
            )
            continue

        if command in {"H", "V"}:
            _append_text_event(events, text_parts, font_number=current_font)
            value, i, use_q_unit = _read_optional_integer_and_q(body, i)

            events.append(
                PlotcharTextEvent(
                    kind="hmove" if command == "H" else "vmove",
                    value=value,
                    use_q_unit=use_q_unit,
                    font_number=current_font,
                )
            )
            continue

        if command in {"X", "Y", "Z"}:
            _append_text_event(events, text_parts, font_number=current_font)
            value, i, use_q_unit = _read_optional_integer_and_q(body, i)

            events.append(
                PlotcharTextEvent(
                    kind={"X": "xzoom", "Y": "yzoom", "Z": "zzoom"}[command],
                    value=value,
                    use_q_unit=use_q_unit,
                    font_number=current_font,
                )
            )
            continue

        raise PlotcharUnsupportedError(
            "Inline Plotchar function-code body command is guarded until the "
            "corresponding PLCHHQ branch is mapped. This Python subset currently "
            "implements F, P/I/K, B/S/E/N, D/A, H/V, X/Y/Z, C, U/L, doubled signal "
            f"literal escapes, and PCGTDI-style integer parsing; got command {command!r}."
        )

    if in_function_code:
        raise PlotcharUnsupportedError(
            "Unterminated inline Plotchar function-code sequence is guarded. "
            "A single function-code signal starts command processing and must be "
            "closed before returning to glyph text."
        )

    _append_text_event(events, text_parts, font_number=current_font)
    return tuple(events)


def parse_plotchar_body_segments(
    body: str,
    *,
    func_code: str | int,
    default_font_number: int,
) -> tuple[PlotcharTextSegment, ...]:
    events = parse_plotchar_body_events(
        body,
        func_code=func_code,
        default_font_number=default_font_number,
    )
    return tuple(
        PlotcharTextSegment(text=event.text, font_number=event.font_number)
        for event in events
        if event.kind == "text" and event.text
    )


def decode_plain_plotchar_body_with_literal_escapes(body: str, *, func_code: str) -> str:
    events = parse_plotchar_body_events(
        body,
        func_code=func_code,
        default_font_number=1,
    )

    if any(event.kind != "text" for event in events):
        raise PlotcharUnsupportedError(
            "Non-text function-code events cannot be decoded as plain glyph text. "
            "Use parse_textitem_plotchar_real_string for event-aware parsing."
        )

    return "".join(event.text for event in events)



def parse_textitem_plotchar_real_string(
    chrs: str,
    *,
    func_code: str | int,
    default_font_number: int = 1,
) -> PlotcharParsedText:
    code = normalize_plotchar_func_code(func_code)
    default_font = normalize_plotchar_font_number(default_font_number)

    across_prefix = f"{code}A{code}"
    down_prefix = f"{code}D{code}"

    if chrs.startswith(across_prefix):
        direction_code = "A"
        prefix = across_prefix
        body = chrs[len(across_prefix):]
        events = parse_plotchar_body_events(
            body,
            func_code=code,
            default_font_number=default_font,
        )
    elif chrs.startswith(down_prefix):
        direction_code = "D"
        prefix = down_prefix
        body = chrs[len(down_prefix):]
        body_events = parse_plotchar_body_events(
            body,
            func_code=code,
            default_font_number=default_font,
        )
        events = (
            PlotcharTextEvent(
                kind="down",
                value=-1,
                font_number=default_font,
            ),
            *body_events,
        )
    else:
        raise PlotcharUnsupportedError(
            "Python PLCHHQ fontcap extent core currently accepts TextItem.c "
            "real_string direction prefixes. "
            f"Expected {across_prefix!r} or {down_prefix!r}; got {chrs!r}."
        )

    segments = tuple(
        PlotcharTextSegment(text=event.text, font_number=event.font_number)
        for event in events
        if event.kind == "text" and event.text
    )
    text = "".join(segment.text for segment in segments)

    return PlotcharParsedText(
        text=text,
        func_code=code,
        direction_code=direction_code,
        prefix=prefix,
        raw=chrs,
        segments=segments,
        events=events,
    )




# Source-mapped Roman wrapper:
# NCL PLCHHQ command R sets IFNT=IFRO. The current Python high-quality
# fontcap runtime implements the Roman path, so R is a no-op for this subset.
# NCL command G sets IFNT=IFGR; Greek glyph selection is not mapped here and
# must remain guarded.
_parse_textitem_plotchar_real_string_before_roman_wrapper = parse_textitem_plotchar_real_string


def _strip_roman_command_preserve_greek_guard(chrs, func_code):
    try:
        code = str(func_code)[0]
    except Exception:
        code = ":"

    roman_token = f"{code}R{code}"
    roman_token_lower = f"{code}r{code}"
    greek_token = f"{code}G{code}"
    greek_token_lower = f"{code}g{code}"

    if greek_token in chrs or greek_token_lower in chrs:
        raise PlotcharUnsupportedError(
            "Plotchar G Greek-font command remains guarded. NCL PLCHHQ maps Greek "
            "through IFGR/INDA/IDDA digitization offsets, not the current fontcap "
            "font-number path. Implement the non-fontcap/PWRITX-digitization branch "
            "before enabling G."
        )

    return chrs.replace(roman_token, "").replace(roman_token_lower, "")


from functools import wraps as _plotchar_wraps


@_plotchar_wraps(_parse_textitem_plotchar_real_string_before_roman_wrapper)
def parse_textitem_plotchar_real_string(*args, **kwargs):
    if args:
        chrs = args[0]
        rest = args[1:]
    else:
        chrs = kwargs.get("chrs")
        rest = ()

    func_code = kwargs.get("func_code", ":")
    if chrs is None:
        return _parse_textitem_plotchar_real_string_before_roman_wrapper(*args, **kwargs)

    cleaned = _strip_roman_command_preserve_greek_guard(str(chrs), func_code)

    if args:
        return _parse_textitem_plotchar_real_string_before_roman_wrapper(
            cleaned,
            *rest,
            **kwargs,
        )

    kwargs = dict(kwargs)
    kwargs["chrs"] = cleaned
    return _parse_textitem_plotchar_real_string_before_roman_wrapper(**kwargs)



# Source-mapped U/L case wrapper for the supported Python Plotchar subset.
# U switches subsequent drawable characters to upper case.
# L switches subsequent drawable characters to lower case.
# A numeric suffix, e.g. U3 or L3, applies the case mode to that many
# following drawable characters and then restores the previous case mode.
_parse_textitem_plotchar_real_string_before_case_wrapper = parse_textitem_plotchar_real_string


def _case_wrapper_parse_optional_int(token, command):
    raw = token[1:].strip()
    if raw == "":
        return 0

    try:
        value = int(raw)
    except ValueError as exc:
        raise PlotcharUnsupportedError(
            f"Plotchar {command} case command received non-integer value {raw!r}."
        ) from exc

    if value < 0:
        raise PlotcharUnsupportedError(
            f"Plotchar {command} case command received negative count {value}."
        )

    return value


def _preprocess_roman_case_preserve_greek_guard(chrs, func_code):
    try:
        code = str(func_code)[0]
    except Exception:
        code = ":"

    body = str(chrs)
    out = []
    case_mode = None
    previous_case_mode = None
    countdown = 0

    def emit_char(char):
        nonlocal case_mode, previous_case_mode, countdown

        if case_mode == "upper":
            out_char = char.upper()
        elif case_mode == "lower":
            out_char = char.lower()
        else:
            out_char = char

        out.append(out_char)

        if countdown > 0:
            countdown -= 1
            if countdown == 0:
                case_mode = previous_case_mode
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
            out.append(char)
            i += 1
            continue

        token = body[i + 1:j]
        if token == "":
            emit_char(code)
            i = j + 1
            continue

        command = token[0].upper()

        if command == "R":
            # Roman is the current supported high-quality subset.
            i = j + 1
            continue

        if command == "G":
            raise PlotcharUnsupportedError(
                "Plotchar G Greek-font command remains guarded. NCL PLCHHQ maps Greek "
                "through IFGR/INDA/IDDA digitization offsets, not the current fontcap "
                "font-number path. Implement the non-fontcap/PWRITX-digitization branch "
                "before enabling G."
            )

        if command == "U":
            previous_case_mode = case_mode
            case_mode = "upper"
            countdown = _case_wrapper_parse_optional_int(token, command)
            i = j + 1
            continue

        if command == "L":
            previous_case_mode = case_mode
            case_mode = "lower"
            countdown = _case_wrapper_parse_optional_int(token, command)
            i = j + 1
            continue

        out.append(code)
        out.append(token)
        out.append(code)
        i = j + 1

    return "".join(out)


from functools import wraps as _plotchar_case_wraps


@_plotchar_case_wraps(_parse_textitem_plotchar_real_string_before_case_wrapper)
def parse_textitem_plotchar_real_string(*args, **kwargs):
    if args:
        chrs = args[0]
        rest = args[1:]
    else:
        chrs = kwargs.get("chrs")
        rest = ()

    func_code = kwargs.get("func_code", ":")
    if chrs is None:
        return _parse_textitem_plotchar_real_string_before_case_wrapper(*args, **kwargs)

    cleaned = _preprocess_roman_case_preserve_greek_guard(str(chrs), func_code)

    if args:
        return _parse_textitem_plotchar_real_string_before_case_wrapper(
            cleaned,
            *rest,
            **kwargs,
        )

    kwargs = dict(kwargs)
    kwargs["chrs"] = cleaned
    return _parse_textitem_plotchar_real_string_before_case_wrapper(**kwargs)



# Restore text-event case after the legacy parser path. The legacy parser may
# normalize plain lowercase to uppercase; this wrapper preserves the text
# implied by the source-mapped U/L preprocessing layer while keeping the
# original event structure.
_parse_textitem_plotchar_real_string_before_case_text_restore_wrapper = parse_textitem_plotchar_real_string


def _case_text_segments_from_cleaned_real_string(chrs, func_code):
    try:
        code = str(func_code)[0]
    except Exception:
        code = ":"

    text = str(chrs)

    across_prefix = f"{code}A{code}"
    down_prefix = f"{code}D{code}"

    if text.startswith(across_prefix):
        body = text[len(across_prefix):]
    elif text.startswith(down_prefix):
        body = text[len(down_prefix):]
    else:
        body = text

    segments = []
    buffer = []

    def flush():
        if buffer:
            segments.append("".join(buffer))
            buffer.clear()

    i = 0
    while i < len(body):
        char = body[i]

        if char != code:
            buffer.append(char)
            i += 1
            continue

        j = body.find(code, i + 1)
        if j < 0:
            buffer.append(char)
            i += 1
            continue

        token = body[i + 1:j]
        if token == "":
            buffer.append(code)
            i = j + 1
            continue

        flush()
        i = j + 1

    flush()
    return segments


from dataclasses import is_dataclass as _plotchar_case_is_dataclass
from dataclasses import replace as _plotchar_case_replace


def _restore_case_on_parsed_text_events(parsed, segments):
    if not segments:
        return parsed

    events = list(getattr(parsed, "events", ()))
    text_event_indices = [
        i for i, event in enumerate(events)
        if getattr(event, "kind", None) == "text"
    ]

    if len(text_event_indices) != len(segments):
        return parsed

    for index, segment in zip(text_event_indices, segments):
        event = events[index]

        if _plotchar_case_is_dataclass(event):
            events[index] = _plotchar_case_replace(event, text=segment)
        else:
            event.text = segment
            events[index] = event

    restored_text = "".join(segments)

    if _plotchar_case_is_dataclass(parsed):
        return _plotchar_case_replace(
            parsed,
            text=restored_text,
            events=tuple(events),
        )

    parsed.text = restored_text
    parsed.events = tuple(events)
    return parsed


@_plotchar_case_wraps(_parse_textitem_plotchar_real_string_before_case_text_restore_wrapper)
def parse_textitem_plotchar_real_string(*args, **kwargs):
    if args:
        chrs = args[0]
    else:
        chrs = kwargs.get("chrs")

    func_code = kwargs.get("func_code", ":")

    parsed = _parse_textitem_plotchar_real_string_before_case_text_restore_wrapper(
        *args,
        **kwargs,
    )

    if chrs is None:
        return parsed

    cleaned = _preprocess_roman_case_preserve_greek_guard(str(chrs), func_code)
    segments = _case_text_segments_from_cleaned_real_string(cleaned, func_code)

    return _restore_case_on_parsed_text_events(parsed, segments)
