from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "ncl_plotchar_remaining_branch_source_map.md"

IMPLEMENTED_FUNCTION_CODE = [
    "A across direction",
    "B subscript",
    "C carriage return",
    "D down direction",
    "E end script",
    "F font change",
    "H horizontal movement",
    "I indexical size",
    "K cartographic size",
    "L lower case",
    "N normal script",
    "P principal size",
    "S superscript",
    "U upper case",
    "V vertical movement",
    "X x zoom",
    "Y y zoom",
    "Z z zoom",
    "doubled function-code signal literal escape",
    "PCGTDI-style signed decimal integer parser",
]

REMAINING_GUARDED = [
    "PWRITX / font-0 / database font branch",
    "non-fontcap Plotchar metrics branch",
    "Medium / Low / Workstation quality branches",
    "mapped-coordinate branch, IMAP != 0",
    "address-unit SIZE semantics, SIZE <= 0 or SIZE >= 1",
    "generic PLCHHQ calls outside TextItem measurement contract",
    "unsupported function-code branches not yet mapped from plchhq.f",
]

ANCHOR_FILENAMES = [
    "plchhq.f",
    "pcgtdi.f",
    "pcgetr.f",
    "pcseti.f",
    "pcsetr.f",
    "pcsetc.f",
    "c_plchhq.c",
    "c_pcgetr.c",
    "c_pcseti.c",
    "c_pcsetr.c",
    "c_pcsetc.c",
]

KEYWORDS = [
    "PWRITX",
    "PWRITY",
    "FONT 0",
    "IPWR",
    "IQUF",
    "IMAP",
    "MAP",
    "SIZE",
    "NODF",
    "PCGTDI",
    "PWR",
    "FN",
    "QU",
    "TE",
]


@dataclass(frozen=True)
class SourceHit:
    path: Path
    line_number: int
    line: str


def ncl_root() -> Path:
    value = os.environ.get("NCL_SRC_ROOT")
    if not value:
        raise SystemExit("Set NCL_SRC_ROOT=/mnt/d/Projects/NCL before running this report.")

    root = Path(value)
    if not root.exists():
        raise SystemExit(f"NCL_SRC_ROOT does not exist: {root}")

    return root


def text_files(root: Path):
    allowed_suffixes = {".f", ".F", ".f90", ".F90", ".c", ".h", ".ncl", ".txt"}

    for path in root.rglob("*"):
        if not path.is_file():
            continue

        name = path.name.lower()
        suffix = path.suffix

        if suffix not in allowed_suffixes:
            continue

        if (
            "plotchar" in str(path).lower()
            or "fontcap" in str(path).lower()
            or "pwr" in name
            or "pc" in name
            or name in ANCHOR_FILENAMES
        ):
            yield path


def safe_read(path: Path) -> str:
    for encoding in ("utf-8", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue

    return ""


def find_anchor_files(root: Path) -> dict[str, list[Path]]:
    by_name: dict[str, list[Path]] = {name: [] for name in ANCHOR_FILENAMES}

    for path in root.rglob("*"):
        if not path.is_file():
            continue

        lower = path.name.lower()
        for name in ANCHOR_FILENAMES:
            if lower == name.lower():
                by_name[name].append(path)

    return by_name


def find_keyword_hits(root: Path, *, max_hits_per_keyword: int = 12) -> dict[str, list[SourceHit]]:
    hits: dict[str, list[SourceHit]] = {keyword: [] for keyword in KEYWORDS}

    for path in text_files(root):
        text = safe_read(path)
        if not text:
            continue

        lines = text.splitlines()
        upper_lines = [line.upper() for line in lines]

        for keyword in KEYWORDS:
            if len(hits[keyword]) >= max_hits_per_keyword:
                continue

            needle = keyword.upper()
            for index, line in enumerate(upper_lines, start=1):
                if needle in line:
                    hits[keyword].append(
                        SourceHit(
                            path=path,
                            line_number=index,
                            line=lines[index - 1].rstrip(),
                        )
                    )

                    if len(hits[keyword]) >= max_hits_per_keyword:
                        break

    return hits


def format_rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def write_report() -> None:
    root = ncl_root()
    anchor_files = find_anchor_files(root)
    hits = find_keyword_hits(root)

    DOC.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    lines.append("# NCL Plotchar Remaining Branch Source Map")
    lines.append("")
    lines.append("This document is generated from the local NCL source tree.")
    lines.append("")
    lines.append(f"- `NCL_SRC_ROOT`: `{root}`")
    lines.append("")
    lines.append("## Implemented Python mainline subset")
    lines.append("")

    for item in IMPLEMENTED_FUNCTION_CODE:
        lines.append(f"- {item}")

    lines.append("")
    lines.append("## Remaining guarded branches")
    lines.append("")

    for item in REMAINING_GUARDED:
        lines.append(f"- {item}")

    lines.append("")
    lines.append("## Required source anchor files")
    lines.append("")

    for name in ANCHOR_FILENAMES:
        paths = anchor_files.get(name, [])

        if paths:
            lines.append(f"- `{name}`")
            for path in paths:
                lines.append(f"  - `{format_rel(path, root)}`")
        else:
            lines.append(f"- `{name}`: not found in current source tree")

    lines.append("")
    lines.append("## Keyword hits for remaining branches")
    lines.append("")

    for keyword in KEYWORDS:
        lines.append(f"### `{keyword}`")
        lines.append("")

        keyword_hits = hits.get(keyword, [])

        if not keyword_hits:
            lines.append("No local source hits found.")
            lines.append("")
            continue

        for hit in keyword_hits:
            lines.append(
                f"- `{format_rel(hit.path, root)}` line {hit.line_number}: "
                f"`{hit.line.strip()}`"
            )

        lines.append("")

    lines.append("## Implementation boundary")
    lines.append("")
    lines.append(
        "This report does not claim that PWRITX, non-fontcap, mapped-coordinate, "
        "address-unit SIZE, or non-TextItem PLCHHQ branches are implemented."
    )
    lines.append("")
    lines.append(
        "The purpose is to keep the remaining source branches visible before any "
        "Python implementation is attempted. If a branch is not source-mapped here, "
        "it must stay guarded."
    )
    lines.append("")

    DOC.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {DOC}")


def main() -> None:
    write_report()


if __name__ == "__main__":
    main()
