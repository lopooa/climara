import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

from climara.plotting import (
    ncl_style,
    create_projection,
    gsn_csm_contour_map,
)


ncl_style()

lon = np.linspace(0, 357.5, 144)
lat = np.linspace(-90, 90, 73)
lon2d, lat2d = np.meshgrid(lon, lat)

data = (
    3.0 * np.sin(np.deg2rad(lon2d * 2.0)) * np.cos(np.deg2rad(lat2d))
    + 2.0 * np.sin(np.deg2rad(lat2d * 2.0))
)

base_res = {
    "cnFillOn": True,
    "cnFillMode": "Pcolormesh",
    "cnLinesOn": False,
    "cnLevelSelectionMode": "ManualLevels",
    "cnMinLevelValF": -5,
    "cnMaxLevelValF": 5,
    "cnLevelSpacingF": 1,
    "cnFillPalette": "RdBu_r",
    "lbLabelBarOn": True,
    "lbOrientation": "horizontal",
    "lbTitleString": "demo units",
    "gsnAddCyclic": True,
}

res = dict(base_res)
res.update(
    {
        "mpProjection": "Robinson",
        "mpCenterLonF": 180,
        "mpFillOn": True,
        "mpLandFillColor": "0.92",
        "mpOceanFillColor": "white",
        "mpGridAndLimbOn": True,
        "mpGridSpacingF": 30,
        "mpGridLineColor": "0.65",
        "mpGridLineDashPattern": "--",
        "mpNationalLineOn": True,
        "mpGeophysicalLineThicknessF": 0.9,
        "tiMainString": "MapPlot: Robinson + fill + grid spacing",
    }
)

fig, ax, out = gsn_csm_contour_map(data, lon=lon, lat=lat, res=res)
fig.savefig("demo_11_map_robinson.png", bbox_inches="tight")
plt.close(fig)

res = dict(base_res)
res.update(
    {
        "mpProjection": "LambertConformal",
        "mpCenterLonF": -100,
        "mpCenterLatF": 40,
        "mpLambertParallel1F": 30,
        "mpLambertParallel2F": 60,
        "mpLimitMode": "LatLon",
        "mpMinLonF": -140,
        "mpMaxLonF": -55,
        "mpMinLatF": 15,
        "mpMaxLatF": 65,
        "mpFillOn": True,
        "mpLandFillColor": "0.94",
        "mpOceanFillColor": "aliceblue",
        "mpGridAndLimbOn": True,
        "mpGridLabelsOn": True,
        "mpGridLonSpacingF": 20,
        "mpGridLatSpacingF": 10,
        "mpGridLabelFontHeightF": 8,
        "mpNationalLineOn": True,
        "mpPerimOn": True,
        "mpPerimLineColor": "0.15",
        "mpPerimLineThicknessF": 1.2,
        "tiMainString": "MapPlot: LambertConformal + LatLon limit",
    }
)

fig, ax, out = gsn_csm_contour_map(data, lon=lon, lat=lat, res=res)
fig.savefig("demo_11_map_lambert.png", bbox_inches="tight")
plt.close(fig)

res = dict(base_res)
res.update(
    {
        "mpProjection": "Orthographic",
        "mpCenterLonF": 105,
        "mpCenterLatF": 25,
        "mpFillOn": True,
        "mpLandFillColor": "0.93",
        "mpOceanFillColor": "white",
        "mpInlandWaterFillColor": "lightblue",
        "mpGridAndLimbOn": True,
        "mpGridSpacingF": 30,
        "mpOutlineOn": True,
        "mpNationalLineOn": True,
        "mpPerimOn": True,
        "tiMainString": "MapPlot: Orthographic",
    }
)

fig, ax, out = gsn_csm_contour_map(data, lon=lon, lat=lat, res=res)
fig.savefig("demo_11_map_orthographic.png", bbox_inches="tight")
plt.close(fig)

print("saved demo_11_map_robinson.png")
print("saved demo_11_map_lambert.png")
print("saved demo_11_map_orthographic.png")
