
from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.path as mpath
import cartopy.crs as ccrs
import cartopy.feature as cfeature

from ._resources import bool_resource
from ._colors import ncl_color_to_mpl
from ._tickmark import apply_gridliner_labels, apply_plain_axis_ticks, build_grid_locators
import matplotlib.patches as mpatches


_PROJECTION_ALIASES = {
    "cylindricalequidistant": "platecarree",
    "cylindrical": "platecarree",
    "platecarree": "platecarree",
    "latlon": "platecarree",
    "equidistantcylindrical": "platecarree",
    "robinson": "robinson",
    "mollweide": "mollweide",
    "mercator": "mercator",
    "orthographic": "orthographic",
    "stereographic": "stereographic",
    "polarstereographic": "stereographic",
    "northpolarstereo": "stereographic",
    "southpolarstereo": "stereographic",
    "lambertconformal": "lambertconformal",
    "lambertconformalconic": "lambertconformal",
    "albers": "albers",
    "albersequalarea": "albers",
    "lambertazimuthal": "lambertazimuthal",
    "lambertazimuthalequalarea": "lambertazimuthal",
    "laea": "lambertazimuthal",
    "azimuthalequidistant": "azimuthalequidistant",
    "aeqd": "azimuthalequidistant",
    "transversemercator": "transversemercator",
    "utm": "transversemercator",
    "nearsideperspective": "nearsideperspective",
    "geostationary": "geostationary",
    "goode": "interruptedgoodehomolosine",
    "interruptedgoodehomolosine": "interruptedgoodehomolosine",
    "equalearth": "equalearth",
    "sinusoidal": "sinusoidal",
    "rotatedpole": "rotatedpole",
}


def _projection_key(value):
    text = str(value or "CylindricalEquidistant")
    text = text.replace("_", "").replace("-", "").replace(" ", "").lower()
    return _PROJECTION_ALIASES.get(text, text)


def _cartopy_class(name):
    return getattr(ccrs, name, None)


def _float(mpres, key, default):
    return float(mpres.get(key, default))


def _infer_polar_latitude(mpres: dict):
    if "mpCenterLatF" in mpres:
        return float(mpres["mpCenterLatF"])

    if "mpMinLatF" in mpres and float(mpres["mpMinLatF"]) >= 0:
        return 90.0

    if "mpMaxLatF" in mpres and float(mpres["mpMaxLatF"]) <= 0:
        return -90.0

    proj = str(mpres.get("mpProjection", "")).lower()

    if "south" in proj:
        return -90.0

    return 90.0


def list_supported_projections():
    names = []

    for key in sorted(set(_PROJECTION_ALIASES.values())):
        if key in ["equalearth", "sinusoidal", "azimuthalequidistant", "nearsideperspective", "geostationary", "interruptedgoodehomolosine"]:
            class_name = {
                "equalearth": "EqualEarth",
                "sinusoidal": "Sinusoidal",
                "azimuthalequidistant": "AzimuthalEquidistant",
                "nearsideperspective": "NearsidePerspective",
                "geostationary": "Geostationary",
                "interruptedgoodehomolosine": "InterruptedGoodeHomolosine",
            }[key]
            if _cartopy_class(class_name) is None:
                continue
        names.append(key)

    return names


def create_projection(mpres: dict | None = None):
    if mpres is None:
        mpres = {}

    key = _projection_key(mpres.get("mpProjection", "CylindricalEquidistant"))
    center_lon = _float(mpres, "mpCenterLonF", 0.0)
    center_lat = _float(mpres, "mpCenterLatF", 0.0)

    if key == "platecarree":
        return ccrs.PlateCarree(central_longitude=center_lon)

    if key == "stereographic":
        polar_lat = _infer_polar_latitude(mpres)
        return ccrs.Stereographic(
            central_longitude=center_lon,
            central_latitude=polar_lat,
            true_scale_latitude=mpres.get("mpTrueScaleLatF", None),
        )

    if key == "orthographic":
        return ccrs.Orthographic(
            central_longitude=center_lon,
            central_latitude=center_lat,
        )

    if key == "robinson":
        return ccrs.Robinson(central_longitude=center_lon)

    if key == "mollweide":
        return ccrs.Mollweide(central_longitude=center_lon)

    if key == "mercator":
        return ccrs.Mercator(
            central_longitude=center_lon,
            min_latitude=mpres.get("mpMercatorMinLatF", None),
            max_latitude=mpres.get("mpMercatorMaxLatF", None),
        )

    if key == "lambertconformal":
        standard_parallels = (
            _float(mpres, "mpLambertParallel1F", 33.0),
            _float(mpres, "mpLambertParallel2F", 45.0),
        )
        return ccrs.LambertConformal(
            central_longitude=center_lon,
            central_latitude=_float(mpres, "mpCenterLatF", 39.0),
            standard_parallels=standard_parallels,
        )

    if key == "albers":
        standard_parallels = (
            _float(mpres, "mpLambertParallel1F", 20.0),
            _float(mpres, "mpLambertParallel2F", 50.0),
        )
        return ccrs.AlbersEqualArea(
            central_longitude=center_lon,
            central_latitude=center_lat,
            standard_parallels=standard_parallels,
        )

    if key == "lambertazimuthal":
        return ccrs.LambertAzimuthalEqualArea(
            central_longitude=center_lon,
            central_latitude=center_lat,
        )

    if key == "azimuthalequidistant":
        cls = _cartopy_class("AzimuthalEquidistant")
        if cls is not None:
            return cls(central_longitude=center_lon, central_latitude=center_lat)

    if key == "transversemercator":
        return ccrs.TransverseMercator(
            central_longitude=center_lon,
            central_latitude=center_lat,
            false_easting=_float(mpres, "mpFalseEastingF", 0.0),
            false_northing=_float(mpres, "mpFalseNorthingF", 0.0),
            scale_factor=_float(mpres, "mpScaleFactorF", 1.0),
        )

    if key == "nearsideperspective":
        cls = _cartopy_class("NearsidePerspective")
        if cls is not None:
            return cls(
                central_longitude=center_lon,
                central_latitude=center_lat,
                satellite_height=_float(mpres, "mpSatelliteHeightF", 35785831.0),
            )

    if key == "geostationary":
        cls = _cartopy_class("Geostationary")
        if cls is not None:
            return cls(
                central_longitude=center_lon,
                satellite_height=_float(mpres, "mpSatelliteHeightF", 35785831.0),
            )

    if key == "interruptedgoodehomolosine":
        cls = _cartopy_class("InterruptedGoodeHomolosine")
        if cls is not None:
            return cls(central_longitude=center_lon)

    if key == "equalearth":
        cls = _cartopy_class("EqualEarth")
        if cls is not None:
            return cls(central_longitude=center_lon)

    if key == "sinusoidal":
        cls = _cartopy_class("Sinusoidal")
        if cls is not None:
            return cls(central_longitude=center_lon)

    if key == "rotatedpole":
        return ccrs.RotatedPole(
            pole_longitude=_float(mpres, "mpPoleLonF", 180.0),
            pole_latitude=_float(mpres, "mpPoleLatF", 45.0),
            central_rotated_longitude=_float(mpres, "mpCenterRotatedLonF", 0.0),
        )

    supported = ", ".join(list_supported_projections())
    unsupported = mpres.get("mpProjection")
    raise ValueError(f"Unsupported map projection: {unsupported}. Supported keys include: {supported}")


