from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from climara.graphics._plotchar_metrics import has_plotchar_metrics_engine
from climara.graphics._plotchar_python_live_engine import (
    python_plotchar_mainline_status,
)
from climara.graphics._text_bbox import has_text_bbox_engine


@dataclass(frozen=True)
class GraphicsMainlineStatus:
    python_plotchar_available: bool
    plotchar_metrics_engine: bool
    text_bbox_engine: bool
    renderer_adjusted_labelbar_gate: bool
    report: str


def renderer_adjusted_labelbar_gate_is_present() -> bool:
    path = Path("src/climara/graphics/_render_svg.py")
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8", errors="ignore")
    return "adjusted-python-plotchar" in text


def collect_graphics_mainline_status() -> GraphicsMainlineStatus:
    status = python_plotchar_mainline_status()
    return GraphicsMainlineStatus(
        python_plotchar_available=bool(status.available),
        plotchar_metrics_engine=bool(has_plotchar_metrics_engine()),
        text_bbox_engine=bool(has_text_bbox_engine()),
        renderer_adjusted_labelbar_gate=renderer_adjusted_labelbar_gate_is_present(),
        report=status.report,
    )


def build_status_report() -> str:
    status = collect_graphics_mainline_status()
    lines = [
        "climara Python Plotchar mainline status",
        "=" * 44,
        "",
        f"Python Plotchar mainline available: {status.python_plotchar_available}",
        f"has_plotchar_metrics_engine(): {status.plotchar_metrics_engine}",
        f"has_text_bbox_engine(): {status.text_bbox_engine}",
        f"Renderer adjusted LabelBar gate present: {status.renderer_adjusted_labelbar_gate}",
        "",
        "Current mainline:",
        "- NCL source is the semantic authority.",
        "- climara runtime mainline is Python implementation, not NCL dynamic-library dependency.",
        "- Optional ctypes / real-library tooling is validation-only, not the core route.",
        "",
        "Completed audited Python path:",
        "- Plotchar state model for TextItem measurement-related PCSETI / PCSETR / PCSETC / PCGETR state.",
        "- Fontcap-backed PLCHHQ extent subset for audited TextItem measurement calls.",
        "- Default Plotchar metrics engine for the audited subset when NCL fontcap source data are available.",
        "- Default TextItem bbox engine for the audited subset.",
        "- Default MultiText bbox aggregation from audited child TextItem bboxes.",
        "- Default LabelBar renderer gate for adjusted LabelBar SVG primitives.",
        "",
        "Still guarded and not claimed complete:",
        "- Down-text.",
        "- Inline Plotchar function-code commands beyond audited literal/function-code prefix handling.",
        "- Subscript / superscript.",
        "- Mapped coordinates / IMAP branches.",
        "- PWRITX non-fontcap branch.",
        "- Medium / Low / Workstation quality branches unless explicitly source-mapped later.",
        "- SIZE >= 1 or SIZE <= 0 address-unit semantics.",
        "- Full NCL PLCHHQ parity.",
        "",
        "No-shortcut rule:",
        "- No fixed-width text metrics.",
        "- No character-count width estimates.",
        "- No SVG/browser text metrics.",
        "- No visual adjustment fallback.",
        "- Unsupported branches must raise guarded errors.",
        "",
        "Availability report:",
        status.report,
    ]
    return "\n".join(lines)


def main() -> None:
    print(build_status_report())


if __name__ == "__main__":
    main()
