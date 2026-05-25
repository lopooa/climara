from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NclSourceRequirement:
    source_file: str
    component: str
    symbol: str
    purpose: str
    status: str


NCL_TEXT_BBOX_SOURCE_REQUIREMENTS = (
    NclSourceRequirement(
        source_file="ni/src/lib/hlu/TextItem.c",
        component="TextItem",
        symbol="FigureAndSetTextBBInfo",
        purpose=(
            "Compute TextItem bounding-box information from Plotchar-derived "
            "DL / DR / DB / DT extents, rotation, justification, and real_string."
        ),
        status="required_before_text_bbox_engine",
    ),
    NclSourceRequirement(
        source_file="ni/src/lib/hlu/TextItem.c",
        component="TextItem",
        symbol="TextItemDraw",
        purpose=(
            "Clarify how real_string, font size, angle, justification, and "
            "Plotchar draw calls are used before bbox semantics are implemented."
        ),
        status="required_before_text_bbox_engine",
    ),
    NclSourceRequirement(
        source_file="ni/src/lib/hlu/MultiText.c",
        component="MultiText",
        symbol="GetMaxTextLength",
        purpose=(
            "Map how MultiText derives maximum text length and text extent "
            "information from child TextItem semantics."
        ),
        status="required_before_multitext_bbox_engine",
    ),
    NclSourceRequirement(
        source_file="ni/src/lib/hlu/MultiText.c",
        component="MultiText",
        symbol="SetDrawFlags",
        purpose=(
            "Map function-code-aware character counting, max extent, zero "
            "fraction logic, and draw flag behavior."
        ),
        status="required_before_multitext_bbox_engine",
    ),
    NclSourceRequirement(
        source_file="ni/src/lib/hlu/MultiText.c",
        component="MultiText",
        symbol="child TextItem geometry aggregation",
        purpose=(
            "Map how child TextItem NhlNvpXF / NhlNvpYF / NhlNvpWidthF / "
            "NhlNvpHeightF values are merged into a MultiText bounding box."
        ),
        status="partially_guarded_by_current_union_contract",
    ),
    NclSourceRequirement(
        source_file="ni/src/lib/hlu/LabelBar.c",
        component="LabelBar",
        symbol="SetTitle",
        purpose=(
            "Map how the title TextItem is created, how NhlGetBB is used, "
            "and how title extents feed into LabelBar geometry."
        ),
        status="required_before_labelbar_title_bbox_feedback",
    ),
    NclSourceRequirement(
        source_file="ni/src/lib/hlu/LabelBar.c",
        component="LabelBar",
        symbol="SetLabels",
        purpose=(
            "Map label strings, label child objects, label positions, label "
            "resource transfer, and label extent computation."
        ),
        status="required_before_labelbar_label_bbox_feedback",
    ),
    NclSourceRequirement(
        source_file="ni/src/lib/hlu/LabelBar.c",
        component="LabelBar",
        symbol="AdjustGeometry",
        purpose=(
            "Map how title and label bounding boxes expand or reposition "
            "the LabelBar under AutoManage and non-AutoManage modes."
        ),
        status="required_before_labelbar_adjust_geometry_engine",
    ),
)


def required_ncl_source_files() -> tuple[str, ...]:
    return tuple(
        sorted({requirement.source_file for requirement in NCL_TEXT_BBOX_SOURCE_REQUIREMENTS})
    )


def requirements_by_component(component: str) -> tuple[NclSourceRequirement, ...]:
    key = str(component).strip().lower()
    return tuple(
        requirement
        for requirement in NCL_TEXT_BBOX_SOURCE_REQUIREMENTS
        if requirement.component.lower() == key
    )


def ncl_text_bbox_requirements_report() -> str:
    lines = [
        "NCL TextItem / MultiText / LabelBar bbox source requirements",
        "=" * 62,
        "",
        "Required source files:",
    ]

    for source_file in required_ncl_source_files():
        lines.append(f"- {source_file}")

    lines.append("")
    lines.append("Required source symbols:")

    for requirement in NCL_TEXT_BBOX_SOURCE_REQUIREMENTS:
        lines.append("")
        lines.append(f"[{requirement.component}] {requirement.symbol}")
        lines.append(f"  source_file: {requirement.source_file}")
        lines.append(f"  status: {requirement.status}")
        lines.append(f"  purpose: {requirement.purpose}")

    lines.append("")
    lines.append("Rule:")
    lines.append(
        "Do not implement TextItem bbox, MultiText bbox, Plotchar metrics, "
        "LabelBar AutoManage, or LabelBar AdjustGeometry without first mapping "
        "the complete source contexts above."
    )

    return "\n".join(lines)


__all__ = [
    "NCL_TEXT_BBOX_SOURCE_REQUIREMENTS",
    "NclSourceRequirement",
    "ncl_text_bbox_requirements_report",
    "required_ncl_source_files",
    "requirements_by_component",
]
