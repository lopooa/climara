from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PlotcharSourceRequirement:
    source_file: str
    symbol: str
    purpose: str
    status: str


NCL_PLOTCHAR_METRICS_SOURCE_REQUIREMENTS = (
    PlotcharSourceRequirement(
        source_file="ni/src/lib/hlu/TextItem.c",
        symbol="FigureAndSetTextBBInfo",
        purpose=(
            "HLU TextItem measurement context. It sets Plotchar text-extent mode, "
            "calls c_plchhq(0.5, 0.5, real_string, real_size, 360.0, -1.0), "
            "retrieves DL / DR / DT / DB, then applies TextItem justification and rotation."
        ),
        status="caller_context",
    ),
    PlotcharSourceRequirement(
        source_file="ncarg2d/src/libncarg/plotcharC/c_plchhq.c",
        symbol="c_plchhq",
        purpose=(
            "C binding used by HLU TextItem.c. It forwards xpos, ypos, chrs, size, "
            "angd, cntr, and Fortran string length into PLCHHQ."
        ),
        status="required_before_live_plotchar_metrics_provider",
    ),
    PlotcharSourceRequirement(
        source_file="ncarg2d/src/libncarg/plotcharC/c_pcgetr.c",
        symbol="c_pcgetr",
        purpose=(
            "C binding used by HLU TextItem.c to retrieve DL / DR / DB / DT after c_plchhq."
        ),
        status="required_before_live_plotchar_metrics_provider",
    ),
    PlotcharSourceRequirement(
        source_file="ncarg2d/src/libncarg/plotcharC/c_pcseti.c",
        symbol="void c_pcseti",
        purpose=(
            "C binding used by HLU TextItem.c to set Plotchar integer state, "
            "especially TE=1, QU, and FN before measurement."
        ),
        status="required_before_live_plotchar_metrics_provider",
    ),
    PlotcharSourceRequirement(
        source_file="ncarg2d/src/libncarg/plotcharC/c_pcsetr.c",
        symbol="void c_pcsetr",
        purpose=(
            "C binding used by HLU TextItem.c to set Plotchar real state, "
            "especially CS, PH, and PW before measurement."
        ),
        status="required_before_live_plotchar_metrics_provider",
    ),
    PlotcharSourceRequirement(
        source_file="ncarg2d/src/libncarg/plotcharC/c_pcsetc.c",
        symbol="void c_pcsetc",
        purpose=(
            "C binding used by HLU TextItem.c to set Plotchar character state, "
            "especially FC before measurement."
        ),
        status="required_before_live_plotchar_metrics_provider",
    ),
    PlotcharSourceRequirement(
        source_file="ncarg2d/src/libncarg/plotchar/pcseti.f",
        symbol="SUBROUTINE PCSETI",
        purpose=(
            "Sets integer Plotchar parameters. TE maps to ITEF, QU maps to IQUF, "
            "and FN maps to NODF before PLCHHQ measurement."
        ),
        status="required_before_live_plotchar_metrics_provider",
    ),
    PlotcharSourceRequirement(
        source_file="ncarg2d/src/libncarg/plotchar/pcsetc.f",
        symbol="SUBROUTINE PCSETC",
        purpose=(
            "Sets character Plotchar parameters. FC maps to NFCC, the function-code "
            "signal character used while parsing CHRS."
        ),
        status="required_before_live_plotchar_metrics_provider",
    ),
    PlotcharSourceRequirement(
        source_file="ncarg2d/src/libncarg/plotchar/plchhq.f",
        symbol="SUBROUTINE PLCHHQ",
        purpose=(
            "High-quality Plotchar routine that computes DSTL / DSTR / DSTB / DSTT "
            "from character digitization, size, spacing, orientation, centering, and function codes."
        ),
        status="required_before_live_plotchar_metrics_provider",
    ),
    PlotcharSourceRequirement(
        source_file="ncarg2d/src/libncarg/plotchar/pcgetr.f",
        symbol="SUBROUTINE PCGETR",
        purpose=(
            "Retrieves real Plotchar parameters. DB maps to DSTB, DL maps to DSTL, "
            "DR maps to DSTR, and DT maps to DSTT."
        ),
        status="required_before_live_plotchar_metrics_provider",
    ),
    PlotcharSourceRequirement(
        source_file="ncarg2d/src/libncarg/plotchar/pcsetr.f",
        symbol="SUBROUTINE PCSETR",
        purpose=(
            "Sets real Plotchar parameters such as CS, PH, PW, and TE. Needed before "
            "implementing any live provider that mutates Plotchar state."
        ),
        status="required_before_live_plotchar_metrics_provider",
    ),
    PlotcharSourceRequirement(
        source_file="ncarg2d/src/libncarg/plotchar/pcrset.f",
        symbol="SUBROUTINE PCRSET",
        purpose=(
            "Resets Plotchar parameters. Needed to understand defaults and avoid leaking "
            "Plotchar state between TextItem measurements."
        ),
        status="required_before_live_plotchar_metrics_provider",
    ),
    PlotcharSourceRequirement(
        source_file="ncarg2d/src/libncarg/plotchar/pcblda.f",
        symbol='ITEF is the "compute-text-extent-vectors" flag',
        purpose=(
            "Block-data defaults and comments define TE / ITEF: when set, PLCHHQ calls "
            "with ANGD=360 compute DSTL / DSTR / DSTB / DSTT for later PCGETR retrieval."
        ),
        status="required_before_live_plotchar_metrics_provider",
    ),
    PlotcharSourceRequirement(
        source_file="ncarg2d/src/examplesC/plotchar/c_epltch.c",
        symbol='c_pcgetr ("DL - DISTANCE LEFT  ",',
        purpose=(
            "Example showing canonical DL / DR / DB / DT retrieval. Useful as a behavioral "
            "reference, not as implementation source."
        ),
        status="reference_example",
    ),
)


def required_plotchar_source_files() -> tuple[str, ...]:
    return tuple(
        sorted({item.source_file for item in NCL_PLOTCHAR_METRICS_SOURCE_REQUIREMENTS})
    )


def plotchar_source_symbols() -> tuple[str, ...]:
    return tuple(item.symbol for item in NCL_PLOTCHAR_METRICS_SOURCE_REQUIREMENTS)


def plotchar_source_requirements_report() -> str:
    lines = [
        "NCL Plotchar metrics source requirements",
        "=" * 40,
        "",
        "Required source files:",
    ]

    for source_file in required_plotchar_source_files():
        lines.append(f"- {source_file}")

    lines.append("")
    lines.append("Required source symbols:")

    for item in NCL_PLOTCHAR_METRICS_SOURCE_REQUIREMENTS:
        lines.append("")
        lines.append(f"[{item.symbol}]")
        lines.append(f"  source_file: {item.source_file}")
        lines.append(f"  status: {item.status}")
        lines.append(f"  purpose: {item.purpose}")

    lines.append("")
    lines.append("Rule:")
    lines.append(
        "Do not implement live Plotchar metrics from fixed-width text heuristics. "
        "The live provider must be mapped from TextItem.c -> PLCHHQ -> PCGETR semantics, "
        "especially TextItem's ANGD=360 measurement call and DSTL / DSTR / DSTB / DSTT."
    )

    return "\n".join(lines)


__all__ = [
    "NCL_PLOTCHAR_METRICS_SOURCE_REQUIREMENTS",
    "PlotcharSourceRequirement",
    "plotchar_source_requirements_report",
    "plotchar_source_symbols",
    "required_plotchar_source_files",
]
