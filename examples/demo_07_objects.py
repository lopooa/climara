import numpy as np
import matplotlib.pyplot as plt

from climara.graphics import ncl_style, ScalarField, ContourMapPlot

ncl_style()

lon = np.linspace(0, 357.5, 144)
lat = np.linspace(-90, 90, 73)
lon2d, lat2d = np.meshgrid(lon, lat)
data = 4.0 * np.sin(np.deg2rad(lon2d * 2.0)) * np.cos(np.deg2rad(lat2d))

field = ScalarField(data, lon=lon, lat=lat, name="demo")
plot = ContourMapPlot(
    field,
    res={
        "cnLevelSelectionMode": "ManualLevels",
        "cnMinLevelValF": -5,
        "cnMaxLevelValF": 5,
        "cnLevelSpacingF": 1,
        "cnFillPalette": "BlueWhiteOrangeRed",
        "mpGridAndLimbOn": True,
        "tiMainString": "object layer",
    },
)

fig, ax, out = plot.draw()
fig.savefig("demo_07_objects.png", bbox_inches="tight")
plt.close(fig)
print("saved demo_07_objects.png")
