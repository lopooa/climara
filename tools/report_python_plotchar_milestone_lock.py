from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "python_plotchar_milestone_lock.md"

LOCKED_SMOKES = [
    "tools/run_python_plotchar_milestone_smokes.py",
    "tools/smoke_python_plotchar_final_stage_closure.py",
    "tools/smoke_python_plotchar_milestone_manifest.py",
    "tools/smoke_python_plotchar_function_code_remaining_roadmap.py",
    "tools/smoke_python_plotchar_mapped_public_facade.py",
    "tools/smoke_python_plotchar_size_address_public_facade.py",
    "tools/smoke_python_plotchar_pwritx_public_facade.py",
    "tools/smoke_python_plotchar_measurement_contract_guard.py",
    "tools/smoke_python_mainline_project_boundary.py",
]

LOCKED_DOCS = [
    "docs/python_plotchar_final_stage_closure.md",
    "docs/python_plotchar_milestone_manifest.md",
    "docs/python_plotchar_stage_status.md",
    "docs/python_plotchar_completion_roadmap.md",
    "docs/python_plotchar_function_code_remaining_roadmap.md",
    "docs/python_plotchar_mapped_backend_status.md",
    "docs/python_plotchar_size_address_provider_backend_status.md",
    "docs/python_plotchar_pwritx_provider_backend_status.md",
]

LOCKED_FACADES = [
    "src/climara/graphics/mapped_plotchar.py",
    "src/climara/graphics/size_address_plotchar.py",
    "src/climara/graphics/pwritx_plotchar.py",
]


def exists(path: str) -> bool:
    return (ROOT / path).exists()


def checklist(items: list[str]) -> list[str]:
    return [f"- [{'x' if exists(item) else ' '}] `{item}`" for item in items]


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)

    missing = [item for item in LOCKED_SMOKES + LOCKED_DOCS + LOCKED_FACADES if not exists(item)]

    lines = []
    lines.append("# Python Plotchar Milestone Lock")
    lines.append("")
    lines.append("## Purpose")
    lines.append("")
    lines.append("This lock document records the short milestone smoke suite for the current Python Plotchar stage.")
    lines.append("")
    lines.append("It is intended for quick verification before committing or before starting a new branch.")
    lines.append("")
    lines.append("## Locked milestone behavior")
    lines.append("")
    lines.append("- Default TextItem/fontcap audited subset remains available.")
    lines.append("- Default mapped-coordinate path remains guarded.")
    lines.append("- Mapped-coordinate opt-in facade remains available.")
    lines.append("- Default SIZE/address-unit path remains guarded.")
    lines.append("- SIZE/address provider-backed facade remains available.")
    lines.append("- Default PWRITX/font0/non-fontcap path remains guarded.")
    lines.append("- PWRITX provider-backed facade remains available.")
    lines.append("- Remaining function-code commands remain documented and guarded.")
    lines.append("")
    lines.append("## Locked smoke entry")
    lines.append("")
    lines.append("```bash")
    lines.append("PYTHONPATH=src python tools/run_python_plotchar_milestone_smokes.py")
    lines.append("```")
    lines.append("")
    lines.append("## Smoke scripts")
    lines.append("")
    lines.extend(checklist(LOCKED_SMOKES))
    lines.append("")
    lines.append("## Documents")
    lines.append("")
    lines.extend(checklist(LOCKED_DOCS))
    lines.append("")
    lines.append("## Public opt-in facades")
    lines.append("")
    lines.extend(checklist(LOCKED_FACADES))
    lines.append("")
    lines.append("## Missing artifacts")
    lines.append("")
    if missing:
        for item in missing:
            lines.append(f"- `{item}`")
    else:
        lines.append("No locked milestone artifacts are missing.")
    lines.append("")
    lines.append("## Boundary rule")
    lines.append("")
    lines.append("This lock is a stage-level verification aid, not a full NCL PLCHHQ parity claim.")
    lines.append("")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT}")

    if missing:
        print("Milestone lock status: missing artifacts detected")
        for item in missing:
            print(f"missing: {item}")
    else:
        print("Milestone lock status: required artifacts present")


if __name__ == "__main__":
    main()