def set_circular_boundary(ax):
    theta = np.linspace(0, 2 * np.pi, 240)
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
    proj_key = _projection_key(mpres.get("mpProjection", ""))

    if limit_mode in ["global", "maximalarea", "all"]:
        try:
            ax.set_global()
        except Exception:
            pass
        return

    if _has_latlon_box(mpres) or limit_mode in ["latlon", "corners"]:
        if _has_latlon_box(mpres):
            ax.set_extent(
                [
                    _float(mpres, "mpMinLonF", -180.0),
                    _float(mpres, "mpMaxLonF", 180.0),
                    _float(mpres, "mpMinLatF", -90.0),
                    _float(mpres, "mpMaxLatF", 90.0),
                ],
                crs=ccrs.PlateCarree(),
            )
        return

    if proj_key == "stereographic":
        center_lat = _infer_polar_latitude(mpres)

        if center_lat >= 0:
            min_lat = _float(mpres, "mpMinLatF", 20.0)
            ax.set_extent([-180, 180, min_lat, 90], crs=ccrs.PlateCarree())
        else:
            max_lat = _float(mpres, "mpMaxLatF", -20.0)
            ax.set_extent([-180, 180, -90, max_lat], crs=ccrs.PlateCarree())

        if bool_resource(mpres, "mpPolarBoundaryOn", True):
            set_circular_boundary(ax)

        return

    try:
        ax.set_global()
    except Exception:
        pass



def _is_curved_global_projection(mpres):
    key = _projection_key(mpres.get("mpProjection", ""))

    curved = {
        "robinson",
        "mollweide",
        "orthographic",
        "interruptedgoodehomolosine",
        "equalearth",
        "sinusoidal",
        "nearsideperspective",
        "geostationary",
    }

    if key in curved:
        return True

    return False


def _safe_grid_draw_labels(mpres):
    try:
        if _is_polar_map(mpres) and bool_resource(mpres, "gsnPolarLabelOn", True):
            return False
    except NameError:
        pass

    if not bool_resource(mpres, "mpGridLabelsOn", False):
        return False

    if bool_resource(mpres, "mpGridLabelsAutoOffForCurvedGlobal", True):
        if _is_curved_global_projection(mpres):
            return False

    return True

def _feature_with_scale(feature, resolution):
    try:
        return feature.with_scale(resolution)
    except Exception:
        return feature


def _add_feature(ax, feature, resolution, **kwargs):
    return ax.add_feature(_feature_with_scale(feature, resolution), **kwargs)


def _apply_map_fill(ax, mpres):
    if not bool_resource(mpres, "mpFillOn", False):
        return []

    resolution = mpres.get("mpDataResolution", "110m")
    artists = []

    ocean = mpres.get("mpOceanFillColor", "white")
    land = mpres.get("mpLandFillColor", "0.95")
    inland = mpres.get("mpInlandWaterFillColor", mpres.get("mpLakeFillColor", None))

    if ocean is not None and str(ocean).lower() != "transparent":
        artists.append(
            _add_feature(
                ax,
                cfeature.OCEAN,
                resolution,
                facecolor=ocean,
                edgecolor="none",
                zorder=_float(mpres, "mpOceanFillZOrder", 0.0),
            )
        )

    if land is not None and str(land).lower() != "transparent":
        artists.append(
            _add_feature(
                ax,
                cfeature.LAND,
                resolution,
                facecolor=land,
                edgecolor="none",
                zorder=_float(mpres, "mpLandFillZOrder", 1.0),
            )
        )

    if inland is not None and str(inland).lower() != "transparent":
        artists.append(
            _add_feature(
                ax,
                cfeature.LAKES,
                resolution,
                facecolor=inland,
                edgecolor=mpres.get("mpInlandWaterEdgeColor", "none"),
                linewidth=_float(mpres, "mpInlandWaterLineThicknessF", 0.2),
                zorder=_float(mpres, "mpInlandWaterFillZOrder", 1.5),
            )
        )

    return artists


