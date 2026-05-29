from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


SMOKES = [
    "examples/demo_plotchar_r_roman_command.py",
    "examples/demo_plotchar_ul_case_metrics.py",
    "examples/demo_plotchar_pik_size_level_metrics.py",
    "examples/demo_plotchar_hvxyz_c_metrics.py",
    "examples/demo_plotchar_size_address_equivalence_metrics.py",

    "examples/demo_plotchar_pwritx_facade_boundary.py",
    "examples/demo_plotchar_pwritx_svg_draw_guard.py",
    "examples/demo_plotchar_pwritx_draw_provider_seam.py",

    "examples/demo_plotchar_greek_draw_provider_seam.py",
    "examples/demo_plotchar_legacy_digitization_offsets.py",
    "examples/demo_plotchar_legacy_digitization_trace.py",
    "examples/demo_plotchar_greek_legacy_trace_draw_seam.py",
    "examples/demo_plotchar_legacy_data_provider_seam.py",
    "examples/demo_plotchar_legacy_idda_decoder_seam.py",
    "examples/demo_plotchar_legacy_idda_raw_contract.py",
    "examples/demo_plotchar_legacy_glyph_output_contract.py",
    "examples/demo_plotchar_legacy_pcfred_provider_seam.py",
    "examples/demo_plotchar_legacy_pcfred_file_backend_guard.py",

    "examples/demo_plotchar_textitem_provider_seams.py",
    "examples/demo_plotchar_textitem_provider_guard_boundary.py",
    "examples/demo_plotchar_textitem_greek_data_backed_decoder_seam.py",
    "examples/demo_plotchar_textitem_greek_data_backed_indices.py",
    "examples/demo_plotchar_textitem_greek_decoder_contract_regression.py",

    "examples/demo_plotchar_mapped_draw_provider_seam.py",
    "examples/demo_plotchar_textitem_mapped_provider_seam.py",

    "examples/demo_plotchar_draw_provider_output_contract.py",
    "examples/demo_plotchar_draw_provider_output_contract_all.py",
]


CORE_FILES = [
    "src/climara/graphics/_plotchar_svg_runtime.py",
    "src/climara/graphics/_render_svg.py",

    "src/climara/graphics/_plotchar_size_address_provider.py",

    "src/climara/graphics/_plotchar_greek_draw_provider.py",
    "src/climara/graphics/_plotchar_pwritx_draw_provider.py",
    "src/climara/graphics/_plotchar_mapped_draw_provider.py",
    "src/climara/graphics/_plotchar_draw_provider_contract.py",

    "src/climara/graphics/_plotchar_legacy_digitization.py",
    "src/climara/graphics/_plotchar_legacy_digitization_trace.py",
    "src/climara/graphics/_plotchar_legacy_glyph_provider.py",
    "src/climara/graphics/_plotchar_legacy_glyph_contract.py",
    "src/climara/graphics/_plotchar_legacy_trace_draw.py",

    "src/climara/graphics/_plotchar_legacy_data_provider.py",
    "src/climara/graphics/_plotchar_legacy_data_backed_glyph.py",
    "src/climara/graphics/_plotchar_legacy_idda_decoder.py",
    "src/climara/graphics/_plotchar_legacy_idda_contract.py",
    "src/climara/graphics/_plotchar_legacy_pcfred_provider.py",
    "src/climara/graphics/_plotchar_legacy_pcfred_file_backend.py",
]


def run(cmd: list[str]) -> None:
    print()
    print("+", " ".join(cmd))
    subprocess.run(cmd, cwd=ROOT, check=True, env=os.environ.copy())


def main() -> None:
    missing = [path for path in CORE_FILES + SMOKES if not (ROOT / path).exists()]

    if missing:
        print("Missing required files:")
        for path in missing:
            print(f"  {path}")
        raise SystemExit(1)

    run([sys.executable, "-m", "py_compile", *CORE_FILES, *SMOKES])

    for script in SMOKES:
        run([sys.executable, script])

    print()
    print("✅ Plotchar provider/contract targeted smokes passed")


if __name__ == "__main__":
    main()
