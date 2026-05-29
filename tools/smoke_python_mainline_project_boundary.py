from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "climara"

FORBIDDEN_CALL_NAMES = {
    "browser_text_metrics",
    "svg_text_metrics",
    "fixed_width",
    "fixed_width_metrics",
    "character_count_metrics",
    "estimate_text_metrics",
    "estimate_plotchar_metrics",
    "measureText",
    "getComputedTextLength",
}

FORBIDDEN_SYMBOL_NAMES = {
    "browser_text_metrics",
    "svg_text_metrics",
    "fixed_width_metrics",
    "character_count_metrics",
    "estimate_text_metrics",
    "estimate_plotchar_metrics",
}

PLOTCHAR_METRIC_TARGET_NAMES = {
    "dl",
    "dr",
    "db",
    "dt",
    "dstl",
    "dstr",
    "dstb",
    "dstt",
    "width",
    "height",
    "metrics",
    "plotchar_metrics",
    "extent_metrics",
}

TEXT_LENGTH_SOURCE_NAMES = {
    "text",
    "string",
    "real_string",
    "chrs",
    "chars",
    "label",
    "title",
}


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )


def assert_status_report_runs() -> None:
    result = run([sys.executable, "tools/report_python_plotchar_mainline_status.py"])
    out = result.stdout

    required = (
        "Python Plotchar mainline status",
        "Current mainline:",
        "climara runtime mainline is Python implementation",
        "Unsupported PLCHHQ branches remain guarded",
        "No fixed-width text metrics",
        "No character-count width estimates",
        "No SVG/browser text metrics",
    )

    missing = [item for item in required if item not in out]
    if missing:
        raise AssertionError(
            "Python mainline status report is missing required wording: "
            + ", ".join(missing)
        )


def node_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id

    if isinstance(node, ast.Attribute):
        base = node_name(node.value)
        if base:
            return f"{base}.{node.attr}"
        return node.attr

    if isinstance(node, ast.Subscript):
        return node_name(node.value)

    if isinstance(node, ast.Call):
        return node_name(node.func)

    return ""


def lowered_node_names(node: ast.AST) -> set[str]:
    names: set[str] = set()

    for child in ast.walk(node):
        name = node_name(child)
        if name:
            names.add(name.lower())

    return names


def target_names(targets: list[ast.expr]) -> set[str]:
    names: set[str] = set()

    for target in targets:
        for child in ast.walk(target):
            name = node_name(child)
            if name:
                names.add(name.split(".")[-1].lower())

    return names


def contains_len_of_text(node: ast.AST) -> bool:
    for child in ast.walk(node):
        if not isinstance(child, ast.Call):
            continue

        if node_name(child.func) != "len":
            continue

        if not child.args:
            continue

        arg_names = lowered_node_names(child.args[0])

        if any(name.split(".")[-1] in TEXT_LENGTH_SOURCE_NAMES for name in arg_names):
            return True

        if isinstance(child.args[0], ast.Attribute):
            attr = child.args[0].attr.lower()
            if attr in TEXT_LENGTH_SOURCE_NAMES:
                return True

    return False


def len_text_feeds_metric_assignment(node: ast.AST) -> bool:
    if isinstance(node, ast.Assign):
        names = target_names(node.targets)
        return bool(names & PLOTCHAR_METRIC_TARGET_NAMES) and contains_len_of_text(node.value)

    if isinstance(node, ast.AnnAssign):
        names = target_names([node.target])
        return (
            bool(names & PLOTCHAR_METRIC_TARGET_NAMES)
            and node.value is not None
            and contains_len_of_text(node.value)
        )

    if isinstance(node, ast.AugAssign):
        names = target_names([node.target])
        return bool(names & PLOTCHAR_METRIC_TARGET_NAMES) and contains_len_of_text(node.value)

    if isinstance(node, ast.Return):
        value = node.value
        if value is None:
            return False

        if isinstance(value, ast.Call):
            func_name = node_name(value.func).lower()
            if "plotchar" in func_name or "metrics" in func_name or "extent" in func_name:
                for keyword in value.keywords:
                    if keyword.arg and keyword.arg.lower() in PLOTCHAR_METRIC_TARGET_NAMES:
                        if contains_len_of_text(keyword.value):
                            return True

        return False

    return False


def assert_no_forbidden_runtime_fallbacks() -> None:
    problems: list[str] = []

    for path in sorted(SRC.rglob("*.py")):
        rel = path.relative_to(ROOT)
        text = path.read_text(encoding="utf-8")

        try:
            tree = ast.parse(text, filename=str(path))
        except SyntaxError as exc:
            raise AssertionError(f"Could not parse {rel}: {exc}") from exc

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                name = node_name(node.func)
                short = name.split(".")[-1]

                if short in FORBIDDEN_CALL_NAMES:
                    problems.append(
                        f"{rel}:{node.lineno}: forbidden fallback call {name}(...)"
                    )

            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if node.name in FORBIDDEN_SYMBOL_NAMES:
                    problems.append(
                        f"{rel}:{node.lineno}: forbidden fallback definition {node.name}"
                    )

            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.name in FORBIDDEN_SYMBOL_NAMES:
                        problems.append(
                            f"{rel}:{node.lineno}: forbidden fallback import {alias.name}"
                        )

            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split(".")[-1] in FORBIDDEN_SYMBOL_NAMES:
                        problems.append(
                            f"{rel}:{node.lineno}: forbidden fallback import {alias.name}"
                        )

            if len_text_feeds_metric_assignment(node):
                lineno = getattr(node, "lineno", "?")
                problems.append(
                    f"{rel}:{lineno}: len(text/real_string/chrs/label/title) feeds "
                    "Plotchar metrics assignment or constructor"
                )

    if problems:
        raise AssertionError(
            "Forbidden runtime fallback implementation found in src/climara:\n"
            + "\n".join(problems)
        )


def assert_core_checks_pass() -> None:
    commands = (
        [sys.executable, "tools/check_no_matplotlib.py"],
        [sys.executable, "tools/check_no_external_render_deps.py"],
    )

    for command in commands:
        result = run(command)
        print(result.stdout.rstrip())


def main() -> None:
    assert_status_report_runs()
    assert_no_forbidden_runtime_fallbacks()
    assert_core_checks_pass()
    print("✅ Python mainline project boundary smoke passed")


if __name__ == "__main__":
    main()