def _apply_perimeter(ax, mpres):
    perim_on = bool_resource(mpres, "mpPerimOn", True)

    hide_rect_frame = bool_resource(mpres, "mpHideRectangularFrameForCurvedGlobal", True)
    hide_rect_frame = hide_rect_frame and _is_curved_global_projection(mpres)

    for attr in ["outline_patch", "background_patch"]:
        try:
            getattr(ax, attr).set_visible(perim_on)
        except Exception:
            pass

    for name, spine in getattr(ax, "spines", {}).items():
        try:
            if hide_rect_frame and name != "geo":
                spine.set_visible(False)
            else:
                spine.set_visible(perim_on)
        except Exception:
            pass

        if "mpPerimLineColor" in mpres:
            try:
                spine.set_edgecolor(mpres["mpPerimLineColor"])
            except Exception:
                pass

        if "mpPerimLineThicknessF" in mpres:
            try:
                spine.set_linewidth(_float(mpres, "mpPerimLineThicknessF", 0.8))
            except Exception:
                pass



def _clear_plain_axis_ticks(ax):
    try:
        ax.set_xticks([])
        ax.set_yticks([])
    except Exception:
        pass

    try:
        ax.tick_params(
            bottom=False,
            top=False,
            left=False,
            right=False,
            labelbottom=False,
            labeltop=False,
            labelleft=False,
            labelright=False,
        )
    except Exception:
        pass

    try:
        labels = ax.get_xticklabels() + ax.get_yticklabels()
    except Exception:
        labels = []

    for label in labels:
        try:
            label.set_visible(False)
        except Exception:
            pass


def _should_apply_plain_axis_ticks(mpres):
    if "tmPlainAxisTicksOn" in mpres:
        return bool_resource(mpres, "tmPlainAxisTicksOn", True)

    if _is_curved_global_projection(mpres):
        if not bool_resource(mpres, "mpGridLabelsOn", False):
            return False

    return True

def add_map_features(ax, mpres: dict | None = None):
    if mpres is None:
        mpres = {}

    mpres = _expand_outline_boundary_sets(mpres)

    resolution = mpres.get("mpDataResolution", "110m")
    fill_artists = _apply_map_fill(ax, mpres)

    outline_on = bool_resource(mpres, "mpOutlineOn", True)
    coast_on = bool_resource(mpres, "mpCoastlineOn", outline_on)
    borders_on = bool_resource(mpres, "mpNationalLineOn", False)
    states_on = bool_resource(mpres, "mpUSStateLineOn", False)
    lakes_on = bool_resource(mpres, "mpLakeLineOn", False)
    rivers_on = bool_resource(mpres, "mpRiverLineOn", False)

    coastline = None
    borders = None
    states = None
    lakes = None
    rivers = None

    if coast_on:
        coastline = ax.coastlines(
            resolution=resolution,
            color=mpres.get("mpGeophysicalLineColor", mpres.get("mpCoastlineColor", "0.25")),
            linewidth=_float(mpres, "mpGeophysicalLineThicknessF", mpres.get("mpCoastlineThicknessF", 0.8)),
            zorder=_float(mpres, "mpGeophysicalLineZOrder", 6.0),
        )

    if borders_on:
        borders = _add_feature(
            ax,
            cfeature.BORDERS,
            resolution,
            edgecolor=mpres.get("mpNationalLineColor", "0.45"),
            linewidth=_float(mpres, "mpNationalLineThicknessF", 0.3),
            facecolor="none",
            zorder=_float(mpres, "mpNationalLineZOrder", 6.0),
        )

    if states_on and hasattr(cfeature, "STATES"):
        states = _add_feature(
            ax,
            cfeature.STATES,
            resolution,
            edgecolor=mpres.get("mpUSStateLineColor", "0.55"),
            linewidth=_float(mpres, "mpUSStateLineThicknessF", 0.25),
            facecolor="none",
            zorder=_float(mpres, "mpUSStateLineZOrder", 6.0),
        )

    if lakes_on:
        lakes = _add_feature(
            ax,
            cfeature.LAKES,
            resolution,
            edgecolor=mpres.get("mpLakeLineColor", "0.45"),
            linewidth=_float(mpres, "mpLakeLineThicknessF", 0.3),
            facecolor="none",
            zorder=_float(mpres, "mpLakeLineZOrder", 5.0),
        )

    if rivers_on:
        rivers = _add_feature(
            ax,
            cfeature.RIVERS,
            resolution,
            edgecolor=mpres.get("mpRiverLineColor", "0.45"),
            linewidth=_float(mpres, "mpRiverLineThicknessF", 0.3),
            facecolor="none",
            zorder=_float(mpres, "mpRiverLineZOrder", 5.0),
        )

    gl = None
    grid_on = (
        bool_resource(mpres, "mpGridAndLimbOn", False)
        or bool_resource(mpres, "mpGridOn", False)
        or bool_resource(mpres, "mpGridLineOn", False)
        or bool_resource(mpres, "mpGridLabelsOn", False)
    )

    if grid_on:
        xlocs, ylocs = build_grid_locators(mpres)

        gl = ax.gridlines(
            crs=ccrs.PlateCarree(),
            draw_labels=_safe_grid_draw_labels(mpres),
            linewidth=_float(mpres, "mpGridLineThicknessF", 0.4),
            color=mpres.get("mpGridLineColor", "0.6"),
            alpha=_float(mpres, "mpGridLineAlphaF", 0.6),
            linestyle=_normalize_dash_pattern(mpres.get("mpGridLineDashPattern", "--")),
            zorder=_float(mpres, "mpGridLineZOrder", 2.0),
            xlocs=xlocs,
            ylocs=ylocs,
        )

        apply_gridliner_labels(gl, mpres)

    _apply_perimeter(ax, mpres)

    if _should_apply_plain_axis_ticks(mpres):
        apply_plain_axis_ticks(ax, mpres)
    else:
        _clear_plain_axis_ticks(ax)

    return {
        "fill_artists": fill_artists,
        "coastline": coastline,
        "borders": borders,
        "states": states,
        "lakes": lakes,
        "rivers": rivers,
        "gridliner": gl,
    }



