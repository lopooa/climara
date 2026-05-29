from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


COMMANDS = [
    [sys.executable, "tools/check_no_matplotlib.py"],
    [sys.executable, "tools/check_no_external_render_deps.py"],
    [sys.executable, "tools/run_plotchar_provider_contract_smokes.py"],
]


def run(command: list[str]) -> None:
    print()
    print("+", " ".join(command))
    subprocess.run(command, cwd=ROOT, check=True, env=os.environ.copy())


def main() -> None:
    for command in COMMANDS:
        run(command)

    print()
    print("+ git diff --stat")
    subprocess.run(["git", "diff", "--stat"], cwd=ROOT, check=False)

    print()
    print("+ git status --short")
    subprocess.run(["git", "status", "--short"], cwd=ROOT, check=False)

    print()
    print("✅ Plotchar provider/contract stage closure checks passed")
    print()
    print("Stage boundary:")
    print("- Provider/contract seams are checked.")
    print("- Real PCFRED record reading is still not implemented.")
    print("- Real IDDA parcel decoding is still not implemented.")
    print("- Real Greek/PWRITX glyph parity is still not implemented.")
    print("- Real mapped transform/clipping parity is still not implemented.")


if __name__ == "__main__":
    main()
