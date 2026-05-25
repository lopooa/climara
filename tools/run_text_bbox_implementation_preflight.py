import argparse
import os
from pathlib import Path


REQUIRED = {
    "ni/src/lib/hlu/TextItem.c": [
        "FigureAndSetTextBBInfo",
        "TextItemDraw",
        "c_plchhq",
        "c_pcgetr",
    ],
    "ni/src/lib/hlu/MultiText.c": [
        "GetMaxTextLength",
        "SetDrawFlags",
        "NhlNvpXF",
        "NhlNvpYF",
        "NhlNvpWidthF",
        "NhlNvpHeightF",
    ],
    "ni/src/lib/hlu/LabelBar.c": [
        "SetTitle",
        "SetLabels",
        "AdjustGeometry",
        "NhlGetBB",
    ],
}


def candidate_roots():
    roots = []

    env_root = os.environ.get("NCL_SRC_ROOT")
    if env_root:
        roots.append(Path(env_root))

    roots.extend(
        [
            Path.cwd() / "external" / "ncl",
            Path.cwd() / "vendor" / "ncl",
            Path.cwd() / "ncl",
            Path.cwd().parent / "ncl",
            Path.cwd().parent / "NCL",
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

    return out


def find_root():
    for root in candidate_roots():
        if all((root / rel).exists() for rel in REQUIRED):
            return root
    return None


def print_required_summary():
    print("Required NCL source files and symbols:")
    for rel, symbols in REQUIRED.items():
        print(f"- {rel}")
        for symbol in symbols:
            print(f"  - {symbol}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--allow-missing",
        action="store_true",
        help="Report missing NCL source without failing. Used by smoke tests.",
    )
    args = parser.parse_args()

    print("TextBBox implementation preflight")
    print("=" * 33)
    print()

    print_required_summary()

    print()
    print("Candidate roots:")
    for root in candidate_roots():
        print(f"- {root}")

    print()
    root = find_root()

    if root is None:
        print("BLOCKED: complete NCL source tree was not found.")
        print()
        print("Set NCL_SRC_ROOT to the root of a full NCL source checkout before implementing bbox behavior.")
        print("Example:")
        print("  export NCL_SRC_ROOT=/mnt/d/Projects/NCL")

        if args.allow_missing:
            return

        raise SystemExit(2)

    print(f"Using NCL source root: {root}")
    print()

    missing_symbols = []

    for rel, symbols in REQUIRED.items():
        path = root / rel
        text = path.read_text(encoding="utf-8", errors="ignore")

        print(f"Checking {rel}")
        for symbol in symbols:
            if symbol in text:
                print(f"  ✅ {symbol}")
            else:
                print(f"  ❌ {symbol}")
                missing_symbols.append((rel, symbol))

    print()

    if missing_symbols:
        print("BLOCKED: required NCL source symbols were not found.")
        for rel, symbol in missing_symbols:
            print(f"- {rel}: {symbol}")

        if args.allow_missing:
            return

        raise SystemExit(3)

    print("READY: required NCL source files and symbols are available.")
    print()
    print("Next step should still be a source-mapping design, not direct visual bbox implementation.")


if __name__ == "__main__":
    main()
