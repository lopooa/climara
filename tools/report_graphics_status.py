from climara.graphics._capabilities import graphics_capabilities
from climara.graphics._labelbar_adjust import has_labelbar_adjust_geometry_engine
from climara.graphics._plotchar_metrics import has_plotchar_metrics_engine
from climara.graphics._text_bbox import has_text_bbox_engine


DONE = [
    "no Matplotlib runtime in src/climara",
    "no Cartopy runtime dependency in src/climara / pyproject check",
    "SVG backend path",

    "shared TextItem semantics helper",
    "shared MultiText semantics helper",
    "LabelBar title TextItem semantics",
    "LabelBar label MultiText/TextItem semantics",

    "TextBBox request / coordinate-space / union contracts",
    "MultiText child bbox aggregation contract",
    "LabelBar text bbox request builder",

    "Plotchar metrics request boundary",
    "TextBBox request to Plotchar metrics bridge",
    "LabelBar Plotchar metrics request builder",

    "TextItem bbox semantics from supplied Plotchar metrics",
    "MultiText bbox semantics from supplied child Plotchar metrics",
    "LabelBar text bbox semantics from supplied title/label Plotchar metrics",

    "LabelBar AdjustGeometry request bridge from supplied text bboxes",
    "LabelBar AdjustGeometry supplied-bbox box semantics",
    "LabelBar AdjustGeometry perimeter / justification semantics from supplied bboxes",
    "LabelBar AdjustGeometry write-back semantics from supplied bboxes",
    "LabelBar AdjustGeometry supplied-bbox execution result",
    "LabelBar AdjustGeometry materialized snapshot",
    "LabelBar AdjustGeometry applied LabelBarGeometry snapshot",
    "LabelBar supplied-metrics AdjustGeometry pipeline",

    "explicit adjusted LabelBar SVG primitive adapter",
    "explicit adjusted LabelBar SVG file export",
]

NOT_DONE = [
    "NCL Plotchar parser",
    "NCL Plotchar DL / DR / DB / DT metrics engine",
    "TextItem bbox engine using live Plotchar metrics",
    "MultiText bbox engine using live child TextItem bbox results",
    "NCL font metrics",
    "NhlDOWN / Down visual text rendering",
    "full LabelBar AutoManage parity",
    "default renderer integration for adjusted LabelBar geometry",
    "default layout integration for adjusted LabelBar geometry",
]


def main():
    caps = graphics_capabilities()

    print("climara graphics status")
    print("=" * 28)
    print()

    print("Capabilities")
    print("-" * 12)
    for name, value in caps.__dict__.items():
        print(f"{name}: {value}")

    print()
    print("Completed / guarded foundation")
    print("-" * 30)
    for item in DONE:
        print(f"✅ {item}")

    print()
    print("Not implemented yet")
    print("-" * 19)
    for item in NOT_DONE:
        print(f"❌ {item}")

    print()
    print("Important guards")
    print("-" * 16)
    print(f"text_bbox_engine: {has_text_bbox_engine()}")
    print(f"plotchar_metrics_engine: {has_plotchar_metrics_engine()}")
    print(f"labelbar_adjust_geometry_engine: {has_labelbar_adjust_geometry_engine()}")
    print("Note: labelbar_adjust_geometry_engine=False means no live/default engine.")
    print("The supplied-bbox AdjustGeometry execution path is explicit and opt-in.")

    print()
    print("Recommended checks")
    print("-" * 18)
    print("PYTHONPATH=src python tools/run_core_smokes.py")
    print("PYTHONPATH=src python tools/run_labelbar_textitem_smokes.py")
    print("PYTHONPATH=src python tools/run_text_bbox_smokes.py")


if __name__ == "__main__":
    main()
