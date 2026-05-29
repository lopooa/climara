from __future__ import annotations

import importlib.util
from pathlib import Path

from climara.graphics._ncl_plotchar_real_library import (
    NCL_PLOTCHAR_LIBRARY_DIRS_ENV,
    NCL_PLOTCHAR_LIBRARY_ENV,
    validate_configured_ncl_plotchar_library,
)


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "tools" / "report_ncl_plotchar_real_library.py"


def load_run_real_backend_smoke():
    spec = importlib.util.spec_from_file_location(
        "climara_report_ncl_plotchar_real_library",
        REPORT_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {REPORT_PATH}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.run_real_backend_smoke


def main():
    validation = validate_configured_ncl_plotchar_library()

    if not validation.ok:
        print(
            "SKIP: no validated real NCAR/NCL Plotchar shared library is configured. "
            f"Set {NCL_PLOTCHAR_LIBRARY_ENV} or {NCL_PLOTCHAR_LIBRARY_DIRS_ENV} to run this smoke."
        )
        return

    run_real_backend_smoke = load_run_real_backend_smoke()
    run_real_backend_smoke()
    print("✅ real NCAR/NCL Plotchar backend smoke passed")


if __name__ == "__main__":
    main()
