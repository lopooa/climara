from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFS_DOC = ROOT / "docs" / "ncl_coordinate_transform_function_definitions.md"
SOURCE_DOC = ROOT / "docs" / "ncl_plotchar_coordinate_transform_source_map.md"
OUT = ROOT / "docs" / "ncl_coordinate_transform_direction_readiness.md"

REQUIRED_TARGETS = ("CFUX", "CFUY", "CUFX", "CUFY", "GETSET")
OPTIONAL_TARGETS = ("SET",)

DIRECTION_HINTS = {
    "CFUX": ("user-to-fractional-or-plotter-x", "requires source confirmation"),
    "CFUY": ("user-to-fractional-or-plotter-y", "requires source confirmation"),
    "CUFX": ("fractional-or-plotter-to-user-x", "requires source confirmation"),
    "CUFY": ("fractional-or-plotter-to-user-y", "requires source confirmation"),
    "GETSET": ("viewport-window-state-read", "requires source confirmation"),
    "SET": ("viewport-window-state-write", "requires source confirmation"),
}


def read_doc(path: Path) -> str:
    if not path.exists():
        raise SystemExit(f"Missing required document: {path}")
    return path.read_text(encoding="utf-8")


def target_section(text: str, target: str) -> str:
    pattern = re.compile(
        rf"^### `{re.escape(target)}`\n\n(.*?)(?=^### `[^`]+`\n\n|^## |\Z)",
        flags=re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(text)
    return match.group(1) if match else ""


def target_window_section(text: str, target: str) -> str:
    pattern = re.compile(
        rf"^### `{re.escape(target)}` windows\n\n(.*?)(?=^### `[^`]+` windows\n\n|^## |\Z)",
        flags=re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(text)
    return match.group(1) if match else ""


def has_definition(section: str) -> bool:
    if not section:
        return False
    if "No direct function/subroutine definition detected" in section:
        return False
    return "definition" in section.lower() and "```fortran" in section


def has_window(section: str) -> bool:
    if not section:
        return False
    if "No fallback keyword window detected" in section:
        return False
    return "```fortran" in section


def target_evidence(text: str, target: str) -> tuple[bool, bool, str]:
    definition = target_section(text, target)
    window = target_window_section(text, target)

    definition_ok = has_definition(definition)
    window_ok = has_window(window)

    if definition_ok:
        status = "definition-found"
    elif window_ok:
        status = "fallback-window-found"
    else:
        status = "missing"

    return definition_ok, window_ok, status


def extract_compact_lines(text: str, target: str, limit: int = 24) -> list[str]:
    lines = []
    upper_target = target.upper()

    for line in text.splitlines():
        upper = line.upper()
        if upper_target in upper:
            lines.append(line)
        if len(lines) >= limit:
            break

    return lines


def readiness_decision(evidence: dict[str, tuple[bool, bool, str]]) -> tuple[bool, str]:
    missing_required = [
        target
        for target in REQUIRED_TARGETS
        if evidence[target][2] == "missing"
    ]

    if missing_required:
        return (
            False,
            "Not ready: missing required coordinate-transform evidence for "
            + ", ".join(missing_required),
        )

    weak_required = [
        target
        for target in REQUIRED_TARGETS
        if evidence[target][2] == "fallback-window-found"
    ]

    if weak_required:
        return (
            False,
            "Not ready for implementation, but ready for manual source inspection: "
            "only fallback windows were found for "
            + ", ".join(weak_required),
        )

    return (
        True,
        "Potentially ready for manual implementation planning: required transform definitions were detected. "
        "Direction semantics still require manual source reading before Python provider implementation.",
    )


def write_report() -> None:
    defs_text = read_doc(DEFS_DOC)
    source_text = read_doc(SOURCE_DOC) if SOURCE_DOC.exists() else ""
    combined = defs_text + "\n\n" + source_text

    targets = REQUIRED_TARGETS + OPTIONAL_TARGETS
    evidence = {target: target_evidence(defs_text, target) for target in targets}

    ready, decision = readiness_decision(evidence)

    OUT.parent.mkdir(parents=True, exist_ok=True)

    lines = []
    lines.append("# NCL Coordinate Transform Direction Readiness")
    lines.append("")
    lines.append("This report checks whether coordinate-transform source evidence is sufficient to begin implementing a Python NCL transform provider.")
    lines.append("")
    lines.append("## Decision")
    lines.append("")
    lines.append(decision)
    lines.append("")
    lines.append(f"- Ready flag: `{ready}`")
    lines.append("")
    lines.append("## Evidence matrix")
    lines.append("")

    for target in targets:
        definition_ok, window_ok, status = evidence[target]
        direction_hint, note = DIRECTION_HINTS[target]
        lines.append(f"### `{target}`")
        lines.append("")
        lines.append(f"- Status: `{status}`")
        lines.append(f"- Definition found: `{definition_ok}`")
        lines.append(f"- Fallback window found: `{window_ok}`")
        lines.append(f"- Direction hint: `{direction_hint}`")
        lines.append(f"- Note: {note}")
        lines.append("")
        lines.append("Compact source lines:")
        lines.append("")
        lines.append("```text")
        compact = extract_compact_lines(combined, target)
        if compact:
            lines.extend(compact)
        else:
            lines.append("No compact source lines found.")
        lines.append("```")
        lines.append("")

    lines.append("## Direction mapping checklist")
    lines.append("")
    lines.append("- Confirm whether `CFUX` maps user X to fractional/NDC X or the reverse.")
    lines.append("- Confirm whether `CFUY` maps user Y to fractional/NDC Y or the reverse.")
    lines.append("- Confirm whether `CUFX` maps fractional/NDC X to user X or the reverse.")
    lines.append("- Confirm whether `CUFY` maps fractional/NDC Y to user Y or the reverse.")
    lines.append("- Confirm `GETSET` return order and coordinate-space meaning.")
    lines.append("- Confirm whether Plotchar `IMAP != 0` uses transform functions for origin only, extents only, or both.")
    lines.append("- Confirm whether `DSTL/DSTR/DSTB/DSTT` are transformed as offsets or recomputed from transformed corners.")
    lines.append("")
    lines.append("## Guard rule")
    lines.append("")
    lines.append(
        "A `True` readiness flag does not mean the transform provider is implemented. "
        "`NclMappedCoordinateTransformProvider` must remain guarded until the direction checklist is manually mapped and positive smokes are written."
    )
    lines.append("")

    OUT.write_text("\n".join(lines), encoding="utf-8")

    print(f"wrote {OUT}")
    print("")
    print("Coordinate transform direction readiness:")
    print(decision)
    print(f"Ready flag: {ready}")

    for target in targets:
        print(f"{target}: {evidence[target][2]}")


def main() -> None:
    write_report()


if __name__ == "__main__":
    main()
