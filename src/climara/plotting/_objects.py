from __future__ import annotations

import inspect
from dataclasses import dataclass, field as dataclass_field
from pathlib import Path

import numpy as np

from ._gsn import gsn_csm_contour_map, gsn_panel
from ._overlay import (
    add_box,
    add_markers,
    add_polyline,
    add_rectangle,
    add_stipple,
    add_text,
    add_vectors,
)
from ._workstation import NclWorkstation, gsn_open_wks


def _get_coord(data, names):
    if not hasattr(data, "coords"):
        return None

    for name in names:
        if name in data.coords:
            return np.asarray(data.coords[name])

    return None


def _copy_res(res):
    if res is None:
        return {}

    return dict(res)


@dataclass
class ScalarField:
    """Lightweight scalar field container."""

    data: object
    lon: object | None = None
    lat: object | None = None
    name: str | None = None
    units: str | None = None
    attrs: dict = dataclass_field(default_factory=dict)

    def __post_init__(self):
        if self.lon is None:
            self.lon = _get_coord(self.data, ["lon", "longitude", "x"])

        if self.lat is None:
            self.lat = _get_coord(self.data, ["lat", "latitude", "y"])

        if self.name is None:
            self.name = getattr(self.data, "name", None)

        if self.units is None:
            self.units = getattr(self.data, "attrs", {}).get("units", None)

        if not self.attrs:
            self.attrs = dict(getattr(self.data, "attrs", {}) or {})

    @property
    def values(self):
        return getattr(self.data, "values", self.data)

    @property
    def shape(self):
        return np.asarray(self.values).shape

    def to_numpy(self):
        return np.asarray(self.values)

    def copy(self, **kwargs):
        params = {
            "data": self.data,
            "lon": self.lon,
            "lat": self.lat,
            "name": self.name,
            "units": self.units,
            "attrs": dict(self.attrs),
        }
        params.update(kwargs)

        return ScalarField(**params)

    @classmethod
    def from_dataarray(cls, da):
        return cls(
            data=da,
            lon=_get_coord(da, ["lon", "longitude", "x"]),
            lat=_get_coord(da, ["lat", "latitude", "y"]),
            name=getattr(da, "name", None),
            units=getattr(da, "attrs", {}).get("units", None),
            attrs=dict(getattr(da, "attrs", {}) or {}),
        )


@dataclass
class OverlayLayer:
    """Small container for overlay instructions."""

    kind: str
    args: tuple = dataclass_field(default_factory=tuple)
    kwargs: dict = dataclass_field(default_factory=dict)

    def draw(self, ax):
        kind = self.kind.lower()

        if kind in ["stipple", "stippled", "stippling"]:
            return add_stipple(ax, *self.args, **self.kwargs)

        if kind in ["marker", "markers"]:
            return add_markers(ax, *self.args, **self.kwargs)

        if kind in ["text", "label"]:
            return add_text(ax, *self.args, **self.kwargs)

        if kind in ["polyline", "line"]:
            return add_polyline(ax, *self.args, **self.kwargs)

        if kind in ["rectangle", "rect"]:
            return add_rectangle(ax, *self.args, **self.kwargs)

        if kind in ["box", "region_box", "region"]:
            return add_box(ax, *self.args, **self.kwargs)

        if kind in ["vector", "vectors", "quiver"]:
            return add_vectors(ax, *self.args, **self.kwargs)

        raise ValueError(f"Unknown overlay layer kind: {self.kind}")


@dataclass
class MapPlot:
    """Minimal base map plot object."""

    res: dict | None = None
    fig: object | None = None
    ax: object | None = None
    wks: NclWorkstation | None = None

    def save(self, filename, dpi=300, bbox_inches="tight", **kwargs):
        if self.fig is None:
            raise RuntimeError("Nothing has been drawn yet.")

        path = Path(filename)
        path.parent.mkdir(parents=True, exist_ok=True)

        self.fig.savefig(path, dpi=dpi, bbox_inches=bbox_inches, **kwargs)

        return path

    def frame(self, filename=None):
        if self.fig is None:
            raise RuntimeError("Nothing has been drawn yet.")

        if self.wks is not None:
            return self.wks.frame(self.fig, filename=filename)

        if filename is None:
            return None

        return self.save(filename)


