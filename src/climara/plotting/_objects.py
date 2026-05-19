from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

import matplotlib.pyplot as plt

from ._contour import ncl_contour_map
from ._gsn import gsn_panel
from ._overlay import (
    overlay_contour,
    overlay_filled_contour,
    overlay_pcolormesh,
    overlay_vectors,
    overlay_markers,
    overlay_text,
    overlay_polyline,
    overlay_polygon,
    overlay_rectangle,
)
from ._hatching import add_hatching, add_stipple
from ._resources import NclResources


@dataclass
class ScalarField:
    """
    NCL-style scalar field object.

    This is similar in spirit to NCL's scalarFieldClass, but Pythonic.
    """
    data: Any
    lon: Any | None = None
    lat: Any | None = None
    name: str | None = None
    attrs: dict = field(default_factory=dict)

    @classmethod
    def from_xarray(cls, da, name: str | None = None):
        lon = None
        lat = None

        for key in ["lon", "longitude", "x"]:
            if key in da.coords:
                lon = da[key].values
                break

        for key in ["lat", "latitude", "y"]:
            if key in da.coords:
                lat = da[key].values
                break

        return cls(
            data=da,
            lon=lon,
            lat=lat,
            name=name or getattr(da, "name", None),
            attrs=dict(getattr(da, "attrs", {})),
        )

    def with_attrs(self, **attrs):
        new_attrs = dict(self.attrs)
        new_attrs.update(attrs)

        return ScalarField(
            data=self.data,
            lon=self.lon,
            lat=self.lat,
            name=self.name,
            attrs=new_attrs,
        )


@dataclass
class OverlayLayer:
    """
    A deferred overlay layer.

    layer_type examples:
        contour
        filled_contour
        pcolormesh
        vectors
        markers
        text
        polyline
        polygon
        rectangle
        hatching
        stipple
        custom
    """
    layer_type: str
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    res: dict = field(default_factory=dict)
    func: Callable | None = None

    def draw(self, ax):
        layer_type = self.layer_type

        if layer_type == "contour":
            return overlay_contour(ax, *self.args, res=self.res, **self.kwargs)

        if layer_type == "filled_contour":
            return overlay_filled_contour(ax, *self.args, res=self.res, **self.kwargs)

        if layer_type == "pcolormesh":
            return overlay_pcolormesh(ax, *self.args, res=self.res, **self.kwargs)

        if layer_type == "vectors":
            return overlay_vectors(ax, *self.args, res=self.res, **self.kwargs)

        if layer_type == "markers":
            return overlay_markers(ax, *self.args, res=self.res, **self.kwargs)

        if layer_type == "text":
            return overlay_text(ax, *self.args, res=self.res, **self.kwargs)

        if layer_type == "polyline":
            return overlay_polyline(ax, *self.args, res=self.res, **self.kwargs)

        if layer_type == "polygon":
            return overlay_polygon(ax, *self.args, res=self.res, **self.kwargs)

        if layer_type == "rectangle":
            return overlay_rectangle(ax, *self.args, res=self.res, **self.kwargs)

        if layer_type == "hatching":
            return add_hatching(ax, *self.args, res=self.res, **self.kwargs)

        if layer_type == "stipple":
            return add_stipple(ax, *self.args, res=self.res, **self.kwargs)

        if layer_type == "custom":
            if self.func is None:
                raise ValueError("custom OverlayLayer requires func")

            return self.func(ax, *self.args, res=self.res, **self.kwargs)

        raise ValueError(f"Unsupported overlay layer type: {layer_type}")


@dataclass
class MapPlot:
    """
    Map-only object.

    Useful when you want to create a map first, then overlay layers.
    """
    res: dict = field(default_factory=dict)
    overlays: list[OverlayLayer] = field(default_factory=list)

    def add_overlay(self, layer: OverlayLayer):
        self.overlays.append(layer)
        return self

    def draw(self, fig=None, ax=None):
        import numpy as np

        dummy = np.zeros((2, 2))
        lon = [0, 1]
        lat = [0, 1]

        draw_res = dict(self.res)
        draw_res.setdefault("cnFillOn", False)
        draw_res.setdefault("cnLinesOn", False)
        draw_res.setdefault("lbLabelBarOn", False)

        fig, ax, out = ncl_contour_map(
            dummy,
            lon=lon,
            lat=lat,
            res=draw_res,
            fig=fig,
            ax=ax,
        )

        overlay_results = []

        for layer in self.overlays:
            overlay_results.append(layer.draw(ax))

        out["overlay_results"] = overlay_results

        return fig, ax, out


