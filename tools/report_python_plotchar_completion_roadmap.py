from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "python_plotchar_completion_roadmap.md"


CURRENT_ARTIFACTS = [
    "src/climara/graphics/_plotchar_state.py",
    "src/climara/graphics/_plotchar_fontcap.py",
    "src/climara/graphics/_plotchar_function_code.py",
    "src/climara/graphics/_plotchar_plchhq_extent.py",
    "src/climara/graphics/_plotchar_mapped_coordinate.py",
    "src/climara/graphics/_plotchar_mapped_runtime_strategy.py",
    "src/climara/graphics/_plotchar_mapped_transform_ncl.py",
    "src/climara/graphics/_plotchar_mapped_opt_in.py",
    "src/climara/graphics/mapped_plotchar.py",
    "src/climara/graphics/_plotchar_size_address_unit.py",
    "src/climara/graphics/_plotchar_size_runtime_strategy.py",
    "src/climara/graphics/_plotchar_size_address_provider.py",
    "src/climara/graphics/size_address_plotchar.py",
    "docs/python_plotchar_stage_status.md",
    "docs/python_plotchar_mapped_backend_status.md",
    "docs/python_plotchar_size_address_provider_backend_status.md",
]


def exists(path: str) -> bool:
    return (ROOT / path).exists()


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)

    lines = []
    lines.append("# Python Plotchar Completion Roadmap")
    lines.append("")
    lines.append("## Honest status")
    lines.append("")
    lines.append("The current work is close to a stage-level closure for the TextItem/fontcap Plotchar engine.")
    lines.append("")
    lines.append("It is not close to full NCL PLCHHQ parity. Full parity would require additional branches such as PWRITX/font0, non-fontcap paths, full address-unit SIZE semantics, log scaling, map/projection transforms, and more function-code commands.")
    lines.append("")
    lines.append("## Current stage artifacts")
    lines.append("")
    for item in CURRENT_ARTIFACTS:
        mark = "x" if exists(item) else " "
        lines.append(f"- [{mark}] `{item}`")
    lines.append("")
    lines.append("## What can be considered near stage-complete")
    lines.append("")
    lines.append("- TextItem measurement boundary.")
    lines.append("- Python high-quality fontcap mainline for the audited subset.")
    lines.append("- Guarded unsupported branches.")
    lines.append("- Mapped-coordinate explicit opt-in linear window/viewport backend.")
    lines.append("- SIZE/address explicit provider-backed facade.")
    lines.append("- Public facades for opt-in experimental branches.")
    lines.append("- Smoke coverage and project boundary checks.")
    lines.append("")
    lines.append("## Remaining work for current stage closure")
    lines.append("")
    lines.append("### 1. Update final stage status document")
    lines.append("")
    lines.append("Merge the latest SIZE/address provider-backed facade into `docs/python_plotchar_stage_status.md`, so the stage report reflects both mapped and SIZE opt-in branches.")
    lines.append("")
    lines.append("### 2. Add one final aggregate smoke")
    lines.append("")
    lines.append("Create a single smoke that checks:")
    lines.append("")
    lines.append("- default mapped path remains guarded")
    lines.append("- explicit mapped opt-in path works")
    lines.append("- default SIZE/address path remains guarded")
    lines.append("- explicit SIZE/address provider-backed path works")
    lines.append("- no Matplotlib / external render dependency checks pass")
    lines.append("")
    lines.append("### 3. Decide next branch")
    lines.append("")
    lines.append("After current stage closure, choose one:")
    lines.append("")
    lines.append("- PWRITX/font0/non-fontcap branch")
    lines.append("- real SIZE/address formula implementation after manual source mapping")
    lines.append("- function-code remaining commands")
    lines.append("- integration into higher-level TextItem/MultiText/LabelBar examples")
    lines.append("")
    lines.append("## Remaining work for full NCL PLCHHQ parity")
    lines.append("")
    lines.append("This is much larger and should not be promised as nearly complete:")
    lines.append("")
    lines.append("- full PWRITX/font0 branch")
    lines.append("- medium/low/workstation quality branches")
    lines.append("- complete SIZE/address-unit semantics")
    lines.append("- log coordinate transforms")
    lines.append("- map/projection transforms")
    lines.append("- complete inline function-code command set")
    lines.append("- full PLCHHQ state mutation parity")
    lines.append("- exact PCGETR/PCSETR side effects")
    lines.append("- exact rotation and justification behavior across all branches")
    lines.append("")
    lines.append("## Practical answer")
    lines.append("")
    lines.append("For a defensible current milestone: about 2 to 4 larger stages remain.")
    lines.append("")
    lines.append("For full NCL PLCHHQ parity: many more stages remain and it should be treated as a long-term project.")
    lines.append("")
    lines.append("## Recommended next action")
    lines.append("")
    lines.append("Close the current TextItem/fontcap milestone first by updating the stage report and adding a final aggregate smoke. Then start the next branch separately.")
    lines.append("")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