@dataclass(init=False)
class ContourMapPlot(MapPlot):
    def __init__(
        self,
        field: ScalarField | object | None = None,
        res: dict | None = None,
        fig: object | None = None,
        ax: object | None = None,
        wks: NclWorkstation | None = None,
        overlays: list | None = None,
    ):
        self.res = _copy_res(res)
        self.fig = fig
        self.ax = ax
        self.wks = wks
        self.field = self._normalize_field(field)
        self.out = None
        self.overlays = list(overlays or [])

    @staticmethod
    def _normalize_field(field):
        if field is None:
            return None

        if isinstance(field, ScalarField):
            return field

        return ScalarField(field)

    @staticmethod
    def _looks_like_resource_dict(value):
        if not isinstance(value, dict):
            return False

        prefixes = (
            "cn",
            "mp",
            "lb",
            "pm",
            "ti",
            "tm",
            "vp",
            "gsn",
            "tx",
            "gs",
            "vc",
            "sf",
            "tr",
        )

        return any(str(key).startswith(prefixes) for key in value)

    def set_field(self, field):
        self.field = self._normalize_field(field)

        return self

    def draw(self, field=None, res=None, fig=None, ax=None, wks=None):
        if field is not None:
            if self._looks_like_resource_dict(field) and res is None and self.field is not None:
                res = field
            else:
                self.field = self._normalize_field(field)

        if self.field is None:
            raise ValueError(
                "No field/data was provided. Use ContourMapPlot(field, ...), "
                "ContourMapPlot(field=field, ...), or plot.draw(field)."
            )

        final_res = _copy_res(self.res)
        final_res.update(_copy_res(res))

        fig = self.fig if fig is None else fig
        ax = self.ax if ax is None else ax
        wks = self.wks if wks is None else wks

        self.fig, self.ax, self.out = gsn_csm_contour_map(
            self.field.data,
            lon=self.field.lon,
            lat=self.field.lat,
            res=final_res,
            fig=fig,
            ax=ax,
            wks=wks,
        )

        self.res = final_res
        self.wks = wks

        for layer in self.overlays:
            layer.draw(self.ax)

        return self.fig, self.ax, self.out

    __call__ = draw

    def ensure_drawn(self):
        if self.fig is None or self.ax is None or self.out is None:
            return self.draw()

        return self.fig, self.ax, self.out

    def add_overlay(self, layer: OverlayLayer):
        self.overlays.append(layer)

        if self.ax is not None:
            return layer.draw(self.ax)

        return layer

    def add_stipple(self, mask, lon=None, lat=None, res=None):
        self.ensure_drawn()

        return add_stipple(
            self.ax,
            mask,
            lon=self.field.lon if lon is None else lon,
            lat=self.field.lat if lat is None else lat,
            res=res,
        )

    def add_markers(self, x, y, res=None, values=None, mask=None):
        self.ensure_drawn()

        return add_markers(
            self.ax,
            x,
            y,
            res=res,
            values=values,
            mask=mask,
        )

    def add_text(self, x, y, text, res=None):
        self.ensure_drawn()

        return add_text(self.ax, x, y, text, res=res)

    def add_polyline(self, x, y, res=None):
        self.ensure_drawn()

        return add_polyline(self.ax, x, y, res=res)

    def add_rectangle(self, x0, y0, x1, y1, res=None):
        self.ensure_drawn()

        return add_rectangle(self.ax, x0, y0, x1, y1, res=res)

    def add_box(self, lon_min, lon_max, lat_min, lat_max, res=None):
        self.ensure_drawn()

        return add_box(self.ax, lon_min, lon_max, lat_min, lat_max, res=res)

    def add_vectors(self, u, v, lon=None, lat=None, res=None):
        self.ensure_drawn()

        return add_vectors(
            self.ax,
            u,
            v,
            lon=self.field.lon if lon is None else lon,
            lat=self.field.lat if lat is None else lat,
            res=res,
        )