def _normalize_dash_pattern(value):
    dash_map = {
        0: "solid",
        1: "dashed",
        2: "dotted",
        3: "dashdot",
        4: "dashed",
        "0": "solid",
        "1": "dashed",
        "2": "dotted",
        "3": "dashdot",
        "4": "dashed",
        "solid": "solid",
        "dash": "dashed",
        "dashed": "dashed",
        "dot": "dotted",
        "dotted": "dotted",
        "dashdot": "dashdot",
        "--": "--",
        "-": "-",
        ":": ":",
        "-.": "-.",
    }

    if isinstance(value, str):
        key = value.strip().lower()
        return dash_map.get(key, value)

    return dash_map.get(value, value)


def _expand_outline_boundary_sets(mpres):
    mpres = dict(mpres or {})
    value = mpres.get("mpOutlineBoundarySets", None)

    if value is None:
        return mpres

    key = str(value).replace("_", "").replace("-", "").replace(" ", "").lower()

    if key in ["none", "no", "false", "off"]:
        mpres.setdefault("mpOutlineOn", False)
        mpres.setdefault("mpNationalLineOn", False)
        mpres.setdefault("mpUSStateLineOn", False)
        return mpres

    if key in ["geophysical", "geophysicalboundarysets"]:
        mpres.setdefault("mpOutlineOn", True)
        return mpres

    if key in [
        "national",
        "nationalboundaries",
        "geophysicalandnational",
        "geophysicalandnationalboundaries",
    ]:
        mpres.setdefault("mpOutlineOn", True)
        mpres.setdefault("mpNationalLineOn", True)
        return mpres

    if key in [
        "allboundaries",
        "all",
        "geophysicalandusstates",
        "geophysicalandusstatesboundaries",
    ]:
        mpres.setdefault("mpOutlineOn", True)
        mpres.setdefault("mpNationalLineOn", True)
        mpres.setdefault("mpUSStateLineOn", True)
        return mpres

    mpres.setdefault("mpOutlineOn", True)

    return mpres


def _is_polar_map(mpres):
    if bool_resource(mpres, "gsnPolar", False):
        return True

    key = _projection_key(mpres.get("mpProjection", ""))

    if key != "stereographic":
        return False

    center_lat = _infer_polar_latitude(mpres)

    return abs(center_lat) >= 60


def _polar_hemisphere(mpres):
    center_lat = _infer_polar_latitude(mpres)

    if center_lat < 0:
        return "SH"

    return "NH"


def _polar_edge_latitude(mpres):
    hemisphere = _polar_hemisphere(mpres)

    if hemisphere == "SH":
        return _float(mpres, "mpMaxLatF", -20.0)

    return _float(mpres, "mpMinLatF", 20.0)


def _format_latitude_label(value):
    value = float(value)
    hemi = "N" if value >= 0 else "S"
    value = abs(value)

    if abs(value - round(value)) < 1e-6:
        return f"{int(round(value))}°{hemi}"

    return f"{value:g}°{hemi}"


def _format_longitude_label(value):
    value = float(value)
    value = ((value + 180.0) % 360.0) - 180.0

    if abs(value) < 1e-6:
        return "0°"

    if abs(abs(value) - 180.0) < 1e-6:
        return "180°"

    if value > 0:
        return f"{int(round(value))}°E"

    return f"{int(round(abs(value)))}°W"


