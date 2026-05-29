from __future__ import annotations

import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "ncl_plotchar_mapped_coordinate_branch_source_map.md"

KEYWORDS = [
    "IMAP",
    "MAP",
    "MAPPED",
    "COORD",
    "COORDINATE",
    "XPOS",
    "YPOS",
    "XCRA",
    "YCRA",
    "XCEN",
    "YCEN",
    "XRGT",
    "YRGT",
    "XBEG",
    "YBEG",
    "XEND",
    "YEND",
    "PCSETI",
    "PCSETR",
    "PCGETR",
    "DL",
    "DR",
    "DB",
    "DT",
]

WINDOW_RADIUS = 24


def ncl_root() -> Path:
    value = os.environ.get("NCL_SRC_ROOT")
    if not value:
        raise SystemExit("Set NCL_SRC_ROOT=/mnt/d/Projects/NCL before running this report.")

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
    suffixes = {".f", ".F", ".f90", ".F90", ".c", ".h", ".ncl", ".txt"}
    out = []

    for path in root.rglob("*"):
        if not path.is_file() or path.suffix not in suffixes:
            continue

        lower = str(path).lower()
        name = path.name.lower()

        if (
            "plotchar" in lower
            or name in {"plchhq.f", "c_plchhq.c"}
            or name.startswith("pc")
        ):
            out.append(path)

    return sorted(set(out))


def windows(path: Path, keyword: str) -> list[tuple[int, list[tuple[int, str]]]]:
    text = safe_read(path)
    if not text:
        return []

    lines = text.splitlines()
    hits = []
    needle = keyword.upper()

    for idx, line in enumerate(lines, start=1):
        upper = line.upper()
        if needle not in upper:
            continue

        if keyword in {"MAP", "DL", "DR", "DB", "DT"}:
            if not any(token in upper for token in ("IMAP", "COORD", "PCGET", "PCSET", "PLCHHQ", "XPOS", "YPOS", "XCEN", "YCEN")):
                continue

        start = max(1, idx - WINDOW_RADIUS)
        end = min(len(lines), idx + WINDOW_RADIUS)
        hits.append((idx, [(n, lines[n - 1].rstrip()) for n in range(start, end + 1)]))

        if len(hits) >= 6:
            break

    return hits


def write_report() -> None:
    root = ncl_root()
    files = source_files(root)
    OUT.parent.mkdir(parents=True, exist_ok=True)

    lines = []
    lines.append("# NCL Plotchar Mapped-Coordinate Branch Source Map")
    lines.append("")
    lines.append(f"- `NCL_SRC_ROOT`: `{root}`")
    lines.append("")
    lines.append("## Current decision")
    lines.append("")
    lines.append(
        "`IMAP != 0` / mapped-coordinate Plotchar behavior remains guarded. "
        "The current Python mainline only supports TextItem measurement with `IMAP == 0`."
    )
    lines.append("")
    lines.append("## Why this branch is separate")
    lines.append("")
    lines.append(
        "Mapped-coordinate behavior can change how PLCHHQ interprets and updates "
        "`XPOS/YPOS`, `XCEN/YCEN`, `XRGT/YRGT`, `XBEG/YBEG`, `XEND/YEND`, and "
        "`DL/DR/DB/DT`. It must not be approximated by current NDC/fontcap metrics."
    )
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

            for center, window in hits[:3]:
                count += 1
                lines.append(f"#### `{keyword}` hit {count}: `{rel}` line {center}")
                lines.append("")
                lines.append("```fortran")
                for n, src in window:
                    marker = ">>" if n == center else "  "
                    lines.append(f"{marker} {n:6d}: {src}")
                lines.append("```")
                lines.append("")

                if count >= 8:
                    break

            if count >= 8:
                break

        if count == 0:
            lines.append("No relevant source window detected.")
            lines.append("")

    lines.append("## Checklist before implementation")
    lines.append("")
    lines.append("- Locate exact `IMAP` branch entry and exit in NCL source.")
    lines.append("- Map coordinate spaces used by `XPOS/YPOS` and internal `XCEN/YCEN` state.")
    lines.append("- Map how mapped coordinates affect `DL/DR/DB/DT`.")
    lines.append("- Map PCGETR-visible state after mapped-coordinate calls.")
    lines.append("- Add positive smokes only after complete source semantics are mapped.")
    lines.append("- Keep unsupported mapped subcases guarded.")
    lines.append("")
    lines.append("## Guard rule")
    lines.append("")
    lines.append(
        "`IMAP != 0` must continue to raise guarded errors. It must not fall back "
        "to NDC/fontcap TextItem measurement behavior."
    )
    lines.append("")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT}")


def main() -> None:
    write_report()


if __name__ == "__main__":
    main()
