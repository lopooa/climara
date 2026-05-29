from __future__ import annotations

from pathlib import Path

from climara.graphics._plotchar_mapped_coordinate import (
    MappedCoordinateExtent,
    MappedCoordinatePoint,
)
from climara.graphics._plotchar_mapped_transform_ncl import (
    NclMappedCoordinateTransformProvider,
    build_ncl_mapped_transform_guard_message,
    ncl_coordinate_transform_report_paths,
    ncl_mapped_coordinate_transform_boundary,
)
from climara.graphics._plotchar_state import PlotcharUnsupportedError


ROOT = Path(__file__).resolve().parents[1]


def assert_guarded(message_part: str, func) -> None:
    try:
        func()
    except PlotcharUnsupportedError as exc:
        message = str(exc)
        assert message_part in message, message
    else:
        raise AssertionError(f"Expected PlotcharUnsupportedError containing {message_part!r}")


def main() -> None:
    boundary = ncl_mapped_coordinate_transform_boundary()
    assert boundary.implemented is False
    assert "CFUX/CFUY/CUFX/CUFY/GETSET/SET" in boundary.reason

    provider = NclMappedCoordinateTransformProvider()
    assert provider.source_mapped is False
    assert provider.source_map_reference == ""

    point = MappedCoordinatePoint(0.5, 0.6)
    extent = MappedCoordinateExtent(dl=0.1, dr=0.2, db=0.3, dt=0.4)

    assert_guarded(
        "NCL mapped-coordinate transform provider is not implemented",
        lambda: provider.user_to_plotchar(point),
    )
    assert_guarded(
        "NCL mapped-coordinate transform provider is not implemented",
        lambda: provider.plotchar_to_user(point),
    )
    assert_guarded(
        "NCL mapped-coordinate transform provider is not implemented",
        lambda: provider.extent_to_user(origin=point, extent=extent),
    )

    message = build_ncl_mapped_transform_guard_message()
    assert "Required source-map documents" in message

    missing = [path for path in ncl_coordinate_transform_report_paths(ROOT) if not path.exists()]
    if missing:
        raise AssertionError("missing NCL mapped transform source-map docs: " + ", ".join(str(path) for path in missing))

    print("✅ Python Plotchar NCL mapped-transform boundary smoke passed")


if __name__ == "__main__":
    main()
