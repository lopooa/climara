from __future__ import annotations

import os
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LABEL_DOC = ROOT / "docs" / "ncl_plotchar_mapped_branch_labels.md"
OUT = ROOT / "docs" / "ncl_plotchar_mapped_label_resolution.md"


def ncl_root() -> Path:
    value = os.environ.get("NCL_SRC_ROOT")
    if not value:
        raise SystemExit("Set NCL_SRC_ROOT=/mnt/d/Projects/NCL before running this report.")

    root = Path(value)
    if not root.exists():
        raise SystemExit(f"NCL_SRC_ROOT does not exist: {root}")

    return root


def find_plchhq(root: Path) -> Path:
    hits = sorted(path for path in root.rglob("plchhq.f") if path.is_file())

    if not hits:
        raise SystemExit(f"Could not find plchhq.f under {root}")

    for path in hits:
        lower = str(path).lower()
        if "plotchar" in lower or "plot" in lower:
            return path

    return hits[0]


def safe_read(path: Path) -> str:
    for encoding in ("utf-8", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue

    raise SystemExit(f"Could not decode {path}")


def is_comment(line: str) -> bool:
    if not line:
        return True
    return line[0] in {"c", "C", "*", "!"}


def extract_fixed_form_labels(lines: list[str]) -> dict[str, list[tuple[int, str]]]:
    labels: dict[str, list[tuple[int, str]]] = {}

    for line_number, line in enumerate(lines, start=1):
        if is_comment(line):
            continue

        # Fixed-form Fortran statement label lives in columns 1-5.
        field = line[:5]
        stripped = field.strip()

        if stripped and stripped.isdigit():
            labels.setdefault(stripped, []).append((line_number, line.rstrip()))

    return labels


def labels_from_goto(line: str) -> set[str]:
    refs: set[str] = set()
    upper = line.upper()

    # Assigned/computed goto: GO TO (10,20,30), I
    for match in re.finditer(r"\bGO\s*TO\s*\(([^)]*)\)", upper):
        inside = match.group(1)
        for label in re.findall(r"\b\d{1,5}\b", inside):
            refs.add(label)

    # Simple goto: GO TO 120 or GOTO 120
    for match in re.finditer(r"\b(?:GO\s*TO|GOTO)\s+(\d{1,5})\b", upper):
        refs.add(match.group(1))

    return refs


def labels_from_arithmetic_if(line: str) -> set[str]:
    refs: set[str] = set()
    stripped = line.strip()
    upper = stripped.upper()

    if not upper.startswith("IF"):
        return refs

    # Only arithmetic IF has the form:
    # IF (expr) label_negative, label_zero, label_positive
    # Logical IF (...) GO TO n is already handled by labels_from_goto.
    if "GO TO" in upper or "GOTO" in upper or "THEN" in upper:
        return refs

    close = upper.find(")")
    if close < 0:
        return refs

    rest = upper[close + 1:].strip()

    if re.fullmatch(r"\d{1,5}\s*,\s*\d{1,5}\s*,\s*\d{1,5}", rest):
        refs.update(re.findall(r"\b\d{1,5}\b", rest))

    return refs


def referenced_labels_from_source(lines: list[str]) -> list[str]:
    refs: set[str] = set()

    for line in lines:
        if is_comment(line):
            continue

        refs.update(labels_from_goto(line))
        refs.update(labels_from_arithmetic_if(line))

    return sorted(refs, key=lambda value: int(value))


def unresolved_from_previous_report() -> list[str]:
    if not LABEL_DOC.exists():
        return []

    text = LABEL_DOC.read_text(encoding="utf-8")
    return sorted(
        set(re.findall(r"- `(\d{1,5})` -> label definition not detected", text)),
        key=lambda value: int(value),
    )


def write_report() -> None:
    root = ncl_root()
    plchhq = find_plchhq(root)
    text = safe_read(plchhq)
    lines = text.splitlines()

    labels = extract_fixed_form_labels(lines)
    old_unresolved = unresolved_from_previous_report()
    source_refs = referenced_labels_from_source(lines)

    # Earlier heuristic report may contain constants from IF expressions.
    # Only labels that are true GO TO / arithmetic-IF references matter here.
    actionable_old_unresolved = [
        label for label in old_unresolved
        if label in source_refs
    ]

    still_unresolved = [
        label for label in actionable_old_unresolved
        if label not in labels
    ]
    resolved = [
        label for label in actionable_old_unresolved
        if label in labels
    ]

    ignored_constants = [
        label for label in old_unresolved
        if label not in source_refs
    ]

    OUT.parent.mkdir(parents=True, exist_ok=True)

    out: list[str] = []
    out.append("# NCL Plotchar Mapped Branch Label Resolution")
    out.append("")
    out.append(f"- `NCL_SRC_ROOT`: `{root}`")
    out.append(f"- `plchhq.f`: `{plchhq}`")
    out.append("")
    out.append("## Resolution decision")
    out.append("")

    if still_unresolved:
        out.append("Unresolved after robust parsing: " + ", ".join(still_unresolved))
    else:
        out.append("Unresolved after robust parsing: none")

    out.append("")
    out.append("## Labels previously reported as missing")
    out.append("")

    if old_unresolved:
        for label in old_unresolved:
            if label in ignored_constants:
                status = "ignored as non-label numeric constant"
            elif label in labels:
                status = "resolved"
            else:
                status = "still unresolved"
            out.append(f"- `{label}`: {status}")
    else:
        out.append("No previously unresolved labels were found in the earlier label report.")

    out.append("")
    out.append("## Ignored non-label numeric constants from earlier heuristic report")
    out.append("")

    if ignored_constants:
        out.append("`" + " ".join(ignored_constants) + "`")
    else:
        out.append("None.")

    out.append("")
    out.append("## Resolved label definitions")
    out.append("")

    if resolved:
        for label in resolved:
            for line_number, source in labels[label]:
                out.append(f"- `{label}` line {line_number}: `{source.strip()}`")
    else:
        out.append("No resolved labels to report.")

    out.append("")
    out.append("## Still unresolved true label references")
    out.append("")

    if still_unresolved:
        for label in still_unresolved:
            out.append(f"- `{label}`")
    else:
        out.append("None.")

    out.append("")
    out.append("## True referenced labels from GO TO / arithmetic IF")
    out.append("")

    if source_refs:
        for label in source_refs[:300]:
            if label in labels:
                locs = ", ".join(f"line {line_number}" for line_number, _ in labels[label][:3])
                out.append(f"- `{label}` -> {locs}")
            else:
                out.append(f"- `{label}` -> not found by robust parser")
    else:
        out.append("No true label references detected.")

    out.append("")
    out.append("## Rule")
    out.append("")
    out.append(
        "Only labels referenced by GO TO/GOTO/computed GO TO or arithmetic IF are "
        "blocking for mapped-coordinate readiness. Numeric constants inside ordinary "
        "IF expressions are not labels and must not block implementation review."
    )
    out.append("")

    OUT.write_text("\n".join(out), encoding="utf-8")

    print(f"wrote {OUT}")
    print("")
    if still_unresolved:
        print("Label resolution: unresolved true labels remain")
        print("Unresolved:", ", ".join(still_unresolved))
    else:
        print("Label resolution: all true label references resolved")


def main() -> None:
    write_report()


if __name__ == "__main__":
    main()
