from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from climara.graphics._plotchar_metrics import build_plotchar_extent_metrics
from climara.graphics._plotchar_plchhq_extent import compute_plchhq_fontcap_text_extent
from climara.graphics._plotchar_pwritx_nonfontcap import (
    PwritxNonFontcapResult,
    build_pwritx_nonfontcap_request,
    compute_pwritx_nonfontcap_extent,
)
from climara.graphics._plotchar_size_address_unit import SizeAddressUnitResult
from climara.graphics._plotchar_state import PlotcharState, PlotcharUnsupportedError
from climara.graphics.mapped_plotchar import (
    NclCoordinateTransformDirectionContract,
    NclWindowViewportState,
    build_ncl_linear_mapped_backend_config,
    compute_plchhq_with_ncl_linear_mapping,
)
from climara.graphics.pwritx_plotchar import (
    PwritxMetricsProvider,
    build_pwritx_provider_backend_config,
    compute_plchhq_with_pwritx_provider,
)
from climara.graphics.size_address_plotchar import (
    SizeAddressScaleProvider,
    build_size_address_provider_backend_config,
    compute_plchhq_with_size_address_provider,
)


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "python_plotchar_final_stage_closure.md"


class SourceMappedSizeProvider(SizeAddressScaleProvider):
    source_mapped = True
    source_map_reference = "docs/ncl_plotchar_size_address_formula_audit.md"

    def fractional_core_size(self, request) -> float:
        return 0.03

    def result_from_core(self, *, request, core_result) -> SizeAddressUnitResult:
        return SizeAddressUnitResult(
            metrics=build_plotchar_extent_metrics(
                dl=core_result.metrics.dl * 10.0,
                dr=core_result.metrics.dr * 10.0,
                db=core_result.metrics.db * 10.0,
                dt=core_result.metrics.dt * 10.0,
            ),
            state=core_result.state,
            text=core_result.text,
            font_number=core_result.font_number,
            glyph_count=core_result.glyph_count,
        )


class SourceMappedPwritxProvider(PwritxMetricsProvider):
    source_mapped = True
    source_map_reference = "docs/ncl_plotchar_pwritx_formula_audit.md"

    def __init__(self):
        self.calls = []

    def metrics_for_request(self, request):
        self.calls.append(request)
        return PwritxNonFontcapResult(
            metrics=build_plotchar_extent_metrics(
                dl=0.81,
                dr=0.82,
                db=0.83,
                dt=0.84,
            ),
            state=request.state,
            text="ABC",
            font_number=0,
            glyph_count=3,
        )


def fontcap_dir() -> Path:
    import os

    ncl_root = os.environ.get("NCL_SRC_ROOT")
    if not ncl_root:
        raise SystemExit("Set NCL_SRC_ROOT=/mnt/d/Projects/NCL")

    return Path(ncl_root) / "common" / "src" / "fontcap"


def plotchar_state(*, mapped: bool = False, font_number: int = 21, quality: int = 0) -> PlotcharState:
    state = PlotcharState.defaults()
    state.pcseti("TE", 1)
    state.pcseti("QU", quality)
    state.pcseti("FN", font_number)
    state.pcseti("MA", 1 if mapped else 0)
    return state


def real_string(state: PlotcharState, text: str = "ABC") -> str:
    code = chr(state.nfcc) if state.nfcc >= 0 else ":"
    return f"{code}A{code}{text}"


def mapped_contract() -> NclCoordinateTransformDirectionContract:
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


