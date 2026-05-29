from __future__ import annotations

from climara.graphics._plotchar_mapped_coordinate import (
    MappedCoordinateExtent,
    MappedCoordinatePoint,
)
from climara.graphics._plotchar_mapped_transform_ncl import (
    NclCoordinateTransformDirectionContract,
    NclLinearWindowViewportTransformProvider,
    NclWindowViewportState,
)
from climara.graphics._plotchar_state import PlotcharUnsupportedError


def verified_contract() -> NclCoordinateTransformDirectionContract:
    return NclCoordinateTransformDirectionContract(
        cfux="user-to-fractional-x",
        cfuy="user-to-fractional-y",
        cufx="fractional-to-user-x",
        cufy="fractional-to-user-y",
        getset="viewport-window-read",
        set_call="viewport-window-write",
        source_map_reference="docs/ncl_coordinate_transform_formula_audit.md",
        manually_verified=True,
    )


def main() -> None:
    state = NclWindowViewportState(
        viewport_left=0.2,
        viewport_right=0.8,
        viewport_bottom=0.1,
        viewport_top=0.9,
        window_left=0.0,
        window_right=10.0,
        window_bottom=100.0,
        window_top=200.0,
        log_scaling_flag=1,
    )

    provider = NclLinearWindowViewportTransformProvider(
        state=state,
        direction_contract=verified_contract(),
    )

    user = MappedCoordinatePoint(5.0, 150.0)
    plotchar = provider.user_to_plotchar(user)
    assert abs(plotchar.x - 0.5) < 1e-12
    assert abs(plotchar.y - 0.5) < 1e-12

    roundtrip = provider.plotchar_to_user(plotchar)
    assert abs(roundtrip.x - user.x) < 1e-12
    assert abs(roundtrip.y - user.y) < 1e-12

    extent = provider.extent_to_user(
        origin=user,
        extent=MappedCoordinateExtent(dl=0.06, dr=0.12, db=0.08, dt=0.16),
    )

    assert abs(extent.dl - 1.0) < 1e-12
    assert abs(extent.dr - 2.0) < 1e-12
    assert abs(extent.db - 10.0) < 1e-12
    assert abs(extent.dt - 20.0) < 1e-12

    try:
        NclLinearWindowViewportTransformProvider(
            state=state,
            direction_contract=NclCoordinateTransformDirectionContract(
                # This is intentionally verified-looking but direction-wrong.
                # It should pass the generic direction-contract guard and fail
                # specifically in _validate_linear_contract().
                cfux="fractional-to-user-x",
                cfuy="user-to-fractional-y",
                cufx="fractional-to-user-x",
                cufy="fractional-to-user-y",
                getset="viewport-window-read",
                set_call="viewport-window-write",
                source_map_reference="docs/ncl_coordinate_transform_formula_audit.md",
                manually_verified=True,
            ),
        )
    except PlotcharUnsupportedError as exc:
        assert "does not match expected" in str(exc), str(exc)
    else:
        raise AssertionError("linear provider accepted wrong direction contract")

    print("✅ Python NCL linear window/viewport transform provider smoke passed")


if __name__ == "__main__":
    main()
