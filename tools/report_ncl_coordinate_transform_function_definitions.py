from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "ncl_coordinate_transform_function_definitions.md"

TARGETS = ("CFUX", "CFUY", "CUFX", "CUFY", "GETSET", "SET")
WINDOW_RADIUS = 28


@dataclass(frozen=True)
class DefinitionHit:
    name: str
    path: Path
    start_line: int
    end_line: int
    kind: str
    source: tuple[str, ...]


@dataclass(frozen=True)
class WindowHit:
    name: str
    path: Path
    center_line: int
    source: tuple[tuple[int, str], ...]


def ncl_root() -> Path:
    value = os.environ.get("NCL_SRC_ROOT")
    if not value:
        raise SystemExit("Set NCL_SRC_ROOT=/mnt/d/Projects/NCL before running.")

    root = Path(value)
    if not root.exists():
        raise SystemExit(f"NCL_SRC_ROOT does not exist: {root}")

    return root


def safe_read(path: Path) -> str:
    for encoding in ("utf-8", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue

    return ""


def candidate_files(root: Path) -> list[Path]:
    suffixes = {".f", ".F", ".f90", ".F90", ".c", ".h", ".txt"}
    out: list[Path] = []

    for path in root.rglob("*"):
        if not path.is_file() or path.suffix not in suffixes:
            continue

        lower = str(path).lower()
        name = path.name.lower()

        if (
            "gks" in lower
            or "plot" in lower
            or "gridal" in lower
            or "util" in lower
            or name.startswith(("cfu", "cuf", "set", "getset"))
            or name in {"plchhq.f", "c_plchhq.c"}
        ):
            out.append(path)

    return sorted(set(out))


def is_comment(line: str) -> bool:
    stripped = line.lstrip()

    if not line:
        return True

    if line[0] in {"c", "C", "*", "!"}:
        return True

    if stripped.startswith("!"):
        return True

    return False


def fixed_form_statement(line: str) -> str:
    if len(line) > 6:
        return line[6:].strip()
    return line.strip()


def normalized_statement(line: str) -> str:
    if is_comment(line):
        return ""
    return fixed_form_statement(line).upper()


def definition_start(line: str, target: str) -> str | None:
    stmt = normalized_statement(line)
    if not stmt:
        return None

    patterns = [
        (rf"\b(?:REAL|DOUBLE\s+PRECISION|INTEGER|LOGICAL|CHARACTER(?:\*\d+)?)\s+FUNCTION\s+{target}\b", "FUNCTION"),
        (rf"\bFUNCTION\s+{target}\b", "FUNCTION"),
        (rf"\bSUBROUTINE\s+{target}\b", "SUBROUTINE"),
        (rf"\b[A-Z_][A-Z0-9_*\s]*\s+{target}\s*\(", "C-LIKE"),
    ]

    for pattern, kind in patterns:
        if re.search(pattern, stmt):
            return kind

    return None


def next_definition_or_end(lines: list[str], start_index: int) -> int:
    for index in range(start_index + 1, len(lines)):
        stmt = normalized_statement(lines[index])

        if not stmt:
            continue

        if re.match(r"^END\b", stmt):
            return index + 1

        if re.search(r"\b(FUNCTION|SUBROUTINE)\b", stmt) and index > start_index:
            return index

    return min(len(lines), start_index + 220)


def find_definitions(path: Path, target: str) -> list[DefinitionHit]:
    text = safe_read(path)
    if not text:
        return []

    lines = text.splitlines()
    hits: list[DefinitionHit] = []

    for index, line in enumerate(lines):
        kind = definition_start(line, target)
        if not kind:
            continue

        end = next_definition_or_end(lines, index)
        source = tuple(lines[index:end])
        hits.append(
            DefinitionHit(
                name=target,
                path=path,
                start_line=index + 1,
                end_line=end,
                kind=kind,
                source=source,
            )
        )

        if len(hits) >= 4:
            break

    return hits


def keyword_windows(path: Path, target: str) -> list[WindowHit]:
    text = safe_read(path)
    if not text:
        return []

    lines = text.splitlines()
    hits: list[WindowHit] = []

    for index, line in enumerate(lines, start=1):
        upper = line.upper()
        if target not in upper:
            continue

        if target == "SET" and not any(
            token in upper
            for token in ("CALL SET", "SUBROUTINE SET", "FUNCTION SET", "GETSET", "VIEWPORT", "WINDOW")
        ):
            continue

        start = max(1, index - WINDOW_RADIUS)
        end = min(len(lines), index + WINDOW_RADIUS)

        hits.append(
            WindowHit(
                name=target,
                path=path,
                center_line=index,
                source=tuple((number, lines[number - 1].rstrip()) for number in range(start, end + 1)),
            )
        )

        if len(hits) >= 4:
            break

    return hits


def rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def write_report() -> None:
    root = ncl_root()
    files = candidate_files(root)

    definitions: dict[str, list[DefinitionHit]] = {target: [] for target in TARGETS}
    windows: dict[str, list[WindowHit]] = {target: [] for target in TARGETS}

    for target in TARGETS:
        for path in files:
            definitions[target].extend(find_definitions(path, target))
            if len(definitions[target]) >= 4:
                break

        for path in files:
            windows[target].extend(keyword_windows(path, target))
            if len(windows[target]) >= 8:
                break

    OUT.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    lines.append("# NCL Coordinate Transform Function Definitions")
    lines.append("")
    lines.append("This report is generated from the local NCL source tree.")
    lines.append("")
    lines.append(f"- `NCL_SRC_ROOT`: `{root}`")
    lines.append("")
    lines.append("## Current decision")
    lines.append("")
    lines.append(
        "This report does not implement coordinate transforms. It extracts function "
        "or subroutine definitions and fallback source windows for `CFUX`, `CFUY`, "
        "`CUFX`, `CUFY`, `GETSET`, and `SET`. A Python transform provider may only "
        "be implemented after these definitions and their coordinate-space meanings "
        "are manually mapped."
    )
    lines.append("")
    lines.append("## Definition availability")
    lines.append("")

    for target in TARGETS:
        status = "found" if definitions[target] else "not found"
        lines.append(f"- `{target}`: {status}")

    lines.append("")
    lines.append("## Function / subroutine definitions")
    lines.append("")

    for target in TARGETS:
        lines.append(f"### `{target}`")
        lines.append("")

        if not definitions[target]:
            lines.append("No direct function/subroutine definition detected by this extractor.")
            lines.append("")
        else:
            for idx, hit in enumerate(definitions[target], start=1):
                lines.append(
                    f"#### `{target}` definition {idx}: `{rel(hit.path, root)}` "
                    f"lines {hit.start_line}-{hit.end_line}, kind={hit.kind}"
                )
                lines.append("")
                lines.append("```fortran")
                for offset, source_line in enumerate(hit.source, start=hit.start_line):
                    lines.append(f"{offset:6d}: {source_line.rstrip()}")
                lines.append("```")
                lines.append("")

    lines.append("## Fallback keyword windows")
    lines.append("")

    for target in TARGETS:
        lines.append(f"### `{target}` windows")
        lines.append("")

        if not windows[target]:
            lines.append("No fallback keyword window detected.")
            lines.append("")
            continue

        for idx, hit in enumerate(windows[target][:8], start=1):
            lines.append(f"#### `{target}` window {idx}: `{rel(hit.path, root)}` line {hit.center_line}")
            lines.append("")
            lines.append("```fortran")
            for number, source_line in hit.source:
                marker = ">>" if number == hit.center_line else "  "
                lines.append(f"{marker} {number:6d}: {source_line}")
            lines.append("```")
            lines.append("")

    lines.append("## Manual mapping checklist")
    lines.append("")
    lines.append("- Determine exact direction of `CFUX` and `CFUY`.")
    lines.append("- Determine exact direction of `CUFX` and `CUFY`.")
    lines.append("- Determine what coordinate system `GETSET` returns.")
    lines.append("- Determine how `SET` mutates viewport/window state.")
    lines.append("- Determine whether Plotchar `IMAP != 0` uses these transforms before placement, after placement, or only for exposed PCGETR geometry.")
    lines.append("- Implement Python provider only after the above items are clear.")
    lines.append("")
    lines.append("## Guard rule")
    lines.append("")
    lines.append(
        "`NclMappedCoordinateTransformProvider` must remain guarded until the above "
        "definitions are manually mapped into a Python provider."
    )
    lines.append("")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT}")

    for target in TARGETS:
        print(f"{target}: definitions={len(definitions[target])}, windows={len(windows[target])}")


def main() -> None:
    write_report()


if __name__ == "__main__":
    main()
