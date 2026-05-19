import numpy as np
import xarray as xr
import matplotlib.pyplot as plt

from climara.plotting import ncl_style, gsn_csm_contour_map

ncl_style()

lon = np.linspace(0, 357.5, 144)
lat = np.linspace(-90, 90, 73)
lon2d, lat2d = np.meshgrid(lon, lat)
data = 4.0 * np.sin(np.deg2rad(lon2d * 2.0)) * np.cos(np.deg2rad(lat2d))

da = xr.DataArray(data, dims=("lat", "lon"), coords={"lat": lat, "lon": lon}, name="demo")

res = {
    "cnLevelSelectionMode": "ManualLevels",
    "cnMinLevelValF": -5,
    "cnMaxLevelValF": 5,
    "cnLevelSpacingF": 1,
    "cnFillPalette": "BlueRed",
    "mpGridAndLimbOn": True,
    "tiMainString": "xarray DataArray input",
}

fig, ax, out = gsn_csm_contour_map(da, res=res)
fig.savefig("demo_05_xarray.png", bbox_inches="tight")
plt.close(fig)
print("saved demo_05_xarray.png")
