from __future__ import annotations

from pathlib import Path


SUPPORTED_RESOURCES = [
    {
        "group": "Workstation",
        "resource": "ncl_draw",
        "status": "yes",
        "file": "_workstation.py",
        "notes": "Draw a matplotlib figure.",
    },
    {
        "group": "Workstation",
        "resource": "ncl_frame",
        "status": "yes",
        "file": "_workstation.py",
        "notes": "Save a matplotlib figure.",
    },
    {
        "group": "Workstation",
        "resource": "ncl_close",
        "status": "yes",
        "file": "_workstation.py",
        "notes": "Close matplotlib figures.",
    },
    {
        "group": "Workstation",
        "resource": "NclWorkstation",
        "status": "yes",
        "file": "_workstation.py",
        "notes": "Workstation object with draw/frame/close methods.",
    },
    {
        "group": "ObjectLayer",
        "resource": "ContourMapPlot",
        "status": "yes",
        "file": "_objects.py",
        "notes": "Object-oriented wrapper around gsn_csm_contour_map.",
    },
    {
        "group": "ObjectLayer",
        "resource": "PanelMapPlot",
        "status": "yes",
        "file": "_objects.py",
        "notes": "Object-oriented wrapper around gsn_panel.",
    },
    {
        "group": "ObjectLayer",
        "resource": "contour_map",
        "status": "yes",
        "file": "_objects.py",
        "notes": "Convenience function returning a drawn ContourMapPlot.",
    },
    {
        "group": "ObjectLayer",
        "resource": "panel_map",
        "status": "yes",
        "file": "_objects.py",
        "notes": "Convenience function returning a drawn PanelMapPlot.",
    },
    {
        "group": "Overlay",
        "resource": "gsMarkerIndex",
        "status": "yes",
        "file": "_overlay.py",
        "notes": "Marker symbol index/name for marker overlays.",
    },
    {
        "group": "Overlay",
        "resource": "gsMarkerColor",
        "status": "yes",
        "file": "_overlay.py",
        "notes": "Marker face color.",
    },
    {
        "group": "Overlay",
        "resource": "gsMarkerSizeF",
        "status": "yes",
        "file": "_overlay.py",
        "notes": "Marker size.",
    },
    {
        "group": "Overlay",
        "resource": "gsMarkerAlphaF",
        "status": "yes",
        "file": "_overlay.py",
        "notes": "Marker opacity.",
    },
    {
        "group": "Overlay",
        "resource": "gsMarkerStride",
        "status": "yes",
        "file": "_overlay.py",
        "notes": "Subsample marker locations.",
    },
    {
        "group": "Overlay",
        "resource": "gsStippleStride",
        "status": "yes",
        "file": "_overlay.py",
        "notes": "Subsample stipple mask locations.",
    },
    {
        "group": "Overlay",
        "resource": "gsStippleColor",
        "status": "yes",
        "file": "_overlay.py",
        "notes": "Stipple marker color.",
    },
    {
        "group": "Overlay",
        "resource": "gsStippleMarkerSizeF",
        "status": "yes",
        "file": "_overlay.py",
        "notes": "Stipple marker size.",
    },
    {
        "group": "Overlay",
        "resource": "gsLineColor",
        "status": "yes",
        "file": "_overlay.py",
        "notes": "Polyline, polygon, and rectangle line color.",
    },
    {
        "group": "Overlay",
        "resource": "gsLineThicknessF",
        "status": "yes",
        "file": "_overlay.py",
        "notes": "Polyline, polygon, and rectangle line width.",
    },
    {
        "group": "Overlay",
        "resource": "gsLineDashPattern",
        "status": "yes",
        "file": "_overlay.py",
        "notes": "Polyline, polygon, and rectangle dash pattern.",
    },
    {
        "group": "Overlay",
        "resource": "gsFillColor",
        "status": "yes",
        "file": "_overlay.py",
        "notes": "Polygon/rectangle fill color.",
    },
    {
        "group": "Overlay",
        "resource": "gsCoordinateMode",
        "status": "yes",
        "file": "_overlay.py",
        "notes": "Use data/geographic, axes, or figure coordinates.",
    },
    {
        "group": "TextItem",
        "resource": "txFontHeightF",
        "status": "yes",
        "file": "_overlay.py",
        "notes": "Overlay text font size.",
    },
    {
        "group": "TextItem",
        "resource": "txFontColor",
        "status": "yes",
        "file": "_overlay.py",
        "notes": "Overlay text color.",
    },
    {
        "group": "TextItem",
        "resource": "txJust",
        "status": "yes",
        "file": "_overlay.py",
        "notes": "Overlay text justification.",
    },
    {
        "group": "TextItem",
        "resource": "txAngleF",
        "status": "yes",
        "file": "_overlay.py",
        "notes": "Overlay text rotation angle.",
    },
    {
        "group": "VectorPlot",
        "resource": "vcGlyphStyle",
        "status": "partial",
        "file": "_overlay.py",
        "notes": "LineArrow via quiver; WindBarb via barbs.",
    },
    {
        "group": "VectorPlot",
        "resource": "vcVectorScaleF",
        "status": "yes",
        "file": "_overlay.py",
        "notes": "Quiver vector scale.",
    },
    {
        "group": "VectorPlot",
        "resource": "vcMinDistanceF",
        "status": "yes",
        "file": "_overlay.py",
        "notes": "Vector stride/subsampling.",
    },
    {
        "group": "VectorPlot",
        "resource": "vcRefAnnoOn",
        "status": "yes",
        "file": "_overlay.py",
        "notes": "Draw a vector reference annotation.",
    },
    {
        "group": "VectorPlot",
        "resource": "vcRefMagnitudeF",
        "status": "yes",
        "file": "_overlay.py",
        "notes": "Reference vector magnitude.",
    },
    {
        "group": "LabelBar",
        "resource": "lbLabelAlignment",
        "status": "yes",
        "file": "_labelbar.py",
        "notes": "Control whether labels are placed on box centers, boundaries, or interior edges.",
    },
    {
        "group": "LabelBar",
        "resource": "lbLabelFormat",
        "status": "yes",
        "file": "_labelbar.py",
        "notes": "Format tick labels using printf, format spec, or str.format style.",
    },
    {
        "group": "LabelBar",
        "resource": "lbLabelMaxCount",
        "status": "yes",
        "file": "_labelbar.py",
        "notes": "Maximum label count used by lbLabelAutoStride.",
    },
    {
        "group": "LabelBar",
        "resource": "lbTickMarksOn",
        "status": "yes",
        "file": "_labelbar.py",
        "notes": "Turn labelbar tick marks on/off.",
    },
    {
        "group": "LabelBar",
        "resource": "lbTickLengthF",
        "status": "yes",
        "file": "_labelbar.py",
        "notes": "Tick mark length.",
    },
    {
        "group": "LabelBar",
        "resource": "lbTickThicknessF",
        "status": "yes",
        "file": "_labelbar.py",
        "notes": "Tick mark linewidth.",
    },
    {
        "group": "LabelBar",
        "resource": "lbBoxSeparatorLineThicknessF",
        "status": "yes",
        "file": "_labelbar.py",
        "notes": "Line width for separators between labelbar boxes.",
    },
    {
        "group": "MapPlot",
        "resource": "mpGeophysicalLineColor",
        "status": "yes",
        "file": "_maps.py",
        "notes": "Coastline/geophysical outline color.",
    },
    {
        "group": "MapPlot",
        "resource": "mpGeophysicalLineThicknessF",
        "status": "yes",
        "file": "_maps.py",
        "notes": "Coastline/geophysical outline linewidth.",
    },
    {
        "group": "MapPlot",
        "resource": "mpNationalLineColor",
        "status": "yes",
        "file": "_maps.py",
        "notes": "National-border line color.",
    },
    {
        "group": "MapPlot",
        "resource": "mpNationalLineThicknessF",
        "status": "yes",
        "file": "_maps.py",
        "notes": "National-border linewidth.",
    },
    {
        "group": "MapPlot",
        "resource": "mpUSStateLineOn",
        "status": "yes",
        "file": "_maps.py",
        "notes": "Draw US state/province lines where Cartopy data are available.",
    },
    {
        "group": "MapPlot",
        "resource": "mpDataResolution",
        "status": "yes",
        "file": "_maps.py",
        "notes": "Map Natural Earth data resolution: 110m, 50m, 10m, or NCL-like aliases.",
    },
    {
        "group": "MapPlot",
        "resource": "mpPerimLineColor",
        "status": "yes",
        "file": "_maps.py",
        "notes": "Map perimeter line color.",
    },
    {
        "group": "MapPlot",
        "resource": "mpPerimLineThicknessF",
        "status": "yes",
        "file": "_maps.py",
        "notes": "Map perimeter linewidth.",
    },
    {
        "group": "GSN",
        "resource": "gsnPolar",
        "status": "yes",
        "file": "_gsn.py / _maps.py",
        "notes": "Enable polar-map defaults and polar label handling.",
    },
    {
        "group": "GSN",
        "resource": "gsnPolarLabelOn",
        "status": "yes",
        "file": "_maps.py",
        "notes": "Turn polar labels on/off.",
    },
    {
        "group": "GSN",
        "resource": "gsnPolarLabelDistance",
        "status": "yes",
        "file": "_maps.py",
        "notes": "Distance of polar labels from the circular map boundary.",
    },
    {
        "group": "GSN",
        "resource": "gsnPolarLabelFontHeightF",
        "status": "yes",
        "file": "_maps.py",
        "notes": "Polar label font size.",
    },
    {
        "group": "GSN",
        "resource": "gsnPolarLongitudeLabelsOn",
        "status": "yes",
        "file": "_maps.py",
        "notes": "Draw longitude labels around polar maps.",
    },
    {
        "group": "GSN",
        "resource": "gsnPolarLatitudeLabelOn",
        "status": "yes",
        "file": "_maps.py",
        "notes": "Draw the polar edge-latitude label.",
    },
    # contour
    {
        "group": "ContourPlot",
        "resource": "cnFillOn",
        "status": "yes",
        "file": "_contour.py",
        "notes": "Turn filled contour/raster field on or off.",
    },
    {
        "group": "ContourPlot",
        "resource": "cnFillMode",
        "status": "partial",
        "file": "_contour.py",
        "notes": "Supports AreaFill, RasterFill, CellFill, PcolorFill, Pcolormesh.",
    },
    {
        "group": "ContourPlot",
        "resource": "cnLinesOn",
        "status": "yes",
        "file": "_contour.py",
        "notes": "Draw contour lines.",
    },
    {
        "group": "ContourPlot",
        "resource": "cnLineLabelsOn",
        "status": "yes",
        "file": "_contour.py",
        "notes": "Draw contour line labels.",
    },
    {
        "group": "ContourPlot",
        "resource": "cnLevelSelectionMode",
        "status": "partial",
        "file": "_resources.py",
        "notes": "Supports ExplicitLevels, ManualLevels, EqualSpacedLevels.",
    },
    {
        "group": "ContourPlot",
        "resource": "cnLevels",
        "status": "yes",
        "file": "_resources.py",
        "notes": "Explicit contour levels.",
    },
    {
        "group": "ContourPlot",
        "resource": "cnMinLevelValF",
        "status": "yes",
        "file": "_resources.py",
        "notes": "Minimum value for ManualLevels / EqualSpacedLevels.",
    },
    {
        "group": "ContourPlot",
        "resource": "cnMaxLevelValF",
        "status": "yes",
        "file": "_resources.py",
        "notes": "Maximum value for ManualLevels / EqualSpacedLevels.",
    },
    {
        "group": "ContourPlot",
        "resource": "cnLevelSpacingF",
        "status": "yes",
        "file": "_resources.py",
        "notes": "Contour level spacing for ManualLevels.",
    },
    {
        "group": "ContourPlot",
        "resource": "cnFillPalette",
        "status": "yes",
        "file": "_colors.py",
        "notes": "Matplotlib colormap name or packaged .rgb colormap.",
    },
    {
        "group": "ContourPlot",
        "resource": "cnFillColors",
        "status": "yes",
        "file": "_contour.py",
        "notes": "Explicit fill color list.",
    },
    {
        "group": "ContourPlot",
        "resource": "cnFillExtendMode",
        "status": "yes",
        "file": "_contour.py",
        "notes": "Supports both, neither, min, max.",
    },
    {
        "group": "ContourPlot",
        "resource": "cnMissingValFillColor",
        "status": "yes",
        "file": "_contour.py",
        "notes": "Color for missing values.",
    },
    {
        "group": "ContourPlot",
        "resource": "cnLineColor",
        "status": "yes",
        "file": "_contour.py / _overlay.py",
        "notes": "Single contour line color.",
    },
    {
        "group": "ContourPlot",
        "resource": "cnLineColors",
        "status": "yes",
        "file": "_contour.py / _overlay.py",
        "notes": "Contour line color list.",
    },
    {
        "group": "ContourPlot",
        "resource": "cnLineThicknessF",
        "status": "yes",
        "file": "_contour.py / _overlay.py",
        "notes": "Single contour line thickness.",
    },
    {
        "group": "ContourPlot",
        "resource": "cnLineThicknesses",
        "status": "yes",
        "file": "_contour.py / _overlay.py",
        "notes": "Contour line thickness list.",
    },
    {
        "group": "ContourPlot",
        "resource": "cnLineDashPattern",
        "status": "yes",
        "file": "_contour.py / _overlay.py",
        "notes": "Single contour dash pattern.",
    },
    {
        "group": "ContourPlot",
        "resource": "cnLineDashPatterns",
        "status": "yes",
        "file": "_contour.py / _overlay.py",
        "notes": "Contour dash pattern list.",
    },
    {
        "group": "ContourPlot",
        "resource": "cnLineLabelInterval",
        "status": "yes",
        "file": "_contour.py / _overlay.py",
        "notes": "Label every N contour levels.",
    },
    {
        "group": "ContourPlot",
        "resource": "cnLineLabelBackgroundColor",
        "status": "yes",
        "file": "_contour.py / _overlay.py",
        "notes": "Background box color for line labels.",
    },
    {
        "group": "ContourPlot",
        "resource": "cnSmoothingOn",
        "status": "partial",
        "file": "_contour.py",
        "notes": "Gaussian smoothing via scipy.ndimage.",
    },
    {
        "group": "ContourPlot",
        "resource": "cnSmoothingSigmaF",
        "status": "yes",
        "file": "_contour.py",
        "notes": "Gaussian smoothing sigma.",
    },
    {
        "group": "ContourPlot",
        "resource": "cnConstFLabelOn",
        "status": "yes",
        "file": "_contour.py",
        "notes": "Label constant fields.",
    },
    {
        "group": "ContourPlot",
        "resource": "cnInfoLabelOn",
        "status": "partial",
        "file": "_contour.py",
        "notes": "Simple min/max info label.",
    },
    {
        "group": "ContourPlot",
        "resource": "cnCellFillEdgeColor",
        "status": "yes",
        "file": "_contour.py",
        "notes": "Cell edge color for pcolormesh-like fill modes.",
    },

    # map
    {
        "group": "MapPlot",
        "resource": "mpProjection",
        "status": "partial",
        "file": "_maps.py",
        "notes": "Supports PlateCarree, Stereographic, Orthographic, Robinson, Mollweide, Mercator, LambertConformal, Albers.",
    },
    {
        "group": "MapPlot",
        "resource": "mpCenterLonF",
        "status": "yes",
        "file": "_maps.py",
        "notes": "Projection center longitude.",
    },
    {
        "group": "MapPlot",
        "resource": "mpCenterLatF",
        "status": "yes",
        "file": "_maps.py",
        "notes": "Projection center latitude.",
    },
    {
        "group": "MapPlot",
        "resource": "mpMinLonF / mpMaxLonF / mpMinLatF / mpMaxLatF",
        "status": "yes",
        "file": "_maps.py",
        "notes": "Lat/lon extent control.",
    },
    {
        "group": "MapPlot",
        "resource": "mpLimitMode",
        "status": "partial",
        "file": "_maps.py",
        "notes": "Supports LatLon / Corners style extent.",
    },
    {
        "group": "MapPlot",
        "resource": "mpFillOn",
        "status": "yes",
        "file": "_maps.py",
        "notes": "Enable land/ocean/inland water fill.",
    },
    {
        "group": "MapPlot",
        "resource": "mpLandFillColor",
        "status": "yes",
        "file": "_maps.py",
        "notes": "Land fill color.",
    },
    {
        "group": "MapPlot",
        "resource": "mpOceanFillColor",
        "status": "yes",
        "file": "_maps.py",
        "notes": "Ocean fill color.",
    },
    {
        "group": "MapPlot",
        "resource": "mpInlandWaterFillColor",
        "status": "yes",
        "file": "_maps.py",
        "notes": "Lake/inland water fill color.",
    },
    {
        "group": "MapPlot",
        "resource": "mpOutlineOn",
        "status": "yes",
        "file": "_maps.py",
        "notes": "Draw coastlines.",
    },
    {
        "group": "MapPlot",
        "resource": "mpNationalLineOn",
        "status": "yes",
        "file": "_maps.py",
        "notes": "Draw national borders.",
    },
    {
        "group": "MapPlot",
        "resource": "mpGridAndLimbOn",
        "status": "yes",
        "file": "_maps.py",
        "notes": "Draw gridlines.",
    },
    {
        "group": "MapPlot",
        "resource": "mpGridLabelsOn",
        "status": "yes",
        "file": "_maps.py / _tickmark.py",
        "notes": "Draw gridline labels.",
    },
    {
        "group": "MapPlot",
        "resource": "mpGridSpacingF / mpGridLonSpacingF / mpGridLatSpacingF",
        "status": "yes",
        "file": "_tickmark.py",
        "notes": "Gridline spacing.",
    },
    {
        "group": "MapPlot",
        "resource": "mpPerimOn",
        "status": "partial",
        "file": "_maps.py",
        "notes": "Map perimeter visibility.",
    },

    {
        "group": "MapPlot",
        "resource": "mpOutlineBoundarySets",
        "status": "partial",
        "file": "_maps.py",
        "notes": "Maps common NCL boundary-set names to coastline, national border, and US state features.",
    },

    # labelbar
    {
        "group": "LabelBar",
        "resource": "lbLabelBarOn",
        "status": "yes",
        "file": "_labelbar.py",
        "notes": "Turn labelbar on/off.",
    },
    {
        "group": "LabelBar",
        "resource": "lbOrientation",
        "status": "yes",
        "file": "_labelbar.py",
        "notes": "Horizontal or vertical labelbar.",
    },
    {
        "group": "LabelBar",
        "resource": "lbTitleString",
        "status": "yes",
        "file": "_labelbar.py",
        "notes": "Labelbar title.",
    },
    {
        "group": "LabelBar",
        "resource": "lbTitlePosition",
        "status": "yes",
        "file": "_labelbar.py",
        "notes": "Title position such as top/bottom/right/left.",
    },
    {
        "group": "LabelBar",
        "resource": "lbLabelStrings",
        "status": "yes",
        "file": "_labelbar.py",
        "notes": "Custom tick labels.",
    },
    {
        "group": "LabelBar",
        "resource": "lbLabelPositions",
        "status": "yes",
        "file": "_labelbar.py",
        "notes": "Custom tick positions.",
    },
    {
        "group": "LabelBar",
        "resource": "lbLabelStride",
        "status": "yes",
        "file": "_labelbar.py",
        "notes": "Show every N labels.",
    },
    {
        "group": "LabelBar",
        "resource": "lbLabelAutoStride",
        "status": "yes",
        "file": "_labelbar.py",
        "notes": "Automatically reduce label count.",
    },
    {
        "group": "LabelBar",
        "resource": "lbBoxLinesOn",
        "status": "yes",
        "file": "_labelbar.py",
        "notes": "Draw labelbar outline and separator lines.",
    },
    {
        "group": "LabelBar",
        "resource": "pmLabelBarSide",
        "status": "yes",
        "file": "_labelbar.py",
        "notes": "Position labelbar on bottom/top/left/right.",
    },
    {
        "group": "LabelBar",
        "resource": "pmLabelBarWidthF / pmLabelBarHeightF",
        "status": "yes",
        "file": "_labelbar.py",
        "notes": "Manual labelbar size.",
    },
    {
        "group": "LabelBar",
        "resource": "pmLabelBarOrthogonalPosF / pmLabelBarParallelPosF",
        "status": "partial",
        "file": "_labelbar.py",
        "notes": "Manual offset from plot axes.",
    },

    # panel
    {
        "group": "Panel",
        "resource": "gsnPanelMainString",
        "status": "yes",
        "file": "_panel.py",
        "notes": "Panel main title.",
    },
    {
        "group": "Panel",
        "resource": "gsnPanelFigureStrings",
        "status": "yes",
        "file": "_panel.py",
        "notes": "Panel labels like (a), (b), ...",
    },
    {
        "group": "Panel",
        "resource": "gsnPanelRowTitles / gsnPanelColTitles",
        "status": "yes",
        "file": "_panel.py",
        "notes": "Panel row/column titles.",
    },
    {
        "group": "Panel",
        "resource": "gsnPanelLeft / Right / Top / Bottom",
        "status": "yes",
        "file": "_panel.py",
        "notes": "Manual panel layout bounds.",
    },
    {
        "group": "Panel",
        "resource": "gsnPanelXWhiteSpacePercent / gsnPanelYWhiteSpacePercent",
        "status": "yes",
        "file": "_panel.py",
        "notes": "Panel spacing controls.",
    },
    {
        "group": "Panel",
        "resource": "gsnPanelLabelBar",
        "status": "yes",
        "file": "_panel.py",
        "notes": "Shared panel labelbar.",
    },

    # gsn strings
    {
        "group": "GSN",
        "resource": "gsnLeftString / gsnCenterString / gsnRightString",
        "status": "yes",
        "file": "_strings.py",
        "notes": "NCL-style left/center/right plot strings.",
    },
    {
        "group": "GSN",
        "resource": "gsnAddCyclic",
        "status": "yes",
        "file": "_contour.py / _overlay.py",
        "notes": "Add cyclic longitude point.",
    },
    {
        "group": "GSN",
        "resource": "gsnFrame",
        "status": "partial",
        "file": "_contour.py / _workstation.py",
        "notes": "Save figure if filename is supplied; workstation frame also supported.",
    },

    # overlay
    {
        "group": "Overlay",
        "resource": "overlay_contour",
        "status": "yes",
        "file": "_overlay.py",
        "notes": "Contour overlay.",
    },
    {
        "group": "Overlay",
        "resource": "overlay_filled_contour / overlay_pcolormesh",
        "status": "yes",
        "file": "_overlay.py",
        "notes": "Filled field overlay.",
    },
    {
        "group": "Overlay",
        "resource": "overlay_vectors",
        "status": "yes",
        "file": "_overlay.py",
        "notes": "Vector/quiver overlay.",
    },
    {
        "group": "Overlay",
        "resource": "overlay_markers / overlay_text",
        "status": "yes",
        "file": "_overlay.py",
        "notes": "Marker and text annotations.",
    },
    {
        "group": "Overlay",
        "resource": "overlay_polyline / polygon / rectangle",
        "status": "yes",
        "file": "_overlay.py",
        "notes": "Geometric annotation overlays.",
    },
    {
        "group": "Overlay",
        "resource": "add_hatching / add_stipple",
        "status": "yes",
        "file": "_hatching.py",
        "notes": "Hatch and stipple masks.",
    },

    # tickmark
    {
        "group": "TickMark",
        "resource": "tmXBOn / tmXTOn / tmYLOn / tmYROn",
        "status": "yes",
        "file": "_tickmark.py",
        "notes": "Bottom/top/left/right tick label controls.",
    },
    {
        "group": "TickMark",
        "resource": "tmXBLabelFontHeightF / tmYLLabelFontHeightF",
        "status": "yes",
        "file": "_tickmark.py",
        "notes": "Tick label size.",
    },
    {
        "group": "TickMark",
        "resource": "tmXBValues / tmYLValues",
        "status": "partial",
        "file": "_tickmark.py",
        "notes": "Custom tick/grid values.",
    },

    # workstation
    {
        "group": "Workstation",
        "resource": "gsn_open_wks",
        "status": "yes",
        "file": "_workstation.py",
        "notes": "NCL-style workstation object.",
    },
    {
        "group": "Workstation",
        "resource": "frame / ncl_frame",
        "status": "yes",
        "file": "_workstation.py",
        "notes": "Save a frame with automatic frame numbering.",
    },

    # objects
    {
        "group": "Objects",
        "resource": "ScalarField",
        "status": "yes",
        "file": "_objects.py",
        "notes": "Python object inspired by NCL scalarFieldClass.",
    },
    {
        "group": "Objects",
        "resource": "ContourMapPlot / PanelMapPlot / MapPlot",
        "status": "yes",
        "file": "_objects.py",
        "notes": "Object-oriented plotting workflow.",
    },

    {
        "group": "Panel",
        "resource": "gsnPanelAutoTickLabels",
        "status": "yes",
        "file": "_panel.py / _tickmark.py",
        "notes": "Automatically shows only outer panel tick/grid labels by default.",
    },
    {
        "group": "Panel",
        "resource": "gsnPanelTopLabelsOn / gsnPanelRightLabelsOn / gsnPanelBottomLabelsOn / gsnPanelLeftLabelsOn",
        "status": "yes",
        "file": "_panel.py",
        "notes": "Controls which outer panel sides receive tick/grid labels.",
    },
    {
        "group": "Panel",
        "resource": "gsnPanelLabelBarSide / gsnPanelLabelBarOrientation",
        "status": "yes",
        "file": "_panel.py",
        "notes": "Places the shared panel labelbar on bottom/top/left/right.",
    },
    {
        "group": "Panel",
        "resource": "gsnPanelLabelBarWidthF / gsnPanelLabelBarHeightF / gsnPanelLabelBarOrthogonalPosF / gsnPanelLabelBarParallelPosF",
        "status": "yes",
        "file": "_panel.py",
        "notes": "NCL-style shared panel labelbar size and offset controls.",
    },
    {
        "group": "TickMark",
        "resource": "tmXBLabelsOn / tmXTLabelsOn / tmYLLabelsOn / tmYRLabelsOn",
        "status": "yes",
        "file": "_tickmark.py",
        "notes": "Separates label visibility from tick visibility for all four sides.",
    },
    {
        "group": "TickMark",
        "resource": "tmXTLabelFontHeightF / tmYRLabelFontHeightF / tmXTLabelFontColor / tmYRLabelFontColor",
        "status": "yes",
        "file": "_tickmark.py",
        "notes": "Top and right label styling support, in addition to bottom and left.",
    },
    {
        "group": "TickMark",
        "resource": "tmLabelClipOn",
        "status": "yes",
        "file": "_tickmark.py",
        "notes": "Clips tick labels to reduce overflow around panel edges.",
    },

    {
        "group": "ContourPlot",
        "resource": "cnFillMode = Auto / Contourf / AreaFill / RasterFill / CellFill",
        "status": "partial",
        "file": "_contour.py",
        "notes": "Auto path tries contourf-style fill and can fall back to pcolormesh.",
    },
    {
        "group": "ContourPlot",
        "resource": "cnLineLabelsOn / cnLineLabelInterval / cnLineLabelFormat",
        "status": "yes",
        "file": "_contour.py",
        "notes": "Adds Matplotlib clabel support for NCL-style contour line labels.",
    },
    {
        "group": "ContourPlot",
        "resource": "cnInfoLabelOn / cnInfoLabelString",
        "status": "yes",
        "file": "_contour.py",
        "notes": "Adds simple info label with automatic min/max/interval text.",
    },
    {
        "group": "ContourPlot",
        "resource": "cnConstantFieldMode / cnConstFLabelOn",
        "status": "yes",
        "file": "_contour.py",
        "notes": "Adds safe fallback behavior for constant fields.",
    },

    {
        "group": "MapPlot",
        "resource": "LambertAzimuthalEqualArea / AzimuthalEquidistant / TransverseMercator",
        "status": "partial",
        "file": "_maps.py",
        "notes": "Adds more Cartopy projection aliases using NCL-style mpProjection names.",
    },
    {
        "group": "MapPlot",
        "resource": "mpCoastlineOn / mpLakeLineOn / mpRiverLineOn / mpUSStateLineOn",
        "status": "yes",
        "file": "_maps.py",
        "notes": "Adds more map outline and boundary controls.",
    },
    {
        "group": "MapPlot",
        "resource": "mpLandFillColor / mpOceanFillColor / mpInlandWaterFillColor",
        "status": "yes",
        "file": "_maps.py",
        "notes": "Improves NCL-style land, ocean, and inland water fill controls.",
    },
]


