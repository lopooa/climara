from __future__ import annotations

import math
import matplotlib.pyplot as plt

from ._contour import ncl_contour_map
from ._labelbar import add_labelbar
from ._maps import create_projection
from ._resources import split_resources


def _copy_res_without_labelbar(res):
    new_res = dict(res or {})
    new_res["lbLabelBarOn"] = False
    return new_res


def _layout_rects(n, ncols, panel_res):
    nrows = math.ceil(n / ncols)

    left = float(panel_res.get("gsnPanelLeft", 0.06))
    right = float(panel_res.get("gsnPanelRight", 0.96))
    bottom = float(panel_res.get("gsnPanelBottom", 0.14))
    top = float(panel_res.get("gsnPanelTop", 0.92))

    xgap = float(panel_res.get("gsnPanelXGap", 0.035))
    ygap = float(panel_res.get("gsnPanelYGap", 0.055))

    if "gsnPanelXWhiteSpacePercent" in panel_res:
        xgap = (right - left) * float(panel_res["gsnPanelXWhiteSpacePercent"]) / 100.0

    if "gsnPanelYWhiteSpacePercent" in panel_res:
        ygap = (top - bottom) * float(panel_res["gsnPanelYWhiteSpacePercent"]) / 100.0

    width = (right - left - xgap * (ncols - 1)) / ncols
    height = (top - bottom - ygap * (nrows - 1)) / nrows

    rects = []

    for i in range(n):
        row = i // ncols
        col = i % ncols

        x0 = left + col * (width + xgap)
        y0 = top - (row + 1) * height - row * ygap

        rects.append([x0, y0, width, height])

    return rects


def _add_panel_figure_strings(fig, axes, panel_res):
    strings = panel_res.get("gsnPanelFigureStrings", None)

    if strings is None:
        return []

    artists = []
    size = float(panel_res.get("gsnPanelFigureStringsFontHeightF", 11))
    color = panel_res.get("gsnPanelFigureStringsFontColor", "black")
    just = str(panel_res.get("gsnPanelFigureStringsJust", "top_left")).lower()
    xoff = float(panel_res.get("gsnPanelFigureStringsXOffset", 0.01))
    yoff = float(panel_res.get("gsnPanelFigureStringsYOffset", 0.01))

    for ax, text in zip(axes, strings):
        pos = ax.get_position()

        if just in ["top_left", "topleft", "left"]:
            x = pos.x0 + xoff
            y = pos.y1 - yoff
            ha = "left"
            va = "top"
        elif just in ["top_right", "topright", "right"]:
            x = pos.x1 - xoff
            y = pos.y1 - yoff
            ha = "right"
            va = "top"
        else:
            x = pos.x0 + xoff
            y = pos.y1 - yoff
            ha = "left"
            va = "top"

        artist = fig.text(
            x,
            y,
            str(text),
            ha=ha,
            va=va,
            fontsize=size,
            color=color,
            fontweight=panel_res.get("gsnPanelFigureStringsFontWeight", "normal"),
        )
        artists.append(artist)

    return artists


def _add_panel_row_col_titles(fig, axes, ncols, panel_res):
    artists = []

    row_titles = panel_res.get("gsnPanelRowTitles", None)
    col_titles = panel_res.get("gsnPanelColTitles", None)

    if col_titles is not None:
        size = float(panel_res.get("gsnPanelColTitleFontHeightF", 12))

        for col, title in enumerate(col_titles):
            if col >= ncols or col >= len(axes):
                continue

            pos = axes[col].get_position()

            artist = fig.text(
                pos.x0 + pos.width / 2,
                pos.y1 + float(panel_res.get("gsnPanelColTitleOffsetF", 0.035)),
                str(title),
                ha="center",
                va="bottom",
                fontsize=size,
                color=panel_res.get("gsnPanelColTitleFontColor", "black"),
            )
            artists.append(artist)

    if row_titles is not None:
        size = float(panel_res.get("gsnPanelRowTitleFontHeightF", 12))
        nrows = math.ceil(len(axes) / ncols)

        for row, title in enumerate(row_titles):
            if row >= nrows:
                continue

            idx = row * ncols

            if idx >= len(axes):
                continue

            pos = axes[idx].get_position()

            artist = fig.text(
                pos.x0 - float(panel_res.get("gsnPanelRowTitleOffsetF", 0.035)),
                pos.y0 + pos.height / 2,
                str(title),
                ha="right",
                va="center",
                rotation=90,
                fontsize=size,
                color=panel_res.get("gsnPanelRowTitleFontColor", "black"),
            )
            artists.append(artist)

    return artists


