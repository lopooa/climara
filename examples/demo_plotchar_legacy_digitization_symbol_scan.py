from pathlib import Path
import os


SYMBOLS = [
    "SUBROUTINE PCBDFF",
    "BLOCK DATA PCBDFF",
    "SUBROUTINE PCBLDA",
    "BLOCK DATA PCBLDA",
    "SUBROUTINE PCCFFF",
    "SUBROUTINE PCCFFC",
    "SUBROUTINE PCEXCD",
    "CALL PCCFFF",
    "CALL PCCFFC",
    "CALL PCEXCD",
    "DATA INDA",
    "DATA IDDA",
    "READ",
    "INDA(",
    "IDDA(",
]


def source_root() -> Path:
    value = os.environ.get("NCL_SRC_ROOT")
    if not value:
        raise RuntimeError("Set NCL_SRC_ROOT=/mnt/d/Projects/NCL")
    return Path(value)


def iter_source_files(root: Path):
    suffixes = {".f", ".F", ".f90", ".F90", ".c", ".h", ".inc", ".dat", ".txt"}

    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix in suffixes:
            yield path


def main():
    root = source_root()
    hits = []

    for path in iter_source_files(root):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        upper = text.upper()
        matched = [symbol for symbol in SYMBOLS if symbol in upper]

        if matched:
            hits.append((path, matched, text.splitlines()))

    print("NCL source root:", root)
    print("matched files:", len(hits))
    print()

    for path, matched, lines in hits:
        print("=" * 88)
        print(path.relative_to(root))
        print("matched:", ", ".join(matched))
        print("=" * 88)

        upper_lines = [line.upper() for line in lines]

        for symbol in matched:
            print()
            print(f"-- {symbol} --")
            count = 0

            for i, upper_line in enumerate(upper_lines, start=1):
                if symbol in upper_line:
                    count += 1
                    start = max(1, i - 5)
                    end = min(len(lines), i + 8)

                    print(f"window lines {start}-{end}")
                    for j in range(start, end + 1):
                        marker = ">>" if j == i else "  "
                        print(f"{marker} {j:5d}: {lines[j - 1]}")

                    if count >= 4:
                        print("  ... more hits omitted for this symbol")
                        break

        print()

    if not hits:
        raise RuntimeError("No legacy digitization symbol hits found")

    print("✅ legacy digitization symbol scan completed")


if __name__ == "__main__":
    main()
