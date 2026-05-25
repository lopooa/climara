from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]

CHECK_FILES = [
    ROOT / "README.md",
    *sorted((ROOT / "docs").glob("*.md")),
]

FORBIDDEN_PATTERNS = [
    r"\bTextItem bbox\b.{0,40}\bis implemented\b",
    r"\bMultiText bbox\b.{0,40}\bis implemented\b",
    r"\bTextBBox engine\b.{0,40}\bis implemented\b",
    r"\bPlotchar parser\b.{0,40}\bis implemented\b",
    r"\bPlotchar metrics\b.{0,40}\bis implemented\b",
    r"\bDown text rendering\b.{0,40}\bis implemented\b",
    r"\bNhlDOWN\b.{0,40}\bis implemented\b",
    r"\bLabelBar AutoManage\b.{0,40}\bis implemented\b",
    r"\bLabelBar AdjustGeometry\b.{0,40}\bis implemented\b",
    r"\bfully NCL compatible\b",
    r"\bfull NCL replacement\b",
    r"\bcomplete NCL replacement\b",
]

ALLOWED_NEGATION_PATTERNS = [
    r"\bnot\b",
    r"\bnot yet\b",
    r"\bnot a\b",
    r"\bnot complete\b",
    r"\bnot fully\b",
    r"\bnot implemented\b",
    r"\bis not implemented\b",
    r"\bstill guarded\b",
    r"\bguarded/incomplete\b",
    r"\bincomplete\b",
    r"\bexplicit non-goals\b",
    r"未实现",
    r"没有实现",
    r"尚未",
]


def _line_is_allowed(line: str) -> bool:
    lowered = line.lower()
    return any(
        re.search(pattern, lowered, flags=re.IGNORECASE)
        for pattern in ALLOWED_NEGATION_PATTERNS
    )


def main():
    hits = []

    for path in CHECK_FILES:
        if not path.exists():
            continue

        text = path.read_text(encoding="utf-8", errors="ignore")
        for lineno, line in enumerate(text.splitlines(), start=1):
            for pattern in FORBIDDEN_PATTERNS:
                if not re.search(pattern, line, flags=re.IGNORECASE):
                    continue

                if _line_is_allowed(line):
                    continue

                hits.append((path.relative_to(ROOT), lineno, line.strip(), pattern))

    if hits:
        print("Found documentation claims that overstate incomplete graphics features:")
        for path, lineno, line, pattern in hits:
            print(f"{path}:{lineno}: {line}")
            print(f"  pattern: {pattern}")

        raise SystemExit(
            "TextItem bbox, MultiText bbox, Plotchar metrics/parser, Down text rendering, "
            "AutoManage, and AdjustGeometry are still guarded/incomplete. "
            "Do not document them as implemented."
        )

    print("OK: no overstated incomplete graphics claims found in README/docs")


if __name__ == "__main__":
    main()
