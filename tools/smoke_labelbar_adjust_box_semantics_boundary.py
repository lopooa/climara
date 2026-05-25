from climara.graphics._capabilities import graphics_capabilities
from climara.graphics._labelbar_adjust import has_labelbar_adjust_geometry_engine
from climara.graphics._plotchar_metrics import has_plotchar_metrics_engine
from climara.graphics._text_bbox import has_text_bbox_engine


def main():
    caps = graphics_capabilities()

    assert caps.labelbar_adjust_box_semantics_from_supplied_bboxes is True

    assert caps.plotchar_metrics_engine is False
    assert caps.text_bbox_engine is False
    assert caps.labelbar_adjust_geometry_engine is False

    assert has_plotchar_metrics_engine() is False
    assert has_text_bbox_engine() is False
    assert has_labelbar_adjust_geometry_engine() is False

    print("✅ LabelBar AdjustGeometry supplied-bbox box semantics boundary smoke passed")


if __name__ == "__main__":
    main()
