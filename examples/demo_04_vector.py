import numpy as np
import matplotlib.pyplot as plt

from climara.graphics import ncl_style, gsn_csm_contour_map, overlay_vectors

ncl_style()

lon = np.linspace(0, 357.5, 72)
lat = np.linspace(-70, 70, 36)
lon2d, lat2d = np.meshgrid(lon, lat)

data = np.sin(np.deg2rad(lon2d)) * np.cos(np.deg2rad(lat2d))
u = np.cos(np.deg2rad(lat2d))
v = np.sin(np.deg2rad(lon2d))

res = {
    "cnLevelSelectionMode": "ManualLevels",
    "cnMinLevelValF": -1,
    "cnMaxLevelValF": 1,
    "cnLevelSpacingF": 0.2,
    "cnFillPalette": "MPL_RdBu",
    "mpGridAndLimbOn": True,
    "tiMainString": "vector overlay",
}

fig, ax, out = gsn_csm_contour_map(data, lon=lon, lat=lat, res=res)

overlay_vectors(
    ax,
    u,
    v,
    lon=lon,
    lat=lat,
    res={
        "vcMinDistanceF": 3,
        "vcVectorColor": "black",
        "vcVectorScaleF": 45,
        "vcLineArrowThicknessF": 0.0025,
    },
)

fig.savefig("demo_04_vector.png", bbox_inches="tight")
plt.close(fig)
print("saved demo_04_vector.png")