def ncl_panel_maps(
    data_list,
    lon=None,
    lat=None,
    res=None,
    titles=None,
    ncols=2,
    figsize=None,
    common_labelbar=True,
):
    groups = split_resources(res)
    panel_res = groups["gsn"]
    mpres = groups["map"]
    tmres = groups["tickmark"]
    lbres = groups["labelbar"]
    pmres = groups["plotmanager"]

    mpres = {**mpres, **tmres}

    n = len(data_list)
    nrows = math.ceil(n / ncols)

    if figsize is None:
        figsize = (4.2 * ncols, 3.6 * nrows)

    fig = plt.figure(figsize=figsize)

    rects = _layout_rects(n, ncols, panel_res)
    axes = []
    results = []

    plot_res = _copy_res_without_labelbar(res)

    for i, data in enumerate(data_list):
        projection = create_projection(mpres)
        ax = fig.add_axes(rects[i], projection=projection)

        this_res = dict(plot_res)

        if titles is not None:
            this_res["tiMainString"] = titles[i]

        fig, ax, result = ncl_contour_map(
            data,
            lon=lon,
            lat=lat,
            res=this_res,
            fig=fig,
            ax=ax,
        )

        axes.append(ax)
        results.append(result)

    cbar = None

    if common_labelbar and bool(panel_res.get("gsnPanelLabelBar", True)):
        first_mappable = None

        for result in results:
            if result["mappable"] is not None:
                first_mappable = result["mappable"]
                break

        if first_mappable is not None:
            cax = fig.add_axes(
                [
                    float(panel_res.get("gsnPanelLabelBarLeft", 0.22)),
                    float(panel_res.get("gsnPanelLabelBarBottom", 0.06)),
                    float(panel_res.get("gsnPanelLabelBarWidth", 0.56)),
                    float(panel_res.get("gsnPanelLabelBarHeight", 0.025)),
                ]
            )

            panel_lbres = dict(lbres)
            panel_lbres.setdefault("lbOrientation", "horizontal")

            if "gsnPanelLabelBarLabelFontHeightF" in panel_res:
                panel_lbres["lbLabelFontHeightF"] = panel_res["gsnPanelLabelBarLabelFontHeightF"]

            cbar = add_labelbar(fig, axes[-1], first_mappable, panel_lbres, cax=cax, pmres=pmres)

    figure_string_artists = _add_panel_figure_strings(fig, axes, panel_res)
    title_artists = _add_panel_row_col_titles(fig, axes, ncols, panel_res)

    if "gsnPanelMainString" in panel_res:
        fig.suptitle(
            panel_res["gsnPanelMainString"],
            fontsize=float(panel_res.get("gsnPanelMainFontHeightF", 13)),
            y=float(panel_res.get("gsnPanelMainYF", 0.98)),
        )

    if bool(panel_res.get("gsnFrame", False)):
        filename = panel_res.get("gsnFrameFileName", None)

        if filename is not None:
            fig.savefig(
                filename,
                dpi=int(panel_res.get("gsnFrameDpi", 300)),
                bbox_inches=panel_res.get("gsnFrameBBoxInches", "tight"),
            )

    return fig, axes, {
        "panel_results": results,
        "colorbar": cbar,
        "figure_string_artists": figure_string_artists,
        "title_artists": title_artists,
        "groups": groups,
    }
