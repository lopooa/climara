from __future__ import annotations


def resource_groups():
    return {
        "ContourPlot": [
            "cnFillOn",
            "cnFillMode",
            "cnLinesOn",
            "cnLineLabelsOn",
            "cnInfoLabelOn",
            "cnLevelSelectionMode",
            "cnMinLevelValF",
            "cnMaxLevelValF",
            "cnLevelSpacingF",
            "cnFillPalette",
            "cnConstantFieldMode",
            "cnConstFLabelOn",
        ],
        "MapPlot": [
            "mpProjection",
            "mpCenterLonF",
            "mpCenterLatF",
            "mpLimitMode",
            "mpMinLonF",
            "mpMaxLonF",
            "mpMinLatF",
            "mpMaxLatF",
            "mpFillOn",
            "mpLandFillColor",
            "mpOceanFillColor",
            "mpOutlineOn",
            "mpNationalLineOn",
            "mpGridAndLimbOn",
            "mpGridLabelsOn",
            "mpGridLonValues",
            "mpGridLatValues",
            "mpGridLonSpacingF",
            "mpGridLatSpacingF",
        ],
        "LabelBar": [
            "lbLabelBarOn",
            "lbOrientation",
            "lbTitleString",
            "lbLabelAutoStride",
            "lbLabelMaxCount",
            "pmLabelBarWidthF",
            "pmLabelBarHeightF",
        ],
        "TickMark": [
            "tmXBOn",
            "tmXTOn",
            "tmYLOn",
            "tmYROn",
            "tmXBLabelsOn",
            "tmXTLabelsOn",
            "tmYLLabelsOn",
            "tmYRLabelsOn",
            "tmLabelClipOn",
            "tmPlainAxisTicksOn",
        ],
        "Panel": [
            "gsnPanelLabelBar",
            "gsnPanelLabelBarSide",
            "gsnPanelLabelBarWidthF",
            "gsnPanelLabelBarHeightF",
            "gsnPanelAutoTickLabels",
            "gsnPanelFigureStrings",
            "gsnPanelMainString",
        ],
        "Titles": [
            "tiMainString",
            "gsnLeftString",
            "gsnCenterString",
            "gsnRightString",
        ],
    }


def print_resource_groups():
    for group, names in resource_groups().items():
        print(f"[{group}]")
        for name in names:
            print(f"  - {name}")
        print()


def projection_aliases():
    return {
        "CylindricalEquidistant": "PlateCarree",
        "PlateCarree": "PlateCarree",
        "Robinson": "Robinson",
        "Mollweide": "Mollweide",
        "Mercator": "Mercator",
        "Orthographic": "Orthographic",
        "NorthPolarStereo": "Stereographic",
        "SouthPolarStereo": "Stereographic",
        "LambertConformal": "LambertConformal",
        "AlbersEqualArea": "AlbersEqualArea",
        "LambertAzimuthalEqualArea": "LambertAzimuthalEqualArea",
        "AzimuthalEquidistant": "AzimuthalEquidistant",
        "TransverseMercator": "TransverseMercator",
        "EqualEarth": "EqualEarth",
        "Sinusoidal": "Sinusoidal",
        "RotatedPole": "RotatedPole",
    }


def print_projection_aliases():
    for key, value in projection_aliases().items():
        print(f"{key} -> {value}")
