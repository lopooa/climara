from __future__ import annotations

import numpy as np
import matplotlib.ticker as mticker

from ._resources import bool_resource


def _format_lon(x):
    x = float(x)

    if abs(x) < 1e-8:
        return "0°"

    if abs(abs(x) - 180) < 1e-8:
        return "180°"

    if x < 0:
        return f"{abs(int(x))}°W"

    return f"{int(x)}°E"


def _format_lat(y):
    y = float(y)

    if abs(y) < 1e-8:
        return "0°"

    if y < 0:
        return f"{abs(int(y))}°S"

    return f"{int(y)}°N"


def _fixed_locator_from_values(values):
    if values is None:
        return None

    return mticker.FixedLocator([float(v) for v in values])


def _fixed_locator_from_spacing(vmin, vmax, spacing):
    spacing = float(spacing)

    if spacing <= 0:
        return None

    start = np.ceil(vmin / spacing) * spacing
    values = np.arange(start, vmax + spacing * 0.5, spacing)

    return mticker.FixedLocator(values)


def build_grid_locators(res):
    """
    Build x/y locators from NCL-style tm/mp resources.
    """
    x_values = res.get("tmXBValues", res.get("mpGridLonValues", None))
    y_values = res.get("tmYLValues", res.get("mpGridLatValues", None))

    xlocs = _fixed_locator_from_values(x_values)
    ylocs = _fixed_locator_from_values(y_values)

    if xlocs is None:
        lon_spacing = res.get("mpGridLonSpacingF", res.get("mpGridSpacingF", None))

        if lon_spacing is not None:
            xlocs = _fixed_locator_from_spacing(-180, 180, lon_spacing)

    if ylocs is None:
        lat_spacing = res.get("mpGridLatSpacingF", res.get("mpGridSpacingF", None))

        if lat_spacing is not None:
            ylocs = _fixed_locator_from_spacing(-90, 90, lat_spacing)

    return xlocs, ylocs


def apply_gridliner_labels(gl, res):
    """
    Apply NCL-style tickmark resources to Cartopy gridliner.

    Supported resources
    -------------------
    tmXBOn
    tmXTOn
    tmYLOn
    tmYROn

    tmXBLabelFontHeightF
    tmYLLabelFontHeightF
    tmXBLabelFontColor
    tmYLLabelFontColor

    tmXBLabelAngleF
    tmYLLabelAngleF
    """
    if gl is None:
        return None

    gl.bottom_labels = bool_resource(res, "tmXBOn", bool_resource(res, "mpGridBottomLabelsOn", True))
    gl.top_labels = bool_resource(res, "tmXTOn", bool_resource(res, "mpGridTopLabelsOn", False))
    gl.left_labels = bool_resource(res, "tmYLOn", bool_resource(res, "mpGridLeftLabelsOn", True))
    gl.right_labels = bool_resource(res, "tmYROn", bool_resource(res, "mpGridRightLabelsOn", False))

    x_size = res.get("tmXBLabelFontHeightF", res.get("mpGridLabelFontHeightF", None))
    y_size = res.get("tmYLLabelFontHeightF", res.get("mpGridLabelFontHeightF", None))

    x_color = res.get("tmXBLabelFontColor", res.get("mpGridLabelFontColor", None))
    y_color = res.get("tmYLLabelFontColor", res.get("mpGridLabelFontColor", None))

    x_style = {}
    y_style = {}

    if x_size is not None:
        x_style["size"] = float(x_size)

    if y_size is not None:
        y_style["size"] = float(y_size)

    if x_color is not None:
        x_style["color"] = x_color

    if y_color is not None:
        y_style["color"] = y_color

    x_angle = res.get("tmXBLabelAngleF", None)
    y_angle = res.get("tmYLLabelAngleF", None)

    if x_angle is not None:
        x_style["rotation"] = float(x_angle)

    if y_angle is not None:
        y_style["rotation"] = float(y_angle)

    if x_style:
        gl.xlabel_style = x_style

    if y_style:
        gl.ylabel_style = y_style

    return gl


def apply_plain_axis_ticks(ax, res):
    """
    Apply tick controls for plain Matplotlib axes.
    For GeoAxes, most tick labels are handled by gridliner.
    """
    if not bool_resource(res, "tmBorderOn", True):
        for spine in getattr(ax, "spines", {}).values():
            spine.set_visible(False)

    if "tmXBValues" in res:
        ax.set_xticks([float(v) for v in res["tmXBValues"]])

    if "tmYLValues" in res:
        ax.set_yticks([float(v) for v in res["tmYLValues"]])

    if "tmXBLabels" in res:
        ax.set_xticklabels(res["tmXBLabels"])

    if "tmYLLabels" in res:
        ax.set_yticklabels(res["tmYLLabels"])

    ax.tick_params(
        bottom=bool_resource(res, "tmXBOn", True),
        top=bool_resource(res, "tmXTOn", False),
        left=bool_resource(res, "tmYLOn", True),
        right=bool_resource(res, "tmYROn", False),
        labelbottom=bool_resource(res, "tmXBLabelsOn", bool_resource(res, "tmXBOn", True)),
        labeltop=bool_resource(res, "tmXTLabelsOn", bool_resource(res, "tmXTOn", False)),
        labelleft=bool_resource(res, "tmYLLabelsOn", bool_resource(res, "tmYLOn", True)),
        labelright=bool_resource(res, "tmYRLabelsOn", bool_resource(res, "tmYROn", False)),
        direction=res.get("tmTickDirection", "out"),
        length=float(res.get("tmMajorLengthF", 4.0)),
        width=float(res.get("tmMajorThicknessF", 0.8)),
    )

    if "tmXBLabelFontHeightF" in res:
        for label in ax.get_xticklabels():
            label.set_fontsize(float(res["tmXBLabelFontHeightF"]))

    if "tmYLLabelFontHeightF" in res:
        for label in ax.get_yticklabels():
            label.set_fontsize(float(res["tmYLLabelFontHeightF"]))

    if "tmXBLabelFontColor" in res:
        for label in ax.get_xticklabels():
            label.set_color(res["tmXBLabelFontColor"])

    if "tmYLLabelFontColor" in res:
        for label in ax.get_yticklabels():
            label.set_color(res["tmYLLabelFontColor"])

    return ax
