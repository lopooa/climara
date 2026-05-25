from climara.graphics._capabilities import graphics_capabilities


def main():
    caps = graphics_capabilities()

    assert caps.no_mpl_runtime is True
    assert caps.no_cartopy_runtime is True
    assert caps.svg_backend is True

    assert caps.text_item_semantics is True
    assert caps.multitext_semantics is True

    assert caps.text_bbox_requests is True
    assert caps.labelbar_text_bbox_requests is True
    assert caps.plotchar_metrics_requests is True
    assert caps.labelbar_plotchar_metrics_requests is True

    assert caps.text_bbox_from_supplied_plotchar_metrics is True
    assert caps.multitext_bbox_from_supplied_plotchar_metrics is True
    assert caps.labelbar_bbox_from_supplied_plotchar_metrics is True

    assert caps.labelbar_adjust_request_from_supplied_bboxes is True
    assert caps.labelbar_adjust_box_semantics_from_supplied_bboxes is True
    assert caps.labelbar_adjust_perimeter_semantics_from_supplied_bboxes is True
    assert caps.labelbar_adjust_writeback_semantics_from_supplied_bboxes is True
    assert caps.labelbar_adjust_execution_from_supplied_bboxes is True
    assert caps.labelbar_adjust_materialization_from_supplied_bboxes is True
    assert caps.labelbar_adjust_apply_geometry_from_supplied_bboxes is True
    assert caps.labelbar_adjust_pipeline_from_supplied_metrics is True

    assert caps.explicit_adjusted_labelbar_svg_adapter is True
    assert caps.explicit_adjusted_labelbar_svg_export is True

    assert caps.text_bbox_engine is False
    assert caps.plotchar_metrics_engine is False
    assert caps.labelbar_adjust_geometry_engine is False

    assert caps.plotchar_parser is False
    assert caps.down_text_rendering is False
    assert caps.default_renderer_uses_adjusted_labelbar is False

    print("✅ graphics capabilities smoke passed")


if __name__ == "__main__":
    main()
