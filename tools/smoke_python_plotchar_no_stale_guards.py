from __future__ import annotations

import ast
import re
from pathlib import Path

from climara.graphics._plotchar_function_code import parse_textitem_plotchar_real_string
from climara.graphics._plotchar_state import PlotcharUnsupportedError


ROOT = Path(__file__).resolve().parents[1]

IMPLEMENTED_COMMANDS = {
    "A": "Across direction",
    "B": "subscript",
    "C": "carriage return",
    "D": "Down direction",
    "E": "end script",
    "F": "font change",
    "H": "horizontal movement",
    "I": "indexical size",
    "K": "cartographic size",
    "L": "lower case",
    "N": "normal script",
    "P": "principal size",
    "S": "superscript",
    "U": "upper case",
    "V": "vertical movement",
    "X": "x zoom",
    "Y": "y zoom",
    "Z": "z zoom",
}

# R is intentionally kept as a representative unsupported command until its
# PLCHHQ source branch is mapped. Do not replace this with an implemented command.
UNSUPPORTED_SENTINEL = "R"


def runner_smokes() -> list[str]:
    runner = ROOT / "tools" / "run_python_mainline_smokes.py"
    tree = ast.parse(runner.read_text(encoding="utf-8"))

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            if any(isinstance(target, ast.Name) and target.id == "SMOKE_SCRIPTS" for target in node.targets):
                return [
                    str(elt.value)
                    for elt in node.value.elts
                    if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
                ]

    raise AssertionError("run_python_mainline_smokes.py does not define SMOKE_SCRIPTS")


def assert_runner_files_exist() -> None:
    missing = [script for script in runner_smokes() if not (ROOT / script).exists()]
    if missing:
        raise AssertionError(
            "run_python_mainline_smokes.py references missing smoke files:\n"
            + "\n".join(missing)
        )


def assert_no_stale_guard_assertions() -> None:
    problems: list[str] = []

    smoke_files = sorted((ROOT / "tools").glob("smoke_python_plotchar_*.py"))

    for path in smoke_files:
        rel = path.relative_to(ROOT)
        text = path.read_text(encoding="utf-8")

        for command, meaning in IMPLEMENTED_COMMANDS.items():
            stale_patterns = [
                f"got command '{command}'",
                f"command {command!r}",
                f"{command} must remain guarded",
                f"{meaning} must remain guarded",
            ]

            for pattern in stale_patterns:
                if pattern in text:
                    # A smoke may mention an implemented command while asserting
                    # that it parses successfully. The stale case we want to
                    # reject is when it appears near assert_raises or guarded wording.
                    for match in re.finditer(re.escape(pattern), text):
                        window = text[max(0, match.start() - 220): match.end() + 220]
                        lowered = window.lower()
                        # Avoid false positives such as "API must remain guarded",
                        # where the last character of "API" is the implemented
                        # command letter "I". Stale command guards should mention
                        # a real function-code command, not arbitrary prose.
                        left = text[max(0, match.start() - 1): match.start()]
                        right = text[match.end(): match.end() + 1]
                        command_is_standalone = not left.isalpha() and not right.isalpha()

                        if command_is_standalone and (
                            "assert_raises" in window or "guarded" in lowered or "unsupported" in lowered
                        ):
                            problems.append(
                                f"{rel}: stale guard wording for implemented command {command}: {pattern!r}"
                            )

    if problems:
        raise AssertionError(
            "Stale guarded assertions found for commands that are now implemented:\n"
            + "\n".join(problems)
        )


def assert_implemented_commands_parse() -> None:
    cases = {
        "A": "~A~A~D1~B~A~C",
        "B": "~A~A~B~B~N~C",
        "C": "~A~A~C~B",
        "D": "~D~ABC",
        "E": "~A~A~S~B~E~C",
        "F": "~A~A~F21~B",
        "H": "~A~A~H1~B",
        "I": "~A~A~I~B",
        "K": "~A~A~K~B",
        "L": "~A~AB~L2~CD",
        "N": "~A~A~B~B~N~C",
        "P": "~A~A~I~B~P~C",
        "S": "~A~A~S~B~E~C",
        "U": "~A~ab~U2~cd",
        "V": "~A~A~V1~B",
        "X": "~A~A~X100~B",
        "Y": "~A~A~Y100~B",
        "Z": "~A~A~Z100~B",
    }

    for command, real_string in cases.items():
        parsed = parse_textitem_plotchar_real_string(
            real_string,
            func_code="~",
            default_font_number=21,
        )
        assert parsed.text, (command, real_string, parsed)


def assert_unsupported_sentinel_still_guarded() -> None:
    try:
        parse_textitem_plotchar_real_string(
            f"~A~A~{UNSUPPORTED_SENTINEL}~B",
            func_code="~",
            default_font_number=21,
        )
    except PlotcharUnsupportedError as exc:
        assert f"got command '{UNSUPPORTED_SENTINEL}'" in str(exc), str(exc)
    else:
        raise AssertionError(
            f"Unsupported sentinel command {UNSUPPORTED_SENTINEL!r} unexpectedly parsed"
        )


def main() -> None:
    assert_runner_files_exist()
    assert_no_stale_guard_assertions()
    assert_implemented_commands_parse()
    assert_unsupported_sentinel_still_guarded()

    print("✅ Python Plotchar no-stale-guards smoke passed")


if __name__ == "__main__":
    main()
