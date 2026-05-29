from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SOURCE_MAP = ROOT / "docs" / "ncl_plotchar_mapped_coordinate_branch_source_map.md"
LABEL_MAP = ROOT / "docs" / "ncl_plotchar_mapped_branch_labels.md"
LABEL_RESOLUTION = ROOT / "docs" / "ncl_plotchar_mapped_label_resolution.md"
OUT = ROOT / "docs" / "ncl_plotchar_mapped_branch_readiness.md"

REQUIRED_EVIDENCE = {
    "IMAP branch evidence": ["IMAP"],
    "coordinate input evidence": ["XPOS", "YPOS"],
    "internal position evidence": ["XCEN", "YCEN", "XRGT", "YRGT"],
    "extent evidence": ["DL", "DR", "DB", "DT"],
    "PCGETR-visible evidence": ["PCGETR", "XB", "XC", "XE", "YB", "YC", "YE"],
    "control-flow evidence": ["GO TO", "GOTO", "IF", "CALL"],
    "label evidence": ["label `", "Referenced labels"],
}


def read_doc(path: Path) -> str:
    if not path.exists():
        raise SystemExit(f"Missing required document: {path}")

    return path.read_text(encoding="utf-8")


def has_all_terms(text: str, terms: list[str]) -> bool:
    upper = text.upper()
    return all(term.upper() in upper for term in terms)


def has_any_terms(text: str, terms: list[str]) -> bool:
    upper = text.upper()
    return any(term.upper() in upper for term in terms)


def label_resolution_status() -> tuple[bool, str]:
    if not LABEL_RESOLUTION.exists():
        return False, "label resolution report is missing"

    text = LABEL_RESOLUTION.read_text(encoding="utf-8")

    if "Unresolved after robust parsing: none" in text:
        return True, "all previously missing labels resolved"

    for line in text.splitlines():
        if line.startswith("Unresolved after robust parsing:"):
            return False, line

    return False, "label resolution status could not be determined"


def evidence_report(combined: str) -> list[tuple[str, bool, str]]:
    rows = []

    for name, terms in REQUIRED_EVIDENCE.items():
        if name in {"PCGETR-visible evidence", "control-flow evidence", "label evidence"}:
            ok = has_any_terms(combined, terms)
        else:
            ok = has_all_terms(combined, terms)

        rows.append((name, ok, ", ".join(terms)))

    return rows


def readiness_decision(rows: list[tuple[str, bool, str]], label_ok: bool, label_note: str) -> tuple[bool, str]:
    missing = [name for name, ok, _ in rows if not ok]

    if missing:
        return False, "Not ready: required evidence is missing: " + ", ".join(missing)

    if not label_ok:
        return False, "Not ready: " + label_note

    return True, (
        "Potentially ready for manual mapped-coordinate implementation review. "
        "This is not an implementation claim; exact NCL branch mapping is still required before changing runtime behavior."
    )


def extract_key_lines(text: str, terms: list[str], limit: int = 120) -> list[str]:
    out = []
    upper_terms = [term.upper() for term in terms]

    for line in text.splitlines():
        upper = line.upper()
        if any(term in upper for term in upper_terms):
            out.append(line)

        if len(out) >= limit:
            break

    return out


def write_report() -> None:
    source_text = read_doc(SOURCE_MAP)
    label_text = read_doc(LABEL_MAP)
    resolution_text = read_doc(LABEL_RESOLUTION) if LABEL_RESOLUTION.exists() else ""

    combined = source_text + "\n\n" + label_text + "\n\n" + resolution_text

    rows = evidence_report(combined)
    label_ok, label_note = label_resolution_status()
    ready, decision = readiness_decision(rows, label_ok, label_note)

    OUT.parent.mkdir(parents=True, exist_ok=True)

    lines = []
    lines.append("# NCL Plotchar Mapped Branch Implementation Readiness")
    lines.append("")
    lines.append("## Decision")
    lines.append("")
    lines.append(decision)
    lines.append("")
    lines.append(f"- Ready flag: `{ready}`")
    lines.append("")
    lines.append("## Evidence checklist")
    lines.append("")

    for name, ok, terms in rows:
        mark = "PASS" if ok else "FAIL"
        lines.append(f"- `{mark}` {name}: {terms}")

    lines.append("")
    lines.append("## Label resolution")
    lines.append("")
    lines.append(f"- Status: {label_note}")
    lines.append("")
    lines.append("## Blocking uncertainty policy")
    lines.append("")
    lines.append(
        "This readiness gate intentionally does not treat every keyword-level "
        "`No relevant source window detected` line as a blocker. Those lines can appear "
        "inside unrelated keyword sections. Blocking is based on the evidence checklist "
        "and fixed-form label resolution."
    )
    lines.append("")
    lines.append("## Key source lines")
    lines.append("")
    lines.append("```text")
    key_lines = extract_key_lines(
        combined,
        [
            "IMAP",
            "MAP",
            "XPOS",
            "YPOS",
            "XCEN",
            "YCEN",
            "XRGT",
            "YRGT",
            "DL",
            "DR",
            "DB",
            "DT",
            "PCGETR",
            "GO TO",
            "GOTO",
            "CALL",
            "IF",
        ],
    )

    if key_lines:
        lines.extend(key_lines)
    else:
        lines.append("No key source lines extracted.")

    lines.append("```")
    lines.append("")
    lines.append("## Rule")
    lines.append("")
    lines.append(
        "A `True` readiness flag only allows manual implementation review. "
        "`IMAP != 0` must remain guarded until the exact NCL mapped-coordinate branch "
        "has been translated into Python state, metric, and PCGETR-visible behavior."
    )
    lines.append("")

    OUT.write_text("\n".join(lines), encoding="utf-8")

    print(f"wrote {OUT}")
    print("")
    print("Mapped branch readiness:")
    print(decision)
    print(f"Ready flag: {ready}")


def main() -> None:
    write_report()


if __name__ == "__main__":
    main()
