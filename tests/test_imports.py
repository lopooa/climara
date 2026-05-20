def test_climara_import():
    import climara

    assert climara.__version__ == "0.3.5"


def test_plotting_imports():
    from climara.plotting import (
        gsn_csm_contour_map,
        gsn_csm_contour_map_polar,
        gsn_panel,
        gsn_open_wks,
        ScalarField,
        ContourMapPlot,
        PanelMapPlot,
        export_resource_compatibility,
    )

    assert gsn_csm_contour_map is not None
    assert gsn_csm_contour_map_polar is not None
    assert gsn_panel is not None
    assert gsn_open_wks is not None
    assert ScalarField is not None
    assert ContourMapPlot is not None
    assert PanelMapPlot is not None
    assert export_resource_compatibility is not None