def list_supported_resources(group: str | None = None, status: str | None = None):
    rows = SUPPORTED_RESOURCES

    if group is not None:
        group_l = group.lower()
        rows = [row for row in rows if row["group"].lower() == group_l]

    if status is not None:
        status_l = status.lower()
        rows = [row for row in rows if row["status"].lower() == status_l]

    return rows


def search_supported_resources(keyword: str):
    keyword = keyword.lower()

    return [
        row
        for row in SUPPORTED_RESOURCES
        if keyword in row["resource"].lower()
        or keyword in row["group"].lower()
        or keyword in row["notes"].lower()
        or keyword in row["file"].lower()
    ]


def supported_resources_to_markdown(rows=None):
    if rows is None:
        rows = SUPPORTED_RESOURCES

    lines = [
        "# NCL-style Resource Compatibility",
        "",
        "| Group | Resource | Status | File | Notes |",
        "|---|---|---:|---|---|",
    ]

    for row in rows:
        lines.append(
            f"| {row['group']} | `{row['resource']}` | {row['status']} | `{row['file']}` | {row['notes']} |"
        )

    lines.append("")

    return "\n".join(lines)


def export_resource_compatibility(path="docs/ncl_resource_compatibility.md", rows=None):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(supported_resources_to_markdown(rows), encoding="utf-8")
    return path


