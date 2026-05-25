import subprocess
import sys
from pathlib import Path


SMOKES = [
    "tools/smoke_text_bbox_guard.py",
    "tools/smoke_ncl_text_bbox_source_map_doc.py",
    "tools/smoke_plotchar_metrics_guard.py",
    "tools/smoke_text_bbox_plotchar_bridge.py",
    "tools/smoke_text_bbox_not_used_by_render_path.py",
    "tools/smoke_text_bbox_coordinate_space_contract.py",
    "tools/smoke_text_bbox_union_contract.py",
    "tools/smoke_multitext_bbox_request_builder.py",
    "tools/smoke_multitext_child_bbox_aggregation.py",
    "tools/smoke_labelbar_text_bbox_request_contract.py",
    "tools/smoke_labelbar_text_bbox_request_builder.py",
    "tools/smoke_labelbar_text_bbox_builder_not_used.py",
    "tools/smoke_labelbar_adjust_geometry_guard.py",
    "tools/smoke_labelbar_adjust_geometry_not_used.py",
]


def main():
    root = Path.cwd()
    failures = []

    for smoke in SMOKES:
        path = root / smoke
        if not path.exists():
            print(f"SKIP missing {smoke}", flush=True)
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
        print("Failed TextBBox / LabelBar AdjustGeometry smokes:")
        for smoke in failures:
            print(f"  - {smoke}")
        raise SystemExit(1)

    print("✅ TextBBox / LabelBar AdjustGeometry smoke bundle passed")


if __name__ == "__main__":
    main()
