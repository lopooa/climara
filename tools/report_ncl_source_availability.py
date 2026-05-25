import os
from pathlib import Path


REQUIRED_FILES = [
    "ni/src/lib/hlu/TextItem.c",
    "ni/src/lib/hlu/MultiText.c",
    "ni/src/lib/hlu/LabelBar.c",
]


def candidate_roots():
    values = []

    env_root = os.environ.get("NCL_SRC_ROOT")
    if env_root:
        values.append(Path(env_root))

    values.extend(
        [
            Path.cwd() / "external" / "ncl",
            Path.cwd() / "vendor" / "ncl",
            Path.cwd() / "ncl",
            Path.cwd().parent / "ncl",
            Path.cwd().parent / "NCL",
        ]
    )

    seen = set()
    out = []

    for root in values:
        resolved = root.expanduser()
        key = str(resolved)
        if key in seen:
            continue
        seen.add(key)
        out.append(resolved)

    return out


def find_sources():
    roots = candidate_roots()
    matches = {}

    for rel in REQUIRED_FILES:
        matches[rel] = []
        for root in roots:
            path = root / rel
            if path.exists():
                matches[rel].append(path)

    return roots, matches


def main():
    roots, matches = find_sources()

    print("NCL source availability report")
    print("=" * 30)
    print()

    print("Candidate roots:")
    for root in roots:
        print(f"- {root}")

    print()
    print("Required files:")

    all_found = True

    for rel in REQUIRED_FILES:
        found = matches[rel]
        if found:
            print(f"✅ {rel}")
            for path in found:
                print(f"   {path}")
        else:
            all_found = False
            print(f"❌ {rel}")

    print()
    if all_found:
        print("All required NCL source files are available.")
    else:
        print("Some required NCL source files are not available.")
        print("Set NCL_SRC_ROOT to the root of a full NCL source checkout before implementing bbox behavior.")
        print("Example:")
        print("  export NCL_SRC_ROOT=/mnt/d/Projects/NCL")


if __name__ == "__main__":
    main()