def print_supported_resources(group: str | None = None, status: str | None = None):
    rows = list_supported_resources(group=group, status=status)
    print(supported_resources_to_markdown(rows))

# climara v0.2.9 compatibility helpers begin

def _compat_normalize_status(status):
    status = str(status).strip().lower()

    aliases = {
        "yes": "yes",
        "supported": "yes",
        "done": "yes",
        "true": "yes",
        "partial": "partial",
        "partly": "partial",
        "experimental": "partial",
        "planned": "planned",
        "todo": "planned",
        "no": "planned",
        "false": "planned",
    }

    return aliases.get(status, status or "planned")


def _compat_resource_rows():
    rows = []

    for item in SUPPORTED_RESOURCES:
        row = dict(item)
        row.setdefault("group", "Other")
        row.setdefault("resource", "")
        row.setdefault("status", "planned")
        row.setdefault("file", "")
        row.setdefault("notes", "")
        row["status"] = _compat_normalize_status(row["status"])
        rows.append(row)

    rows.sort(
        key=lambda r: (
            str(r.get("group", "")),
            str(r.get("resource", "")),
        )
    )

    return rows


def get_resource_compatibility():
    return _compat_resource_rows()


def list_supported_resources(group=None, status=None):
    rows = _compat_resource_rows()

    if group is not None:
        key = str(group).lower()
        rows = [
            row for row in rows
            if str(row.get("group", "")).lower() == key
        ]

    if status is not None:
        key = _compat_normalize_status(status)
        rows = [
            row for row in rows
            if _compat_normalize_status(row.get("status", "")) == key
        ]

    return rows