@dataclass
class PanelMapPlot:
    """Object-oriented wrapper around gsn_panel."""

    fields: list
    res: dict | None = None
    titles: list[str] | None = None
    ncols: int = 2
    figsize: tuple | None = None
    common_labelbar: bool = True
    wks: NclWorkstation | None = None

    def __post_init__(self):
        self.fields = [
            field if isinstance(field, ScalarField) else ScalarField(field)
            for field in self.fields
        ]
        self.res = _copy_res(self.res)
        self.fig = None
        self.axes = None
        self.out = None

    def draw(
        self,
        res=None,
        titles=None,
        ncols=None,
        figsize=None,
        common_labelbar=None,
        wks=None,
    ):
        final_res = _copy_res(self.res)
        final_res.update(_copy_res(res))

        titles = self.titles if titles is None else titles
        ncols = self.ncols if ncols is None else ncols
        figsize = self.figsize if figsize is None else figsize
        wks = self.wks if wks is None else wks

        if common_labelbar is None:
            common_labelbar = self.common_labelbar

        data_list = [field.data for field in self.fields]
        lon = self.fields[0].lon
        lat = self.fields[0].lat

        sig = inspect.signature(gsn_panel)
        kwargs = {}

        if "lon" in sig.parameters:
            kwargs["lon"] = lon

        if "lat" in sig.parameters:
            kwargs["lat"] = lat

        if "res" in sig.parameters:
            kwargs["res"] = final_res

        if "titles" in sig.parameters:
            kwargs["titles"] = titles

        if "ncols" in sig.parameters:
            kwargs["ncols"] = ncols
        elif "ncol" in sig.parameters:
            kwargs["ncol"] = ncols

        if "figsize" in sig.parameters:
            kwargs["figsize"] = figsize

        if "common_labelbar" in sig.parameters:
            kwargs["common_labelbar"] = common_labelbar

        if "wks" in sig.parameters:
            kwargs["wks"] = wks

        self.fig, self.axes, self.out = gsn_panel(
            data_list,
            **kwargs,
        )

        self.res = final_res
        self.titles = titles
        self.ncols = ncols
        self.figsize = figsize
        self.common_labelbar = common_labelbar
        self.wks = wks

        return self.fig, self.axes, self.out

    __call__ = draw

    def ensure_drawn(self):
        if self.fig is None or self.axes is None or self.out is None:
            return self.draw()

        return self.fig, self.axes, self.out

    def save(self, filename, dpi=300, bbox_inches="tight", **kwargs):
        self.ensure_drawn()

        path = Path(filename)
        path.parent.mkdir(parents=True, exist_ok=True)

        self.fig.savefig(path, dpi=dpi, bbox_inches=bbox_inches, **kwargs)

        return path

    def frame(self, filename=None):
        self.ensure_drawn()

        if self.wks is not None:
            return self.wks.frame(self.fig, filename=filename)

        if filename is None:
            return None

        return self.save(filename)


def contour_map(field, res=None, wks=None, **kwargs):
    """Convenience function returning a drawn ContourMapPlot."""
    plot = ContourMapPlot(field=field, res=res, wks=wks)
    plot.draw(**kwargs)

    return plot


def panel_map(
    fields,
    res=None,
    titles=None,
    ncols=2,
    figsize=None,
    common_labelbar=True,
    wks=None,
):
    """Convenience function returning a drawn PanelMapPlot."""
    plot = PanelMapPlot(
        fields=fields,
        res=res,
        titles=titles,
        ncols=ncols,
        figsize=figsize,
        common_labelbar=common_labelbar,
        wks=wks,
    )
    plot.draw()

    return plot


def open_workstation(wks_type="png", name="climara", output_dir="."):
    """Object-layer alias for gsn_open_wks."""
    return gsn_open_wks(wks_type, name, output_dir=output_dir)


__all__ = [
    "ScalarField",
    "OverlayLayer",
    "MapPlot",
    "ContourMapPlot",
    "PanelMapPlot",
    "contour_map",
    "panel_map",
    "open_workstation",
]
