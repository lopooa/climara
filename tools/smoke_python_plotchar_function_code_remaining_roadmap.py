from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "python_plotchar_function_code_remaining_roadmap.md"


def main() -> None:
    subprocess.run(
        [sys.executable, "tools/report_python_plotchar_function_code_remaining_roadmap.py"],
        cwd=ROOT,
        check=True,
    )

    if not DOC.exists():
        raise AssertionError(f"Expected roadmap to exist: {DOC}")

    text = DOC.read_text(encoding="utf-8")
    required = [
        "Python Plotchar Remaining Function-Code Roadmap",
        "Current implemented groups",
        "Remaining letters",
        "High-risk remaining letters",
        "Recommended next implementation order",
        "Guard rule",
    ]

    missing = [item for item in required if item not in text]
    if missing:
        raise AssertionError("function-code remaining roadmap missing sections: " + ", ".join(missing))

    for known in ["B", "S", "E", "N", "P", "I", "K", "U", "L", "C", "X", "Y", "Z", "H", "V", "F"]:
        if f"`{known}`" not in text:
            raise AssertionError(f"implemented group letter missing from roadmap: {known}")

    if "Do not implement `G` or `R` until SIZE/address-unit formulas are manually mapped." not in text:
        raise AssertionError("roadmap must guard G/R behind SIZE/address mapping")

    print("✅ Python Plotchar remaining function-code roadmap smoke passed")


if __name__ == "__main__":
    main()