def mapped_viewport() -> NclWindowViewportState:
    return NclWindowViewportState(
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


def assert_status_doc() -> None:
    subprocess.run(
        [sys.executable, "tools/report_python_plotchar_final_stage_closure.py"],
        cwd=ROOT,
        check=True,
    )

    if not DOC.exists():
        raise AssertionError(f"Expected final closure document to exist: {DOC}")

    text = DOC.read_text(encoding="utf-8")
    required = [
        "Python Plotchar Final Stage Closure",
        "Closure scope",
        "What this stage supports",
        "Default behavior that remains guarded",
        "Public opt-in facades",
        "PWRITX/font0/non-fontcap",
        "Boundary rule",
    ]

    missing = [item for item in required if item not in text]
    if missing:
        raise AssertionError("final stage closure document missing sections: " + ", ".join(missing))


def assert_default_mapped_guarded() -> None:
    state = plotchar_state(mapped=True)
    try:
        compute_plchhq_fontcap_text_extent(
            chrs=real_string(state),
            state=state,
            xpos=5.0,
            ypos=150.0,
            size=0.03,
            angle=360.0,
            cntr=-1.0,
            fontcap_dir=fontcap_dir(),
        )
    except PlotcharUnsupportedError:
        return
    raise AssertionError("default IMAP != 0 unexpectedly computed without opt-in backend")


def assert_mapped_opt_in_runs() -> None:
    config = build_ncl_linear_mapped_backend_config(
        window_viewport_state=mapped_viewport(),
        direction_contract=mapped_contract(),
    )
    mapped_state = plotchar_state(mapped=True)

    mapped = compute_plchhq_with_ncl_linear_mapping(
        chrs=real_string(mapped_state),
        state=mapped_state,
        xpos=5.0,
        ypos=150.0,
        size=0.03,
        angle=360.0,
        cntr=-1.0,
        config=config,
        fontcap_dir=fontcap_dir(),
    )

    core_state = plotchar_state(mapped=False)
    core = compute_plchhq_fontcap_text_extent(
        chrs=real_string(core_state),
        state=core_state,
        xpos=0.5,
        ypos=0.5,
        size=0.03,
        angle=360.0,
        cntr=-1.0,
        fontcap_dir=fontcap_dir(),
    )

    assert mapped.text == core.text
    assert mapped.font_number == core.font_number
    assert mapped.glyph_count == core.glyph_count
    assert mapped.metrics.width > core.metrics.width
    assert mapped.metrics.height > core.metrics.height


def assert_default_size_guarded() -> None:
    state = plotchar_state(mapped=False)
    try:
        compute_plchhq_fontcap_text_extent(
            chrs=real_string(state),
            state=state,
            xpos=0.5,
            ypos=0.5,
            size=1.0,
            angle=360.0,
            cntr=-1.0,
            fontcap_dir=fontcap_dir(),
        )
    except PlotcharUnsupportedError as exc:
        assert "SIZE" in str(exc), str(exc)
        return
    raise AssertionError("default SIZE/address path unexpectedly computed without opt-in provider")


def assert_size_opt_in_runs() -> None:
    provider = SourceMappedSizeProvider()
    config = build_size_address_provider_backend_config(scale_provider=provider)
    state = plotchar_state(mapped=False)

    sized = compute_plchhq_with_size_address_provider(
        chrs=real_string(state),
        state=state,
        xpos=0.5,
        ypos=0.5,
        size=1.0,
        angle=360.0,
        cntr=-1.0,
        config=config,
        fontcap_dir=fontcap_dir(),
    )

    core_state = plotchar_state(mapped=False)
    core = compute_plchhq_fontcap_text_extent(
        chrs=real_string(core_state),
        state=core_state,
        xpos=0.5,
        ypos=0.5,
        size=0.03,
        angle=360.0,
        cntr=-1.0,
        fontcap_dir=fontcap_dir(),
    )

    assert sized.text == core.text
    assert sized.font_number == core.font_number
    assert sized.glyph_count == core.glyph_count
    assert abs(sized.metrics.width - core.metrics.width * 10.0) < 1e-12
    assert abs(sized.metrics.height - core.metrics.height * 10.0) < 1e-12


def assert_default_pwritx_guarded() -> None:
    state = plotchar_state(mapped=False, font_number=0, quality=1)
    request = build_pwritx_nonfontcap_request(
        chrs=real_string(state),
        state=state,
        xpos=0.5,
        ypos=0.5,
        size=0.03,
        angle=360.0,
        cntr=-1.0,
    )
    try:
        compute_pwritx_nonfontcap_extent(request)
    except PlotcharUnsupportedError as exc:
        assert "PWRITX/font0/non-fontcap" in str(exc), str(exc)
        return
    raise AssertionError("default PWRITX path unexpectedly computed without opt-in provider")


def assert_pwritx_opt_in_runs() -> None:
    provider = SourceMappedPwritxProvider()
    config = build_pwritx_provider_backend_config(metrics_provider=provider)
    state = plotchar_state(mapped=False, font_number=0, quality=1)

    result = compute_plchhq_with_pwritx_provider(
        chrs=real_string(state),
        state=state,
        xpos=0.5,
        ypos=0.5,
        size=0.03,
        angle=360.0,
        cntr=-1.0,
        config=config,
        fontcap_dir=None,
    )

    assert provider.calls, "PWRITX provider was not called"
    assert result.text == "ABC"
    assert result.font_number == 0
    assert result.glyph_count == 3
    assert result.metrics.dl == 0.81
    assert result.metrics.dr == 0.82
    assert result.metrics.db == 0.83
    assert result.metrics.dt == 0.84


def main() -> None:
    assert_status_doc()
    assert_default_mapped_guarded()
    assert_mapped_opt_in_runs()
    assert_default_size_guarded()
    assert_size_opt_in_runs()
    assert_default_pwritx_guarded()
    assert_pwritx_opt_in_runs()
    print("✅ Python Plotchar final stage closure smoke passed")


if __name__ == "__main__":
    main()
