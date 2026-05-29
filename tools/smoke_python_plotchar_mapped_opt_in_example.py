from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "python_plotchar_mapped_opt_in_backend_usage.md"
EXAMPLE = ROOT / "examples" / "plotchar_mapped_opt_in_linear.py"


def main() -> None:
    if not DOC.exists():
        raise AssertionError(f"Expected usage document to exist: {DOC}")

    text = DOC.read_text(encoding="utf-8")
    required = [
        "Python Plotchar Explicit Opt-In Mapped Backend Usage",
        "Supported subset",
        "Still guarded",
        "Minimal usage pattern",
        "Boundary rule",
    ]

    missing = [item for item in required if item not in text]
    if missing:
        raise AssertionError("mapped opt-in usage document missing sections: " + ", ".join(missing))

    if not EXAMPLE.exists():
        raise AssertionError(f"Expected example to exist: {EXAMPLE}")

    result = subprocess.run(
        [sys.executable, str(EXAMPLE)],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    stdout = result.stdout
    required_output = [
        "Mapped opt-in result:",
        "Unmapped core reference:",
        "metrics:",
    ]

    missing_output = [item for item in required_output if item not in stdout]
    if missing_output:
        raise AssertionError(
            "mapped opt-in example output missing sections: "
            + ", ".join(missing_output)
            + "\nOutput was:\n"
            + stdout
        )

    print("✅ Python Plotchar mapped opt-in example smoke passed")


if __name__ == "__main__":
    main()
