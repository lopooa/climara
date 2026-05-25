from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

BLOCKED_ROOT_PATTERNS = [
    "apply_*.py",
    "*.patch",
    "*.diff",
]

ALLOWLIST = {
    "pyproject.toml",
}


def main():
    hits = []

    for pattern in BLOCKED_ROOT_PATTERNS:
        for path in ROOT.glob(pattern):
            if path.name in ALLOWLIST:
                continue
            if path.is_file():
                hits.append(path.relative_to(ROOT))

    if hits:
        print("Found local worktree artifact files that should not be committed:")
        for path in hits:
            print(f"  - {path}")
        raise SystemExit(1)

    print("OK: no local worktree artifact files found in project root")


if __name__ == "__main__":
    main()
