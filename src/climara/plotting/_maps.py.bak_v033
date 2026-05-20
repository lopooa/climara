from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.path as mpath
import cartopy.crs as ccrs
import cartopy.feature as cfeature

from ._resources import bool_resource
from ._tickmark import apply_gridliner_labels, apply_plain_axis_ticks, build_grid_locators


def _infer_polar_latitude(mpres: dict):
    if "mpCenterLatF" in mpres:
        return float(mpres["mpCenterLatF"])

    if "mpMinLatF" in mpres and float(mpres["mpMinLatF"]) >= 0:
        return 90.0

    if "mpMaxLatF" in mpres and float(mpres["mpMaxLatF"]) <= 0:
        return -90.0

    return 90.0


def create_projection(mpres: dict | None = None):
    if mpres is None:
        mpres = {}

    proj = str(mpres.get("mpProjection", "CylindricalEquidistant"))
    center_lon = float(mpres.get("mpCenterLonF", 0.0))
    center_lat = float(mpres.get("mpCenterLatF", 0.0))

    proj_key = proj.lower()

    if proj_key in ["cylindricalequidistant", "cylindrical", "platecarree", "latlon"]:
        return ccrs.PlateCarree(central_longitude=center_lon)

    if proj_key in ["stereographic", "polarstereographic", "northpolarstereo", "southpolarstereo"]:
        polar_lat = _infer_polar_latitude(mpres)

        return ccrs.Stereographic(
            central_longitude=center_lon,
            central_latitude=polar_lat,
        )

    if proj_key == "orthographic":
        return ccrs.Orthographic(
            central_longitude=center_lon,
            central_latitude=center_lat,
        )

    if proj_key == "robinson":
        return ccrs.Robinson(central_longitude=center_lon)

    if proj_key == "mollweide":
        return ccrs.Mollweide(central_longitude=center_lon)

    if proj_key == "mercator":
        return ccrs.Mercator(central_longitude=center_lon)

    if proj_key in ["lambertconformal", "lambertconformalconic"]:
        standard_parallels = (
            float(mpres.get("mpLambertParallel1F", 33.0)),
            float(mpres.get("mpLambertParallel2F", 45.0)),
        )

        return ccrs.LambertConformal(
            central_longitude=center_lon,
            central_latitude=float(mpres.get("mpCenterLatF", 39.0)),
            standard_parallels=standard_parallels,
        )

    if proj_key in ["albersequalarea", "albers"]:
        standard_parallels = (
            float(mpres.get("mpLambertParallel1F", 20.0)),
            float(mpres.get("mpLambertParallel2F", 50.0)),
        )

        return ccrs.AlbersEqualArea(
            central_longitude=center_lon,
            central_latitude=center_lat,
            standard_parallels=standard_parallels,
        )

    raise ValueError(f"Unsupported map projection: {proj}")


def set_circular_boundary(ax):
    theta = np.linspace(0, 2 * np.pi, 200)
    center = [0.5, 0.5]
    radius = 0.5

    verts = np.vstack(
        [
            np.sin(theta) * radius + center[0],
            np.cos(theta) * radius + center[1],
        ]
    ).T

    circle = mpath.Path(verts)
    ax.set_boundary(circle, transform=ax.transAxes)


def _has_latlon_box(mpres):
    return all(
        key in mpres
        for key in ["mpMinLonF", "mpMaxLonF", "mpMinLatF", "mpMaxLatF"]
    )


def set_map_extent(ax, mpres: dict | None = None):
    if mpres is None:
        mpres = {}

    limit_mode = str(mpres.get("mpLimitMode", "")).lower()

    if _has_latlon_box(mpres) or limit_mode in ["latlon", "corners"]:
        if _has_latlon_box(mpres):
            ax.set_extent(
                [
                    float(mpres["mpMinLonF"]),
                    float(mpres["mpMaxLonF"]),
                    float(mpres["mpMinLatF"]),
                    float(mpres["mpMaxLatF"]),
                ],
                crs=ccrs.PlateCarree(),
            )
        return

    proj = str(mpres.get("mpProjection", "")).lower()

    if "stereo" in proj or proj == "stereographic":
        center_lat = _infer_polar_latitude(mpres)

        if center_lat >= 0:
            min_lat = float(mpres.get("mpMinLatF", 20.0))
            ax.set_extent([-180, 180, min_lat, 90], crs=ccrs.PlateCarree())
        else:
            max_lat = float(mpres.get("mpMaxLatF", -20.0))
            ax.set_extent([-180, 180, -90, max_lat], crs=ccrs.PlateCarree())

        if bool_resource(mpres, "mpPolarBoundaryOn", True):
            set_circular_boundary(ax)


