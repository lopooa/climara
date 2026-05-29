
from __future__ import annotations

import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "ncl_plotchar_pwritx_nonfontcap_exact_branch_packet.md"

TERMS = [
    "PWRITX", "PWRITY", "PWRIT", "PCHIQU", "PLCHHQ",
    "FONT", "IFNT", "NFNT", "NODF", "QU", "IQUF",
    "QUALITY", "MEDIUM", "LOW", "WORKSTATION", "FONTCAP",
    "PCGET", "PCSET", "DSTL", "DSTR", "DSTB", "DSTT",
    "DL", "DR", "DB", "DT",
]

RADIUS = 34


def ncl_root() -> Path:
    value = os.environ.get("NCL_SRC_ROOT")
    if not value:
        raise SystemExit("Set NCL_SRC_ROOT=/mnt/d/Projects/NCL before running.")
    root = Path(value)
    if not root.exists():
        raise SystemExit(f"NCL_SRC_ROOT does not exist: {root}")
    return root


def safe_read(path: Path) -> str:
    for enc in ("utf-8", "latin-1"):
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError:
            pass
    return ""


def rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def candidate_files(root: Path) -> list[Path]:
    suffixes = {".f", ".F", ".f90", ".F90", ".c", ".h", ".txt"}
    out = []
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix not in suffixes:
            continue
        lower = str(path).lower()
        name = path.name.lower()
        if (
            "plotchar" in lower
            or "font" in lower
            or "pwr" in lower
            or name.startswith(("plch", "pchi", "pwri", "pwr", "pcget", "pcset"))
            or name == "c_plchhq.c"
        ):
            out.append(path)
    return sorted(set(out))


def windows_for(path: Path, term: str) -> list[tuple[int, list[tuple[int, str]]]]:
    text = safe_read(path)
    if not text:
        return []
    lines = text.splitlines()
    hits = []
    for i, line in enumerate(lines, start=1):
        if term not in line.upper():
            continue
        start = max(1, i - RADIUS)
        end = min(len(lines), i + RADIUS)
        hits.append((i, [(n, lines[n - 1].rstrip()) for n in range(start, end + 1)]))
        if len(hits) >= 3:
            break
    return hits


def direct_defs(path: Path) -> list[tuple[str, int, int, list[str]]]:
    text = safe_read(path)
    if not text:
        return []
    lines = text.splitlines()
    names = ("PWRITX", "PWRITY", "PCHIQU", "PLCHHQ")
    hits = []
    for i, line in enumerate(lines):
        stmt = line[6:].strip().upper() if len(line) > 6 else line.strip().upper()
        for name in names:
            if (f"SUBROUTINE {name}" in stmt) or (f"FUNCTION {name}" in stmt):
                end = min(len(lines), i + 260)
                for j in range(i + 1, len(lines)):
                    s = lines[j][6:].strip().upper() if len(lines[j]) > 6 else lines[j].strip().upper()
                    if s.startswith("END"):
                        end = j + 1
                        break
                hits.append((name, i + 1, end, lines[i:end]))
                if len(hits) >= 6:
                    return hits
    return hits


def readiness(parts: list[str]) -> tuple[bool, str]:
    text = "\n".join(parts).upper()
    checks = {
        "PWRITX/PWRITY": ("PWRITX" in text or "PWRITY" in text),
        "font state": any(t in text for t in ("IFNT", "NFNT", "NODF", "FONT")),
        "quality state": any(t in text for t in ("IQUF", "QUALITY", "MEDIUM", "LOW", "WORKSTATION", "QU")),
        "extent state": any(t in text for t in ("DSTL", "DSTR", "DSTB", "DSTT", "DL", "DR", "DB", "DT")),
    }
    missing = [k for k, v in checks.items() if not v]
    if missing:
        return False, "Not ready for implementation planning: missing " + ", ".join(missing)
    return True, "Potentially ready for manual PWRITX/font0/non-fontcap implementation planning. This is not a runtime implementation claim."


def main() -> None:
    root = ncl_root()
    files = candidate_files(root)
    parts = []

    defs = []
    for path in files:
        hits = direct_defs(path)
        for item in hits:
            defs.append((path, *item))
            parts.append("\n".join(item[3]))
        if len(defs) >= 8:
            break

    term_hits = {}
    for term in TERMS:
        term_hits[term] = []
        for path in files:
            hits = windows_for(path, term)
            for center, win in hits[:2]:
                term_hits[term].append((path, center, win))
                parts.append("\n".join(src for _, src in win))
            if len(term_hits[term]) >= 4:
                break

    ready, decision = readiness(parts)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    lines.append("# NCL Plotchar PWRITX / Font0 / Non-Fontcap Exact Branch Packet")
    lines.append("")
    lines.append(f"- `NCL_SRC_ROOT`: `{root}`")
    lines.append("")
    lines.append("## Decision")
    lines.append("")
    lines.append(decision)
    lines.append("")
    lines.append(f"- Exact branch packet ready: `{ready}`")
    lines.append("")
    lines.append("## Current Python boundary")
    lines.append("")
    lines.append("The current Python Plotchar engine implements the audited high-quality fontcap subset. PWRITX, font0, and non-fontcap paths remain guarded.")
    lines.append("")
    lines.append("## Definition blocks")
    lines.append("")

    if not defs:
        lines.append("No direct definition blocks found by this extractor.")
        lines.append("")
    else:
        for idx, (path, name, start, end, src) in enumerate(defs, start=1):
            lines.append(f"### Definition {idx}: `{name}` in `{rel(path, root)}` lines {start}-{end}")
            lines.append("")
            lines.append("```fortran")
            for n, source in enumerate(src, start=start):
                lines.append(f"{n:6d}: {source.rstrip()}")
            lines.append("```")
            lines.append("")

    lines.append("## Focus windows")
    lines.append("")
    for term in TERMS:
        lines.append(f"### `{term}`")
        lines.append("")
        hits = term_hits.get(term, [])
        if not hits:
            lines.append("No source window detected.")
            lines.append("")
            continue
        for idx, (path, center, win) in enumerate(hits[:4], start=1):
            lines.append(f"#### `{term}` window {idx}: `{rel(path, root)}` line {center}")
            lines.append("")
            lines.append("```fortran")
            for n, source in win:
                marker = ">>" if n == center else "  "
                lines.append(f"{marker} {n:6d}: {source}")
            lines.append("```")
            lines.append("")

    lines.append("## Manual implementation checklist")
    lines.append("")
    lines.append("- Identify exact branch condition selecting PWRITX/font0/non-fontcap instead of fontcap.")
    lines.append("- Identify quality-resource values entering medium, low, workstation, and PWRITX paths.")
    lines.append("- Identify how PWRITX returns or mutates text extents.")
    lines.append("- Identify how PWRITX relates to `DL/DR/DB/DT` and `DSTL/DSTR/DSTB/DSTT`.")
    lines.append("- Identify font database dependencies for font0 and any non-fontcap path.")
    lines.append("- Preserve current fontcap subset exactly.")
    lines.append("- Keep this branch guarded until positive source-mapped smokes exist.")
    lines.append("")
    lines.append("## Guard rule")
    lines.append("")
    lines.append("This packet does not implement PWRITX/font0/non-fontcap behavior. It only defines the source boundary for a future runtime stage.")
    lines.append("")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT}")
    print("")
    print("PWRITX/font0/non-fontcap exact branch packet:")
    print(decision)
    print(f"Exact branch packet ready: {ready}")


if __name__ == "__main__":
    main()
