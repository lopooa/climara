from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "ncl_plotchar_function_code_coverage.md"


def main() -> None:
    subprocess.run(
        [sys.executable, "tools/report_ncl_plotchar_function_code_coverage.py"],
        cwd=ROOT,
        check=True,
    )

    if not DOC.exists():
        raise AssertionError(f"Expected coverage document to exist: {DOC}")

    text = DOC.read_text(encoding="utf-8")

    required = [
        "Python implemented command subset",
        "`B`: Subscript",
        "`D`: Down direction",
        "`Z`: Z zoom",
        "Guarded command letters",
        "Guarded non-command branches",
        "Implementation rule",
    ]

    missing = [item for item in required if item not in text]
    if missing:
        raise AssertionError(
            "Function-code coverage document is missing required items: "
            + ", ".join(missing)
        )

    print("✅ NCL Plotchar function-code coverage smoke passed")


if __name__ == "__main__":
    main()
