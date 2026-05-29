from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from climara.graphics._plotchar_mapped_transform_ncl import (
    NclMappedCoordinateTransformProvider,
)
from climara.graphics._plotchar_mapped_coordinate import (
    MappedCoordinateExtent,
    MappedCoordinatePoint,
)
from climara.graphics._plotchar_state import PlotcharUnsupportedError


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "ncl_coordinate_transform_function_definitions.md"


def assert_guarded(message_part: str, func) -> None:
    try:
        func()
    except PlotcharUnsupportedError as exc:
        message = str(exc)
        assert message_part in message, message
    else:
        raise AssertionError(f"Expected PlotcharUnsupportedError containing {message_part!r}")


def main() -> None:
    subprocess.run(
        [sys.executable, "tools/report_ncl_coordinate_transform_function_definitions.py"],
        cwd=ROOT,
        check=True,
    )

    if not DOC.exists():
        raise AssertionError(f"Expected report to exist: {DOC}")

    text = DOC.read_text(encoding="utf-8")

    required = [
        "NCL Coordinate Transform Function Definitions",
        "Definition availability",
        "Function / subroutine definitions",
        "Fallback keyword windows",
        "Manual mapping checklist",
        "Guard rule",
    ]

    missing = [item for item in required if item not in text]
    if missing:
        raise AssertionError(
            "Coordinate transform definition report missing sections: "
            + ", ".join(missing)
        )

    provider = NclMappedCoordinateTransformProvider()
    point = MappedCoordinatePoint(0.5, 0.6)
    extent = MappedCoordinateExtent(0.1, 0.2, 0.3, 0.4)

    assert_guarded("not implemented", lambda: provider.user_to_plotchar(point))
    assert_guarded("not implemented", lambda: provider.plotchar_to_user(point))
    assert_guarded("not implemented", lambda: provider.extent_to_user(origin=point, extent=extent))

    print("✅ NCL coordinate-transform function definition smoke passed")


if __name__ == "__main__":
    main()