def search_supported_resources(keyword):
    keyword = str(keyword).lower()
    rows = _compat_resource_rows()

    return [
        row for row in rows
        if keyword in str(row.get("resource", "")).lower()
        or keyword in str(row.get("group", "")).lower()
        or keyword in str(row.get("file", "")).lower()
        or keyword in str(row.get("notes", "")).lower()
    ]


def summarize_resource_compatibility():
    rows = _compat_resource_rows()
    summary = {}

    for row in rows:
        status = _compat_normalize_status(row.get("status", "planned"))
        summary[status] = summary.get(status, 0) + 1

    return dict(sorted(summary.items()))


def _compat_markdown_table(rows):
    lines = [
        "| Group | Resource | Status | File | Notes |",
        "|---|---|---|---|---|",
    ]

    for row in rows:
        group = str(row.get("group", "")).replace("|", "\\|")
        resource = str(row.get("resource", "")).replace("|", "\\|")
        status = str(row.get("status", "")).replace("|", "\\|")
        file = str(row.get("file", "")).replace("|", "\\|")
        notes = str(row.get("notes", "")).replace("|", "\\|")

        lines.append(
            f"| {group} | `{resource}` | {status} | `{file}` | {notes} |"
        )

    return "\n".join(lines)


def make_resource_compatibility_markdown(title="NCL Resource Compatibility"):
    rows = _compat_resource_rows()
    summary = summarize_resource_compatibility()

    lines = [
        f"# {title}",
        "",
        "This file is generated from `src/climara/plotting/_compat.py`.",
        "",
        "## Summary",
        "",
        "| Status | Count |",
        "|---|---:|",
    ]

    for status, count in summary.items():
        lines.append(f"| {status} | {count} |")

    lines.extend(
        [
            "",
            "## Resources",
            "",
            _compat_markdown_table(rows),
            "",
        ]
    )

    return "\n".join(lines)


def export_resource_compatibility(path="docs/ncl_resource_compatibility.md"):
    from pathlib import Path

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        make_resource_compatibility_markdown(),
        encoding="utf-8",
    )

    return path


def print_resource_compatibility_summary():
    summary = summarize_resource_compatibility()

    print("NCL resource compatibility summary:")

    for status, count in summary.items():
        print(f"  {status}: {count}")

    return summary

# climara v0.2.9 compatibility helpers end