def _polar_label_positions(mpres):
    center_lon = _float(mpres, "mpCenterLonF", 0.0)
    hemisphere = _polar_hemisphere(mpres)
    sign = 1.0 if hemisphere == "NH" else -1.0

    longitudes = mpres.get("gsnPolarLongitudeLabelValues", None)

    if longitudes is None:
        longitudes = [0.0, 90.0, 180.0, -90.0]

    if isinstance(longitudes, str):
        longitudes = longitudes.replace(",", " ").split()

    longitudes = [float(v) for v in longitudes]

    distance = float(mpres.get("gsnPolarLabelDistance", 1.08))
    radius = 0.5 * distance

    out = []

    for lon in longitudes:
        angle = np.deg2rad(lon - center_lon)
        x = 0.5 + radius * np.sin(angle)
        y = 0.5 + sign * radius * np.cos(angle)

        if abs(x - 0.5) < 0.05:
            ha = "center"
        elif x < 0.5:
            ha = "right"
        else:
            ha = "left"

        if abs(y - 0.5) < 0.05:
            va = "center"
        elif y < 0.5:
            va = "top"
        else:
            va = "bottom"

        if bool_resource(mpres, "gsnPolarClampBottomLabelsOn", True) and y < 0:
            y = float(mpres.get("gsnPolarBottomLabelYF", 0.025))
            va = "bottom"

        out.append((x, y, _format_longitude_label(lon), ha, va))

    return out



def add_polar_boundary(ax, mpres=None):
    """Apply an NCL-like circular boundary for polar stereographic maps."""
    mpres = dict(mpres or {})

    if not _is_polar_map(mpres):
        return None

    if not bool_resource(mpres, "mpPolarBoundaryOn", True):
        return None

    theta = np.linspace(0, 2 * np.pi, 240)
    center = np.array([0.5, 0.5])
    radius = float(mpres.get("mpPolarBoundaryRadiusF", 0.5))

    verts = np.vstack(
        [
            np.sin(theta) * radius + center[0],
            np.cos(theta) * radius + center[1],
        ]
    ).T

    circle_path = mpath.Path(verts)
    ax.set_boundary(circle_path, transform=ax.transAxes)

    if bool_resource(mpres, "mpPolarHideRectangularFrameOn", True):
        for spine in ax.spines.values():
            try:
                spine.set_visible(False)
            except Exception:
                pass

    if not bool_resource(mpres, "mpPerimOn", True):
        return None

    circle = mpatches.Circle(
        (0.5, 0.5),
        radius,
        transform=ax.transAxes,
        fill=False,
        linewidth=float(mpres.get("mpPerimLineThicknessF", 0.8)),
        edgecolor=mpres.get("mpPerimLineColor", "black"),
        zorder=float(mpres.get("mpPerimZOrder", 25.0)),
        clip_on=False,
    )

    ax.add_patch(circle)

    return circle


def add_polar_labels(ax, mpres=None):
    mpres = dict(mpres or {})

    if not _is_polar_map(mpres):
        return []

    if not bool_resource(mpres, "gsnPolarLabelOn", True):
        return []

    artists = []
    fontsize = float(mpres.get("gsnPolarLabelFontHeightF", 9.0))
    color = mpres.get("gsnPolarLabelFontColor", mpres.get("tmXBLabelFontColor", "black"))
    zorder = float(mpres.get("gsnPolarLabelZOrder", 30.0))

    if bool_resource(mpres, "gsnPolarLongitudeLabelsOn", True):
        for x, y, label, ha, va in _polar_label_positions(mpres):
            artist = ax.text(
                x,
                y,
                label,
                transform=ax.transAxes,
                ha=ha,
                va=va,
                fontsize=fontsize,
                color=color,
                clip_on=False,
                rotation=float(mpres.get("gsnPolarLongitudeLabelAngleF", 0.0)),
                rotation_mode="anchor",
                zorder=zorder,
            )
            artists.append(artist)

    if bool_resource(mpres, "gsnPolarLatitudeLabelOn", True):
        edge_lat = _polar_edge_latitude(mpres)
        label = mpres.get("gsnPolarLatitudeLabelString", _format_latitude_label(edge_lat))
        position = str(mpres.get("gsnPolarLatitudeLabelPosition", "inside_bottom")).lower()
        distance = float(mpres.get("gsnPolarLatitudeLabelDistance", mpres.get("gsnPolarLabelDistance", 1.08)))

        if position in ["inside_bottom", "inner_bottom", "bottom_inside"]:
            x = 0.5
            y = float(mpres.get("gsnPolarLatitudeLabelYF", 0.115))
            ha, va = "center", "bottom"
        elif position in ["inside_top", "inner_top", "top_inside"]:
            x = 0.5
            y = float(mpres.get("gsnPolarLatitudeLabelYF", 0.115))
            ha, va = "center", "top"
        elif position == "top":
            x, y, ha, va = 0.5, 0.5 + 0.5 * distance, "center", "bottom"
        elif position == "left":
            x, y, ha, va = 0.5 - 0.5 * distance, 0.5, "right", "center"
        elif position == "right":
            x, y, ha, va = 0.5 + 0.5 * distance, 0.5, "left", "center"
        else:
            x, y, ha, va = 0.5, 0.5 - 0.5 * distance, "center", "top"

        artist = ax.text(
            x,
            y,
            str(label),
            transform=ax.transAxes,
            ha=ha,
            va=va,
            fontsize=fontsize,
            color=color,
            clip_on=False,
            zorder=zorder,
        )
        artists.append(artist)

    return artists


def create_map_axes(fig=None, ax=None, mpres: dict | None = None, subplot=111):
    if fig is None:
        fig = plt.figure(figsize=(8, 5))

    if ax is None:
        projection = create_projection(mpres)
        ax = fig.add_subplot(subplot, projection=projection)

    set_map_extent(ax, mpres)
    add_map_features(ax, mpres)
    add_polar_boundary(ax, mpres)
    add_polar_labels(ax, mpres)

    return fig, ax

