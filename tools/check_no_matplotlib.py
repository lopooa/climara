from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "climara"

FORBIDDEN_MODULES = {
    "matplotlib",
    "matplotlib.pyplot",
    "pyplot",
}

FORBIDDEN_TEXT = (
    "matplotlib",
    "matplotlib.pyplot",
    "pyplot",
)


def is_forbidden_module(name: str) -> bool:
    lowered = name.lower()
    return any(
        lowered == forbidden or lowered.startswith(forbidden + ".")
        for forbidden in FORBIDDEN_MODULES
    )


def check_ast_imports(path: Path, text: str) -> list[str]:
    problems: list[str] = []

    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        return [f"{path}: syntax error while checking imports: {exc}"]

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if is_forbidden_module(alias.name):
                    problems.append(
                        f"{path}:{node.lineno}: forbidden import `{alias.name}`"
                    )

        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if is_forbidden_module(module):
                problems.append(
                    f"{path}:{node.lineno}: forbidden import from `{module}`"
                )

    return problems


def check_explicit_text(path: Path, text: str) -> list[str]:
    problems: list[str] = []

    for lineno, line in enumerate(text.splitlines(), start=1):
        lowered = line.lower()

        for token in FORBIDDEN_TEXT:
            if token in lowered:
                problems.append(
                    f"{path}:{lineno}: contains forbidden explicit token `{token}`: {line.rstrip()}"
                )

    return problems


def main() -> None:
    problems: list[str] = []

    for path in sorted(SRC.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue

        text = path.read_text(encoding="utf-8")
        problems.extend(check_ast_imports(path, text))
        problems.extend(check_explicit_text(path, text))

    if problems:
        print("Matplotlib-related code found:")
        print()
        for problem in problems:
            print(problem)
        raise SystemExit(1)

    print("OK: no Matplotlib-related code found in src/climara")


if __name__ == "__main__":
    main()
