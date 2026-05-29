from __future__ import annotations

from pathlib import Path

from climara.graphics._plotchar_mapped_coordinate import (
    MappedCoordinateExtent,
    MappedCoordinatePoint,
    MappedCoordinateTransformProvider,
)
from climara.graphics._plotchar_mapped_runtime_strategy import (
    ProviderBackedMappedCoordinateRuntimeStrategy,
)
from climara.graphics._plotchar_plchhq_extent import compute_plchhq_fontcap_text_extent
from climara.graphics._plotchar_state import PlotcharState


class OffsetScaleSourceMappedProvider(MappedCoordinateTransformProvider):
    source_mapped = True
    source_map_reference = "docs/ncl_plotchar_mapped_exact_branch_packet.md"

    def __init__(self):
        self.user_to_plotchar_calls = []
        self.plotchar_to_user_calls = []
        self.extent_to_user_calls = []

    def user_to_plotchar(self, point: MappedCoordinatePoint) -> MappedCoordinatePoint:
        self.user_to_plotchar_calls.append(point)
        return MappedCoordinatePoint(point.x + 0.10, point.y + 0.20)

    def plotchar_to_user(self, point: MappedCoordinatePoint) -> MappedCoordinatePoint:
        self.plotchar_to_user_calls.append(point)
        return MappedCoordinatePoint(point.x - 0.10, point.y - 0.20)

    def extent_to_user(
        self,
        *,
        origin: MappedCoordinatePoint,
        extent: MappedCoordinateExtent,
    ) -> MappedCoordinateExtent:
        self.extent_to_user_calls.append((origin, extent))
        return MappedCoordinateExtent(
            dl=extent.dl * 2.0,
            dr=extent.dr * 2.0,
            db=extent.db * 3.0,
            dt=extent.dt * 3.0,
        )


def fontcap_dir() -> Path:
    import os

    explicit = os.environ.get("CLIMARA_PLOTCHAR_FONTCAP_DIR")
    if explicit:
        return Path(explicit)

    ncl_root = os.environ.get("NCL_SRC_ROOT")
    if not ncl_root:
        raise SystemExit("Set NCL_SRC_ROOT=/mnt/d/Projects/NCL")

    return Path(ncl_root) / "common" / "src" / "fontcap"


def state_with_ma(value: int) -> PlotcharState:
    state = PlotcharState.defaults()
    state.pcseti("TE", 1)
    state.pcseti("QU", 0)
    state.pcseti("FN", 21)
    state.pcseti("MA", value)
    return state


def real_string(state: PlotcharState) -> str:
    code = chr(state.nfcc) if state.nfcc >= 0 else ":"
    return f"{code}A{code}ABC"


def main() -> None:
    provider = OffsetScaleSourceMappedProvider()
    strategy = ProviderBackedMappedCoordinateRuntimeStrategy()

    mapped_state = state_with_ma(1)
    unmapped_state = state_with_ma(0)

    mapped = compute_plchhq_fontcap_text_extent(
        chrs=real_string(mapped_state),
        state=mapped_state,
        xpos=0.5,
        ypos=0.5,
        size=0.03,
        angle=360.0,
        cntr=-1.0,
        fontcap_dir=fontcap_dir(),
        mapped_transform_provider=provider,
        mapped_runtime_strategy=strategy,
    )

    direct_core = compute_plchhq_fontcap_text_extent(
        chrs=real_string(unmapped_state),
        state=unmapped_state,
        xpos=0.6,
        ypos=0.7,
        size=0.03,
        angle=360.0,
        cntr=-1.0,
        fontcap_dir=fontcap_dir(),
    )

    assert provider.user_to_plotchar_calls == [MappedCoordinatePoint(0.5, 0.5)]
    assert len(provider.extent_to_user_calls) == 1

    origin, core_extent = provider.extent_to_user_calls[0]
    assert origin == MappedCoordinatePoint(0.5, 0.5)
    assert core_extent.dl == direct_core.metrics.dl
    assert core_extent.dr == direct_core.metrics.dr
    assert core_extent.db == direct_core.metrics.db
    assert core_extent.dt == direct_core.metrics.dt

    assert mapped.metrics.dl == direct_core.metrics.dl * 2.0
    assert mapped.metrics.dr == direct_core.metrics.dr * 2.0
    assert mapped.metrics.db == direct_core.metrics.db * 3.0
    assert mapped.metrics.dt == direct_core.metrics.dt * 3.0
    assert mapped.text == direct_core.text
    assert mapped.font_number == direct_core.font_number
    assert mapped.glyph_count == direct_core.glyph_count

    print("✅ Python Plotchar provider-backed mapped-coordinate strategy smoke passed")


if __name__ == "__main__":
    main()