@dataclass
class ContourMapPlot:
    """
    NCL-style contour map plot object.
    """
    field: ScalarField
    res: dict = field(default_factory=dict)
    overlays: list[OverlayLayer] = field(default_factory=list)

    def add_overlay(self, layer: OverlayLayer):
        self.overlays.append(layer)
        return self

    def add_contour(self, data=None, lon=None, lat=None, res=None):
        if data is None:
            data = self.field.data
            lon = self.field.lon if lon is None else lon
            lat = self.field.lat if lat is None else lat

        return self.add_overlay(
            OverlayLayer(
                "contour",
                args=(data,),
                kwargs={"lon": lon, "lat": lat},
                res=res or {},
            )
        )

    def add_hatching(self, mask, lon=None, lat=None, res=None):
        if lon is None:
            lon = self.field.lon

        if lat is None:
            lat = self.field.lat

        return self.add_overlay(
            OverlayLayer(
                "hatching",
                args=(mask,),
                kwargs={"lon": lon, "lat": lat},
                res=res or {},
            )
        )

    def add_stipple(self, mask, lon=None, lat=None, res=None):
        if lon is None:
            lon = self.field.lon

        if lat is None:
            lat = self.field.lat

        return self.add_overlay(
            OverlayLayer(
                "stipple",
                args=(mask,),
                kwargs={"lon": lon, "lat": lat},
                res=res or {},
            )
        )

    def add_markers(self, x, y, res=None, values=None):
        return self.add_overlay(
            OverlayLayer(
                "markers",
                args=(x, y),
                kwargs={"values": values},
                res=res or {},
            )
        )

    def add_text(self, x, y, text, res=None):
        return self.add_overlay(
            OverlayLayer(
                "text",
                args=(x, y, text),
                res=res or {},
            )
        )

    def add_polyline(self, x, y, res=None):
        return self.add_overlay(
            OverlayLayer(
                "polyline",
                args=(x, y),
                res=res or {},
            )
        )

    def add_polygon(self, xy, res=None):
        return self.add_overlay(
            OverlayLayer(
                "polygon",
                args=(xy,),
                res=res or {},
            )
        )

    def add_rectangle(self, x0, y0, x1, y1, res=None):
        return self.add_overlay(
            OverlayLayer(
                "rectangle",
                args=(x0, y0, x1, y1),
                res=res or {},
            )
        )

    def add_vectors(self, u, v, lon=None, lat=None, res=None):
        if lon is None:
            lon = self.field.lon

        if lat is None:
            lat = self.field.lat

        return self.add_overlay(
            OverlayLayer(
                "vectors",
                args=(u, v),
                kwargs={"lon": lon, "lat": lat},
                res=res or {},
            )
        )

    def draw(self, fig=None, ax=None):
        fig, ax, out = ncl_contour_map(
            self.field.data,
            lon=self.field.lon,
            lat=self.field.lat,
            res=self.res,
            fig=fig,
            ax=ax,
        )

        overlay_results = []

        for layer in self.overlays:
            overlay_results.append(layer.draw(ax))

        out["overlay_results"] = overlay_results

        return fig, ax, out

    def save(self, filename, dpi=300, bbox_inches="tight"):
        fig, ax, out = self.draw()
        fig.savefig(filename, dpi=dpi, bbox_inches=bbox_inches)
        plt.close(fig)

        return filename


@dataclass
class PanelMapPlot:
    """
    NCL-style panel map plot object.
    """
    fields: list[ScalarField]
    res: dict = field(default_factory=dict)
    titles: list[str] | None = None
    ncol: int = 2
    common_labelbar: bool = True
    row_titles: list[str] | None = None
    col_titles: list[str] | None = None

    def draw(self, figsize=None):
        data_list = [field.data for field in self.fields]

        lon = self.fields[0].lon if self.fields else None
        lat = self.fields[0].lat if self.fields else None

        res = NclResources(self.res).merged({})

        if self.row_titles is not None:
            res["gsnPanelRowTitles"] = self.row_titles

        if self.col_titles is not None:
            res["gsnPanelColTitles"] = self.col_titles

        return gsn_panel(
            data_list,
            lon=lon,
            lat=lat,
            res=res,
            titles=self.titles,
            ncol=self.ncol,
            figsize=figsize,
            common_labelbar=self.common_labelbar,
        )

    def save(self, filename, dpi=300, bbox_inches="tight", figsize=None):
        fig, axes, out = self.draw(figsize=figsize)
        fig.savefig(filename, dpi=dpi, bbox_inches=bbox_inches)
        plt.close(fig)

        return filename
