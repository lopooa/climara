import subprocess
import sys
from pathlib import Path


SMOKES = [
    "tools/smoke_text_semantics.py",
    "tools/smoke_text_semantics_labelbar_bridge.py",
    "tools/smoke_text_semantics_shared_delegation.py",
    "tools/smoke_labelbar_title_object_semantics.py",
    "tools/smoke_labelbar_title_geometry_semantics.py",
    "tools/smoke_labelbar_title_text_geometry_semantics.py",
    "tools/smoke_labelbar_title_text_item_semantics.py",
    "tools/smoke_labelbar_title_textitem_real_string_semantics.py",
    "tools/smoke_labelbar_title_textitem_quality_semantics.py",
    "tools/smoke_labelbar_title_svg_adapter_semantics.py",
    "tools/smoke_labelbar_title_svg_adapter_real_string_semantics.py",
    "tools/smoke_svg_labelbar_title_render.py",
    "tools/smoke_svg_labelbar_title_angle_render.py",
    "tools/smoke_svg_labelbar_title_down_direction_guard.py",
    "tools/smoke_svg_labelbar_title_plotchar_guard.py",
    "tools/smoke_svg_labelbar_draw_order.py",
    "tools/smoke_labelbar_label_shared_text_semantics.py",
    "tools/smoke_labelbar_label_plotchar_guard.py",
    "tools/smoke_labelbar_label_direction_guard.py",
    "tools/smoke_labelbar_label_textitem_real_string_semantics.py",
    "tools/smoke_labelbar_label_font_height_svg.py",
    "tools/smoke_labelbar_label_textitem_font_resources.py",
    "tools/smoke_labelbar_label_font_color_adapter_svg.py",
    "tools/smoke_svg_labelbar_label_angle_color_render.py",
    "tools/smoke_labelbar_label_textitem_contract.py",
    "tools/smoke_labelbar_svg_text_contract.py",
    "tools/smoke_svg_labelbar_textitem_data_attrs.py",
    "tools/smoke_panel_shared_labelbar_svg.py",
]


def main():
    root = Path.cwd()
    failures = []

    for smoke in SMOKES:
        path = root / smoke
        if not path.exists():
            print(f"SKIP missing {smoke}")
            continue

        print(f"RUN {smoke}", flush=True)
        result = subprocess.run(
            [sys.executable, smoke],
            cwd=root,
            text=True,
        )

        if result.returncode != 0:
            failures.append(smoke)
            print(f"FAIL {smoke}", flush=True)
        else:
            print(f"PASS {smoke}", flush=True)

    if failures:
        print()
        print("Failed LabelBar TextItem smokes:")
        for smoke in failures:
            print(f"  - {smoke}")
        raise SystemExit(1)

    print("✅ LabelBar TextItem smoke bundle passed")


if __name__ == "__main__":
    main()