def _apply_map_fill(ax, mpres):
    fill_on = bool_resource(mpres, "mpFillOn", False)

    if not fill_on:
        return []

    artists = []

    ocean = mpres.get("mpOceanFillColor", None)
    land = mpres.get("mpLandFillColor", None)
    inland = mpres.get("mpInlandWaterFillColor", None)

    if ocean is not None:
        artists.append(
            ax.add_feature(
                cfeature.OCEAN,
                facecolor=ocean,
                edgecolor="none",
                zorder=float(mpres.get("mpOceanFillZOrder", 0)),
            )
        )

    if land is not None:
        artists.append(
            ax.add_feature(
                cfeature.LAND,
                facecolor=land,
                edgecolor="none",
                zorder=float(mpres.get("mpLandFillZOrder", 1)),
            )
        )

    if inland is not None:
        artists.append(
            ax.add_feature(
                cfeature.LAKES,
                facecolor=inland,
                edgecolor=mpres.get("mpInlandWaterEdgeColor", "none"),
                linewidth=float(mpres.get("mpInlandWaterLineThicknessF", 0.2)),
                zorder=float(mpres.get("mpInlandWaterFillZOrder", 1.5)),
            )
        )

    return artists


def _apply_perimeter(ax, mpres):
    perim_on = bool_resource(mpres, "mpPerimOn", True)

    try:
        ax.outline_patch.set_visible(perim_on)
    except Exception:
        pass

    for spine in getattr(ax, "spines", {}).values():
        spine.set_visible(perim_on)

        if "mpPerimLineColor" in mpres:
            spine.set_edgecolor(mpres["mpPerimLineColor"])

        if "mpPerimLineThicknessF" in mpres:
            spine.set_linewidth(float(mpres["mpPerimLineThicknessF"]))


def add_map_features(ax, mpres: dict | None = None):
    if mpres is None:
        mpres = {}

    fill_artists = _apply_map_fill(ax, mpres)

    outline_on = bool_resource(mpres, "mpOutlineOn", True)
    grid_on = bool_resource(mpres, "mpGridAndLimbOn", False)
    borders_on = bool_resource(mpres, "mpNationalLineOn", False)

    coastline = None
    borders = None

    if outline_on:
        coastline = ax.coastlines(
            resolution=mpres.get("mpDataResolution", "110m"),
            color=mpres.get("mpGeophysicalLineColor", "0.25"),
            linewidth=float(mpres.get("mpGeophysicalLineThicknessF", 0.8)),
            zorder=float(mpres.get("mpGeophysicalLineZOrder", 6)),
        )

    if borders_on:
        borders = ax.add_feature(
            cfeature.BORDERS,
            edgecolor=mpres.get("mpNationalLineColor", "0.45"),
            linewidth=float(mpres.get("mpNationalLineThicknessF", 0.3)),
            zorder=float(mpres.get("mpNationalLineZOrder", 6)),
        )

    gl = None

    if grid_on:
        xlocs, ylocs = build_grid_locators(mpres)

        gl = ax.gridlines(
            crs=ccrs.PlateCarree(),
            draw_labels=bool_resource(mpres, "mpGridLabelsOn", False),
            linewidth=float(mpres.get("mpGridLineThicknessF", 0.4)),
            color=mpres.get("mpGridLineColor", "0.6"),
            alpha=float(mpres.get("mpGridLineAlphaF", 0.6)),
            linestyle=mpres.get("mpGridLineDashPattern", "--"),
            zorder=float(mpres.get("mpGridLineZOrder", 2)),
            xlocs=xlocs,
            ylocs=ylocs,
        )

        apply_gridliner_labels(gl, mpres)

    _apply_perimeter(ax, mpres)
    apply_plain_axis_ticks(ax, mpres)

    return {
        "fill_artists": fill_artists,
        "coastline": coastline,
        "borders": borders,
        "gridliner": gl,
    }


def create_map_axes(fig=None, ax=None, mpres: dict | None = None, subplot=111):
    if fig is None:
        fig = plt.figure(figsize=(8, 5))

    if ax is None:
        projection = create_projection(mpres)
        ax = fig.add_subplot(subplot, projection=projection)

    set_map_extent(ax, mpres)
    add_map_features(ax, mpres)

    return fig, ax