# climara v0.3.0 polar label override begin

def _climara_polar_is_map(mpres=None):
    mpres = dict(mpres or {})

    if bool_resource(mpres, "gsnPolar", False):
        return True

    key = _projection_key(mpres.get("mpProjection", ""))

    if key != "stereographic":
        return False

    try:
        center_lat = _infer_polar_latitude(mpres)
    except Exception:
        center_lat = float(mpres.get("mpCenterLatF", 90.0))

    return abs(center_lat) >= 60.0


def _climara_polar_hemisphere(mpres=None):
    mpres = dict(mpres or {})

    try:
        center_lat = _infer_polar_latitude(mpres)
    except Exception:
        center_lat = float(mpres.get("mpCenterLatF", 90.0))

    if center_lat < 0:
        return "SH"

    return "NH"


def _climara_polar_format_lon(value):
    value = float(value)
    value = ((value + 180.0) % 360.0) - 180.0

    if abs(value) < 1e-8:
        return "0°"

    if abs(abs(value) - 180.0) < 1e-8:
        return "180°"

    if value > 0:
        return f"{int(round(value))}°E"

    return f"{int(round(abs(value)))}°W"


def _climara_polar_format_lat(value):
    value = float(value)
    hemi = "N" if value >= 0 else "S"
    value = abs(value)

    if abs(value - round(value)) < 1e-8:
        return f"{int(round(value))}°{hemi}"

    return f"{value:g}°{hemi}"


def _climara_polar_edge_lat(mpres=None):
    mpres = dict(mpres or {})
    hemi = _climara_polar_hemisphere(mpres)

    if hemi == "SH":
        return float(mpres.get("mpMaxLatF", -20.0))

    return float(mpres.get("mpMinLatF", 20.0))


def _climara_polar_lon_labels(mpres=None):
    mpres = dict(mpres or {})
    hemi = _climara_polar_hemisphere(mpres)
    center_lon = float(mpres.get("mpCenterLonF", 0.0))

    if hemi == "SH":
        top = center_lon + 180.0
        bottom = center_lon
    else:
        top = center_lon
        bottom = center_lon + 180.0

    left = center_lon - 90.0
    right = center_lon + 90.0

    return {
        "top": _climara_polar_format_lon(top),
        "bottom": _climara_polar_format_lon(bottom),
        "left": _climara_polar_format_lon(left),
        "right": _climara_polar_format_lon(right),
    }


def _climara_polar_label_padding(mpres, axis):
    if axis == "x":
        return float(
            mpres.get(
                "gsnPolarLongitudeLabelXPaddingF",
                mpres.get("gsnPolarLongitudeLabelPaddingF", 0.025),
            )
        )

    return float(
        mpres.get(
            "gsnPolarLongitudeLabelYPaddingF",
            mpres.get("gsnPolarLongitudeLabelPaddingF", 0.025),
        )
    )


try:
    _climara_v030_base_add_map_features
except NameError:
    _climara_v030_base_add_map_features = add_map_features


def add_map_features(ax, mpres=None):
    mpres = dict(mpres or {})

    if _climara_polar_is_map(mpres):
        mpres["mpGridLabelsOn"] = False

    return _climara_v030_base_add_map_features(ax, mpres)


def _climara_clear_old_polar_labels(ax):
    for old in list(getattr(ax, "texts", [])):
        try:
            if getattr(old, "_climara_polar_label", False):
                old.remove()
        except Exception:
            pass


def _climara_add_axes_text(ax, x, y, text, ha, va, fontsize, color, zorder, rotation=0.0):
    artist = ax.text(
        x,
        y,
        text,
        transform=ax.transAxes,
        ha=ha,
        va=va,
        fontsize=fontsize,
        color=color,
        rotation=rotation,
        rotation_mode="anchor",
        clip_on=False,
        zorder=zorder,
    )
    artist._climara_polar_label = True

    return artist


