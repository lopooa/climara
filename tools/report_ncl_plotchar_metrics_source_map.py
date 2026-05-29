from __future__ import annotations

import argparse
import os
from pathlib import Path

from climara.graphics._plotchar_source_requirements import (
    NCL_PLOTCHAR_METRICS_SOURCE_REQUIREMENTS,
    plotchar_source_requirements_report,
    required_plotchar_source_files,
)


KEY_PATTERNS = (
    "FigureAndSetTextBBInfo",
    "c_plchhq(0.5,0.5",
    'c_pcgetr("DL"',
    'c_pcgetr("DR"',
    'c_pcgetr("DT"',
    'c_pcgetr("DB"',
    "SUBROUTINE PLCHHQ",
    "SUBROUTINE PCGETR",
    "SUBROUTINE PCSETR",
    "SUBROUTINE PCRSET",
    "void c_plchhq",
    "void c_pcgetr",
    'ITEF is the "compute-text-extent-vectors" flag',
    "DSTL",
    "DSTR",
    "DSTB",
    "DSTT",
    "XBEG",
    "XEND",
    "YBEG",
    "YEND",
    "CNTR",
    "real_ph_width",
    "real_ph_height",
    "real_size",
    "void c_pcsetc",
    "void c_pcsetr",
    "void c_pcseti",
    "SUBROUTINE PCSETC",
    "SUBROUTINE PCSETI",
    "c_pcsetc(",
    "c_pcsetr(",
    "c_pcseti(",
    "SIZE",
    "SIZM",
    "ANGD.EQ.360",
    'c_pcgetr ("DL - DISTANCE LEFT  ",',
    'c_pcgetr ("DR - DISTANCE RIGHT ",',
    'c_pcgetr ("DB - DISTANCE BOTTOM",',
    'c_pcgetr ("DT - DISTANCE TOP   ",',
)


def candidate_roots() -> tuple[Path, ...]:
    roots = []

    env_root = os.environ.get("NCL_SRC_ROOT")
    if env_root:
        roots.append(Path(env_root))

    cwd = Path.cwd()
    roots.extend(
        [
            cwd / "external" / "ncl",
            cwd / "vendor" / "ncl",
            cwd / "ncl",
            cwd.parent / "ncl",
            cwd.parent / "NCL",
        ]
    )

    out = []
    seen = set()

    for root in roots:
        root = root.expanduser()
        key = str(root)
        if key in seen:
            continue
        seen.add(key)
        out.append(root)

    return tuple(out)


def find_source_root() -> Path | None:
    for root in candidate_roots():
        if all((root / rel).exists() for rel in required_plotchar_source_files()):
            return root
    return None


def matching_lines(path: Path, patterns: tuple[str, ...]) -> tuple[tuple[int, str], ...]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    hits = []
    lowered_patterns = tuple(pattern.lower() for pattern in patterns)

    for lineno, line in enumerate(text.splitlines(), start=1):
        lowered = line.lower()
        if any(pattern in lowered for pattern in lowered_patterns):
            hits.append((lineno, line.rstrip()))

    return tuple(hits)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--allow-missing", action="store_true")
    parser.add_argument("--max-lines-per-file", type=int, default=80)
    args = parser.parse_args()

    print(plotchar_source_requirements_report())
    print()
    print("Local NCL source availability")
    print("=" * 29)
    print()

    print("Candidate roots:")
    for root in candidate_roots():
        print(f"- {root}")

    print()
    root = find_source_root()

    if root is None:
        print("BLOCKED: complete NCL Plotchar source set was not found.")
        print("Set NCL_SRC_ROOT to the root of a full NCL source checkout.")
        print("Example:")
        print("  export NCL_SRC_ROOT=/mnt/d/Projects/NCL")
        if args.allow_missing:
            return
        raise SystemExit(2)

    print(f"Using NCL source root: {root}")
    print()

    missing_symbols = []
    for req in NCL_PLOTCHAR_METRICS_SOURCE_REQUIREMENTS:
        path = root / req.source_file
        if not path.exists():
            missing_symbols.append((req.source_file, req.symbol, "missing file"))
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if req.symbol not in text:
            missing_symbols.append((req.source_file, req.symbol, "missing symbol"))

    if missing_symbols:
        print("BLOCKED: required Plotchar symbols were not found.")
        for source_file, symbol, reason in missing_symbols:
            print(f"- {source_file}: {symbol} ({reason})")
        if args.allow_missing:
            return
        raise SystemExit(3)

    print("READY: required Plotchar source files and symbols are available.")
    print()
    print("Key source excerpts")
    print("=" * 19)

    for rel in required_plotchar_source_files():
        path = root / rel
        print()
        print(f"--- {rel} ---")
        hits = matching_lines(path, KEY_PATTERNS)
        if not hits:
            print("(no key lines matched)")
            continue
        for lineno, text in hits[: args.max_lines_per_file]:
            print(f"{lineno}: {text}")
        if len(hits) > args.max_lines_per_file:
            print(f"... {len(hits) - args.max_lines_per_file} more matched lines omitted")

    print()
    print("Next implementation boundary")
    print("=" * 28)
    print("A live Plotchar metrics provider must map:")
    print("- TextItem.c DoPcCalc Plotchar state setup")
    print("- TextItem.c c_plchhq(0.5, 0.5, real_string, real_size, 360.0, -1.0)")
    print("- PCGETR DL / DR / DB / DT retrieval")
    print("- TextItem.c post-metric justification and rotation")
    print("- unsupported function-code / Down-text cases must stay guarded")


if __name__ == "__main__":
    main()
