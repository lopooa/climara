from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

MILESTONE_SMOKES = [
    "tools/check_no_matplotlib.py",
    "tools/check_no_external_render_deps.py",
    "tools/smoke_python_plotchar_final_stage_closure.py",
    "tools/smoke_python_plotchar_milestone_manifest.py",
    "tools/smoke_python_plotchar_function_code_remaining_roadmap.py",
    "tools/smoke_python_plotchar_mapped_public_facade.py",
    "tools/smoke_python_plotchar_size_address_public_facade.py",
    "tools/smoke_python_plotchar_pwritx_public_facade.py",
    "tools/smoke_python_plotchar_measurement_contract_guard.py",
    "tools/smoke_python_mainline_project_boundary.py",
]


def run(script: str) -> None:
    path = ROOT / script
    if not path.exists():
        raise FileNotFoundError(f"Milestone smoke missing: {script}")

    print(f"RUN milestone smoke: {script}", flush=True)
    subprocess.run([sys.executable, script], cwd=ROOT, check=True)


def main() -> None:
    for script in MILESTONE_SMOKES:
        run(script)

    print("✅ Python Plotchar milestone smoke suite passed")


if __name__ == "__main__":
    main()