def add_polar_labels(ax, mpres=None):
    mpres = dict(mpres or {})

    if not _climara_polar_is_map(mpres):
        return []

    if not bool_resource(mpres, "gsnPolarLabelOn", True):
        return []

    artists = []

    fontsize = float(mpres.get("gsnPolarLabelFontHeightF", 9.0))
    color = mpres.get(
        "gsnPolarLabelFontColor",
        mpres.get("tmXBLabelFontColor", "black"),
    )
    zorder = float(mpres.get("gsnPolarLabelZOrder", 50.0))

    _climara_clear_old_polar_labels(ax)

    labels = _climara_polar_lon_labels(mpres)

    xpad = _climara_polar_label_padding(mpres, "x")
    ypad = _climara_polar_label_padding(mpres, "y")

    top_y = float(mpres.get("gsnPolarTopLongitudeLabelYF", 1.0 + ypad))
    bottom_y = float(mpres.get("gsnPolarBottomLongitudeLabelYF", -ypad))
    left_x = float(mpres.get("gsnPolarLeftLongitudeLabelXF", -xpad))
    right_x = float(mpres.get("gsnPolarRightLongitudeLabelXF", 1.0 + xpad))

    if bool_resource(mpres, "gsnPolarLongitudeLabelsOn", True):
        specs = [
            (0.5, top_y, labels["top"], "center", "bottom"),
            (0.5, bottom_y, labels["bottom"], "center", "top"),
            (left_x, 0.5, labels["left"], "right", "center"),
            (right_x, 0.5, labels["right"], "left", "center"),
        ]

        for x, y, text, ha, va in specs:
            artists.append(
                _climara_add_axes_text(
                    ax,
                    x,
                    y,
                    text,
                    ha,
                    va,
                    fontsize,
                    color,
                    zorder,
                    rotation=float(mpres.get("gsnPolarLongitudeLabelAngleF", 0.0)),
                )
            )

    if bool_resource(mpres, "gsnPolarLatitudeLabelOn", True):
        edge_lat = _climara_polar_edge_lat(mpres)
        text = mpres.get(
            "gsnPolarLatitudeLabelString",
            _climara_polar_format_lat(edge_lat),
        )

        position = str(mpres.get("gsnPolarLatitudeLabelPosition", "inside_bottom")).lower()
        distance = float(mpres.get("gsnPolarLatitudeLabelDistance", 0.12))

        if position in ["inside_bottom", "inner_bottom", "bottom_inside"]:
            default_x, default_y = 0.5, distance
            ha, va = "center", "bottom"
        elif position in ["inside_top", "inner_top", "top_inside"]:
            default_x, default_y = 0.5, 1.0 - distance
            ha, va = "center", "top"
        elif position == "bottom":
            default_x, default_y = 0.5, -ypad
            ha, va = "center", "top"
        elif position == "top":
            default_x, default_y = 0.5, 1.0 + ypad
            ha, va = "center", "bottom"
        elif position == "left":
            default_x, default_y = -xpad, 0.5
            ha, va = "right", "center"
        elif position == "right":
            default_x, default_y = 1.0 + xpad, 0.5
            ha, va = "left", "center"
        else:
            default_x, default_y = 0.5, distance
            ha, va = "center", "bottom"

        lat_x = float(mpres.get("gsnPolarLatitudeLabelXF", default_x))
        lat_y = float(mpres.get("gsnPolarLatitudeLabelYF", default_y))

        artists.append(
            _climara_add_axes_text(
                ax,
                lat_x,
                lat_y,
                str(text),
                ha,
                va,
                fontsize,
                color,
                zorder,
                rotation=float(mpres.get("gsnPolarLatitudeLabelAngleF", 0.0)),
            )
        )

    return artists

# climara v0.3.0 polar label override end

# climara v0.2.4 map resource override begin

def _v024_normalize_resolution(value):
    """Normalize NCL-like map data resolution names to Cartopy scales."""
    if value is None:
        return "110m"

    key = str(value).replace("_", "").replace("-", "").replace(" ", "").lower()

    aliases = {
        "low": "110m",
        "lowres": "110m",
        "coarse": "110m",
        "110m": "110m",

        "medium": "50m",
        "mediumres": "50m",
        "medres": "50m",
        "50m": "50m",

        "high": "10m",
        "highres": "10m",
        "fine": "10m",
        "10m": "10m",
    }

    return aliases.get(key, str(value))


def _v024_is_transparent_color(value):
    if value is None:
        return True

    key = str(value).strip().lower()

    return key in ["none", "transparent", "no", "false", "off"]


def _v024_expand_outline_boundary_sets(mpres):
    mpres = dict(mpres or {})
    value = mpres.get("mpOutlineBoundarySets", None)

    if value is None:
        return mpres

    key = str(value).replace("_", "").replace("-", "").replace(" ", "").lower()

    if key in ["none", "no", "false", "off"]:
        mpres["mpOutlineOn"] = False
        mpres["mpNationalLineOn"] = False
        mpres["mpUSStateLineOn"] = False
        return mpres

    if key in ["geophysical", "geophysicalboundarysets"]:
        mpres.setdefault("mpOutlineOn", True)
        return mpres

    if key in [
        "national",
        "nationalboundaries",
        "geophysicalandnational",
        "geophysicalandnationalboundaries",
    ]:
        mpres.setdefault("mpOutlineOn", True)
        mpres.setdefault("mpNationalLineOn", True)
        return mpres

    if key in [
        "all",
        "allboundaries",
        "allboundarysets",
        "geophysicalandusstates",
        "geophysicalandusstatesboundaries",
    ]:
        mpres.setdefault("mpOutlineOn", True)
        mpres.setdefault("mpNationalLineOn", True)
        mpres.setdefault("mpUSStateLineOn", True)
        return mpres

    mpres.setdefault("mpOutlineOn", True)

    return mpres


def _v024_add_map_fills(ax, mpres):
    import cartopy.feature as cfeature

    artists = []

    if not bool_resource(mpres, "mpFillOn", False):
        return artists

    scale = _v024_normalize_resolution(mpres.get("mpDataResolution", "110m"))

    ocean_color = mpres.get("mpOceanFillColor", "white")
    land_color = mpres.get("mpLandFillColor", "0.9")
    inland_water_color = mpres.get("mpInlandWaterFillColor", ocean_color)

    ocean_zorder = float(mpres.get("mpOceanFillZOrder", 0.0))
    land_zorder = float(mpres.get("mpLandFillZOrder", 1.0))
    inland_zorder = float(mpres.get("mpInlandWaterFillZOrder", 2.0))

    if not _v024_is_transparent_color(ocean_color):
        artists.append(
            ax.add_feature(
                cfeature.OCEAN.with_scale(scale),
                facecolor=ocean_color,
                edgecolor="none",
                zorder=ocean_zorder,
            )
        )

    if not _v024_is_transparent_color(land_color):
        artists.append(
            ax.add_feature(
                cfeature.LAND.with_scale(scale),
                facecolor=land_color,
                edgecolor="none",
                zorder=land_zorder,
            )
        )

    if not _v024_is_transparent_color(inland_water_color):
        artists.append(
            ax.add_feature(
                cfeature.LAKES.with_scale(scale),
                facecolor=inland_water_color,
                edgecolor="none",
                zorder=inland_zorder,
            )
        )

    return artists


