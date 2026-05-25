import subprocess
import sys


SMOKES = [
    "tools/smoke_svg_labelbar_textitem_data_attrs.py",
    "tools/smoke_labelbar_label_textitem_contract.py",
    "tools/smoke_labelbar_label_textitem_font_resources.py",
    "tools/smoke_labelbar_label_font_height_svg.py",
    "tools/smoke_labelbar_label_textitem_real_string_semantics.py",
    "tools/smoke_labelbar_label_direction_guard.py",
    "tools/smoke_labelbar_svg_text_contract.py",
    "tools/smoke_labelbar_label_plotchar_guard.py",
    "tools/smoke_svg_labelbar_title_plotchar_guard.py",
    "tools/smoke_svg_labelbar_title_down_direction_guard.py",
    "tools/smoke_svg_labelbar_title_angle_render.py",
    "tools/smoke_svg_labelbar_title_render.py",
    "tools/smoke_svg_labelbar_draw_order.py",
    "tools/smoke_panel_shared_labelbar_svg.py",
]


def main():
    for smoke in SMOKES:
        print(f"RUN {smoke}")
        subprocess.run([sys.executable, smoke], check=True)

    print("✅ LabelBar TextItem SVG bundle passed")


if __name__ == "__main__":
    main()
