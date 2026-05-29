from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from climara.graphics._plotchar_mapped_transform_ncl import (
    NclCoordinateTransformDirectionContract,
    guarded_ncl_coordinate_transform_direction_contract,
    validate_ncl_coordinate_transform_direction_contract,
)
from climara.graphics._plotchar_state import PlotcharUnsupportedError


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "ncl_coordinate_transform_direction_readiness.md"


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
        [sys.executable, "tools/report_ncl_coordinate_transform_direction_readiness.py"],
        cwd=ROOT,
        check=True,
    )

    if not DOC.exists():
        raise AssertionError(f"Expected report to exist: {DOC}")

    text = DOC.read_text(encoding="utf-8")
    required = [
        "NCL Coordinate Transform Direction Readiness",
        "Decision",
        "Evidence matrix",
        "Direction mapping checklist",
        "Guard rule",
    ]
    missing = [item for item in required if item not in text]
    if missing:
        raise AssertionError(
            "Direction readiness report missing sections: "
            + ", ".join(missing)
        )

    guarded = guarded_ncl_coordinate_transform_direction_contract()
    assert guarded.manually_verified is False
    assert_guarded(
        "not manually verified",
        lambda: validate_ncl_coordinate_transform_direction_contract(guarded),
    )

    incomplete = NclCoordinateTransformDirectionContract(
        cfux="user-to-fractional-x",
        cfuy="user-to-fractional-y",
        cufx="fractional-to-user-x",
        cufy="fractional-to-user-y",
        getset="viewport-window-read",
        set_call="unverified",
        source_map_reference="docs/ncl_coordinate_transform_direction_readiness.md",
        manually_verified=True,
    )
    assert_guarded(
        "unverified fields",
        lambda: validate_ncl_coordinate_transform_direction_contract(incomplete),
    )

    verified = NclCoordinateTransformDirectionContract(
        cfux="user-to-fractional-x",
        cfuy="user-to-fractional-y",
        cufx="fractional-to-user-x",
        cufy="fractional-to-user-y",
        getset="viewport-window-read",
        set_call="viewport-window-write",
        source_map_reference="docs/ncl_coordinate_transform_direction_readiness.md",
        manually_verified=True,
    )
    validate_ncl_coordinate_transform_direction_contract(verified)

    print("✅ NCL coordinate-transform direction readiness smoke passed")


if __name__ == "__main__":
    main()