def _v024_add_map_outlines(ax, mpres):
    import cartopy.feature as cfeature

    artists = []

    scale = _v024_normalize_resolution(mpres.get("mpDataResolution", "110m"))

    geo_color = mpres.get(
        "mpGeophysicalLineColor",
        mpres.get("mpOutlineLineColor", mpres.get("mpOutlineColor", "0.25")),
    )
    geo_width = float(
        mpres.get(
            "mpGeophysicalLineThicknessF",
            mpres.get("mpOutlineLineThicknessF", 0.8),
        )
    )
    geo_zorder = float(mpres.get("mpGeophysicalLineZOrder", 20.0))

    if bool_resource(mpres, "mpOutlineOn", True):
        try:
            coast = ax.coastlines(
                resolution=scale,
                color=geo_color,
                linewidth=geo_width,
                zorder=geo_zorder,
            )
            artists.append(coast)
        except Exception:
            artists.append(
                ax.add_feature(
                    cfeature.COASTLINE.with_scale(scale),
                    edgecolor=geo_color,
                    linewidth=geo_width,
                    facecolor="none",
                    zorder=geo_zorder,
                )
            )

    if bool_resource(mpres, "mpNationalLineOn", False):
        national_color = mpres.get("mpNationalLineColor", geo_color)
        national_width = float(mpres.get("mpNationalLineThicknessF", geo_width * 0.6))

        artists.append(
            ax.add_feature(
                cfeature.BORDERS.with_scale(scale),
                edgecolor=national_color,
                linewidth=national_width,
                facecolor="none",
                zorder=float(mpres.get("mpNationalLineZOrder", geo_zorder + 0.5)),
            )
        )

    if bool_resource(mpres, "mpUSStateLineOn", False):
        state_color = mpres.get("mpUSStateLineColor", mpres.get("mpNationalLineColor", geo_color))
        state_width = float(mpres.get("mpUSStateLineThicknessF", geo_width * 0.45))

        artists.append(
            ax.add_feature(
                cfeature.STATES.with_scale(scale),
                edgecolor=state_color,
                linewidth=state_width,
                facecolor="none",
                zorder=float(mpres.get("mpUSStateLineZOrder", geo_zorder + 0.75)),
            )
        )

    if bool_resource(mpres, "mpInlandWaterLineOn", False):
        water_color = mpres.get("mpInlandWaterLineColor", geo_color)
        water_width = float(mpres.get("mpInlandWaterLineThicknessF", geo_width * 0.5))

        artists.append(
            ax.add_feature(
                cfeature.LAKES.with_scale(scale),
                edgecolor=water_color,
                linewidth=water_width,
                facecolor="none",
                zorder=float(mpres.get("mpInlandWaterLineZOrder", geo_zorder + 0.25)),
            )
        )

    return artists


def _v024_apply_map_perimeter(ax, mpres):
    if not bool_resource(mpres, "mpPerimOn", True):
        for spine in ax.spines.values():
            try:
                spine.set_visible(False)
            except Exception:
                pass
        return []

    color = mpres.get("mpPerimLineColor", mpres.get("mpPerimColor", "black"))
    width = float(mpres.get("mpPerimLineThicknessF", 0.8))

    artists = []

    for spine in ax.spines.values():
        try:
            spine.set_visible(True)
            spine.set_edgecolor(color)
            spine.set_linewidth(width)
            artists.append(spine)
        except Exception:
            pass

    return artists


def _normalize_map_color_resources(mpres):
    """Normalize NCL-style map color resources before passing them to Matplotlib."""
    mpres = dict(mpres or {})

    for key, value in list(mpres.items()):
        if key.endswith("Color") or "Color" in key:
            mpres[key] = ncl_color_to_mpl(value)

    return mpres


try:
    _climara_v024_base_add_map_features
except NameError:
    _climara_v024_base_add_map_features = add_map_features


def add_map_features(ax, mpres=None):
    """Add map features with additional NCL-style MapPlot resources."""
    mpres = _v024_expand_outline_boundary_sets(dict(mpres or {}))
    mpres = _normalize_map_color_resources(mpres)

    artists = {
        "fills": [],
        "base": None,
        "outlines": [],
        "perimeter": [],
    }

    artists["fills"] = _v024_add_map_fills(ax, mpres)

    # Preserve previous behavior, including gridlines and polar-label safeguards.
    artists["base"] = _climara_v024_base_add_map_features(ax, mpres)

    # Add explicit high-zorder outlines so they remain visible over filled contours.
    artists["outlines"] = _v024_add_map_outlines(ax, mpres)
    artists["perimeter"] = _v024_apply_map_perimeter(ax, mpres)

    return artists

# climara v0.2.4 map resource override end
