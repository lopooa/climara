from __future__ import annotations

from climara.graphics import _plotchar_plchhq_extent as extent
from climara.graphics._plotchar_mapped_coordinate import (
    MappedCoordinateExtent,
    MappedCoordinatePoint,
    MappedCoordinateResult,
    MappedCoordinateTransformProvider,
)
from climara.graphics._plotchar_mapped_runtime_strategy import MappedCoordinateRuntimeStrategy
from climara.graphics._plotchar_metrics import build_plotchar_extent_metrics
from climara.graphics._plotchar_state import PlotcharState


class SourceMappedTransformProvider(MappedCoordinateTransformProvider):
    source_mapped = True
    source_map_reference = "docs/ncl_plotchar_mapped_exact_branch_packet.md"

    def user_to_plotchar(self, point: MappedCoordinatePoint) -> MappedCoordinatePoint:
        return point

    def plotchar_to_user(self, point: MappedCoordinatePoint) -> MappedCoordinatePoint:
        return point

    def extent_to_user(
        self,
        *,
        origin: MappedCoordinatePoint,
        extent: MappedCoordinateExtent,
    ) -> MappedCoordinateExtent:
        return extent


class FakeRuntimeStrategy(MappedCoordinateRuntimeStrategy):
    source_mapped = True
    runtime_implemented = True
    source_map_reference = "docs/ncl_plotchar_mapped_exact_branch_packet.md"

    def __init__(self):
        self.calls = []

    def compute(self, request):
        self.calls.append(request)
        return MappedCoordinateResult(
            metrics=build_plotchar_extent_metrics(
                dl=0.21,
                dr=0.22,
                db=0.23,
                dt=0.24,
            ),
            state=request.state,
            text="ABC",
            font_number=21,
            glyph_count=3,
        )


def mapped_state() -> PlotcharState:
    state = PlotcharState.defaults()
    state.pcseti("TE", 1)
    state.pcseti("QU", 0)
    state.pcseti("FN", 21)
    state.pcseti("MA", 1)
    return state


def real_string(state: PlotcharState) -> str:
    code = chr(state.nfcc) if state.nfcc >= 0 else ":"
    return f"{code}A{code}ABC"


def main() -> None:
    state = mapped_state()
    transform = SourceMappedTransformProvider()
    strategy = FakeRuntimeStrategy()

    result = extent.compute_plchhq_fontcap_text_extent(
        chrs=real_string(state),
        state=state,
        xpos=0.5,
        ypos=0.5,
        size=0.03,
        angle=360.0,
        cntr=-1.0,
        fontcap_dir=None,
        mapped_transform_provider=transform,
        mapped_runtime_strategy=strategy,
    )

    assert strategy.calls, "mapped runtime strategy was not called"
    request = strategy.calls[0]
    assert request.transform_provider is transform
    assert request.runtime_strategy is strategy
    assert request.snapshot.imap == 1

    assert result.text == "ABC"
    assert result.font_number == 21
    assert result.glyph_count == 3
    assert result.metrics.dl == 0.21
    assert result.metrics.dr == 0.22
    assert result.metrics.db == 0.23
    assert result.metrics.dt == 0.24

    print("✅ Python Plotchar mapped-coordinate runtime strategy injection smoke passed")


if __name__ == "__main__":
    main()
