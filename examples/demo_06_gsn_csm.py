import numpy as np
import matplotlib.pyplot as plt

from climara.graphics import ncl_style, gsn_csm_contour_map, gsn_csm_contour_map_polar

ncl_style()

lon = np.linspace(0, 357.5, 144)
lat = np.linspace(-90, 90, 73)
lon2d, lat2d = np.meshgrid(lon, lat)
data = 4.0 * np.sin(np.deg2rad(lon2d * 2.0)) * np.cos(np.deg2rad(lat2d))

res = {
    "cnLevelSelectionMode": "ManualLevels",
    "cnMinLevelValF": -5,
    "cnMaxLevelValF": 5,
    "cnLevelSpacingF": 1,
    "cnFillPalette": "BlueWhiteOrangeRed",
    "mpGridAndLimbOn": True,
    "mpNationalLineOn": True,
    "lbTitleString": "demo units",
    "tiMainString": "gsn_csm_contour_map",
}

fig, ax, out = gsn_csm_contour_map(data, lon=lon, lat=lat, res=res)
fig.savefig("demo_06_gsn_csm_contour_map.png", bbox_inches="tight")
plt.close(fig)

lat_nh = lat[lat >= 20]
nh = data[lat >= 20, :]
res_polar = dict(res)
res_polar.update({"mpMinLatF": 20, "tiMainString": "gsn_csm_contour_map_polar"})
fig, ax, out = gsn_csm_contour_map_polar(nh, lon=lon, lat=lat_nh, res=res_polar, hemisphere="NH")
fig.savefig("demo_06_gsn_csm_contour_map_polar.png", bbox_inches="tight")
plt.close(fig)

print("saved demo_06_gsn_csm_contour_map.png")
print("saved demo_06_gsn_csm_contour_map_polar.png")
