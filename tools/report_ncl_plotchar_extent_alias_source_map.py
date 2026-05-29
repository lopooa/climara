from __future__ import annotations

import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "ncl_plotchar_extent_alias_source_map.md"

KEYWORDS = [
    "DSTL",
    "DSTR",
    "DSTB",
    "DSTT",
    "DL",
    "DR",
    "DB",
    "DT",
    "PCGETR",
    "PCSETR",
    "XB",
    "XC",
    "XE",
    "YB",
    "YC",
    "YE",
]

WINDOW_RADIUS = 24


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


def source_files(root: Path) -> list[Path]:
    suffixes = {".f", ".F", ".c", ".h"}

    out = []
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix not in suffixes:
            continue

        name = path.name.lower()
        lower = str(path).lower()

        if (
            name in {"plchhq.f", "pcgetr.f", "c_pcgetr.c"}
            or "plotchar" in lower
            or name.startswith("pcget")
            or name.startswith("pcset")
        ):
            out.append(path)

    return sorted(set(out))


def relevant(keyword: str, line: str) -> bool:
    upper = line.upper()
    key = keyword.upper()

    if key not in upper:
        return False

    if key in {"DL", "DR", "DB", "DT", "XB", "XC", "XE", "YB", "YC", "YE"}:
        return any(
            token in upper
            for token in (
                "PCGETR",
                "PCSETR",
                "DST",
                "GET",
                "SET",
                "XBEG",
                "XCEN",
                "XEND",
                "YBEG",
                "YCEN",
                "YEND",
            )
        )

    return True


def windows(path: Path, keyword: str) -> list[tuple[int, list[tuple[int, str]]]]:
    text = safe_read(path)
    if not text:
        return []

    lines = text.splitlines()
    hits = []

    for index, line in enumerate(lines, start=1):
        if not relevant(keyword, line):
            continue

        start = max(1, index - WINDOW_RADIUS)
        end = min(len(lines), index + WINDOW_RADIUS)
        hits.append(
            (
                index,
                [(number, lines[number - 1].rstrip()) for number in range(start, end + 1)],
            )
        )

        if len(hits) >= 6:
            break

    return hits


def write_report() -> None:
    root = ncl_root()
    files = source_files(root)

    OUT.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    lines.append("# NCL Plotchar Extent Alias Source Map")
    lines.append("")
    lines.append(f"- `NCL_SRC_ROOT`: `{root}`")
    lines.append("")
    lines.append("## Purpose")
    lines.append("")
    lines.append(
        "This report connects internal PLCHHQ extent variables with PCGETR-visible "
        "extent resources. Python implementation should not require literal `DL/DR/DB/DT` "
        "inside `plchhq.f` if the source uses `DSTL/DSTR/DSTB/DSTT` internally."
    )
    lines.append("")
    lines.append("## Expected alias relationship")
    lines.append("")
    lines.append("- `DL` corresponds to left extent, commonly represented internally as `DSTL`.")
    lines.append("- `DR` corresponds to right extent, commonly represented internally as `DSTR`.")
    lines.append("- `DB` corresponds to bottom extent, commonly represented internally as `DSTB`.")
    lines.append("- `DT` corresponds to top extent, commonly represented internally as `DSTT`.")
    lines.append("- `XB/XC/XE/YB/YC/YE` correspond to PCGETR-visible geometry state.")
    lines.append("")
    lines.append("## Keyword source windows")
    lines.append("")

    for keyword in KEYWORDS:
        lines.append(f"### `{keyword}`")
        lines.append("")

        count = 0
        for path in files:
            hits = windows(path, keyword)
            if not hits:
                continue

            try:
                rel = path.relative_to(root)
            except ValueError:
                rel = path

            for center, win in hits[:3]:
                count += 1
                lines.append(f"#### `{keyword}` hit {count}: `{rel}` line {center}")
                lines.append("")
                lines.append("```fortran")
                for number, source in win:
                    marker = ">>" if number == center else "  "
                    lines.append(f"{marker} {number:6d}: {source}")
                lines.append("```")
                lines.append("")

                if count >= 8:
                    break

            if count >= 8:
                break

        if count == 0:
            lines.append("No relevant source window detected.")
            lines.append("")

    lines.append("## Readiness implication")
    lines.append("")
    lines.append(
        "Mapped-coordinate readiness may count extent evidence as present when "
        "`DSTL/DSTR/DSTB/DSTT` are found together with PCGETR or geometry-state evidence. "
        "This is still not an implementation claim."
    )
    lines.append("")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT}")


def main() -> None:
    write_report()


if __name__ == "__main__":
    main()
