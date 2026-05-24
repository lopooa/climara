from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import matplotlib.pyplot as plt

from ._strings import draw_text_item_ndc_mpl
from ._polyline import draw_polyline_ndc_mpl
from ._render_mpl import draw_polygon_ndc_mpl
from ._polymarker import draw_marker_ndc_mpl


_SUPPORTED_WKS_TYPES = {
    "png": "png",
    "pdf": "pdf",
    "ps": "ps",
    "eps": "eps",
    "svg": "svg",
    "jpg": "jpg",
    "jpeg": "jpeg",
    "tif": "tif",
    "tiff": "tiff",
}


def _normalize_wks_type(wks_type):
    if wks_type is None:
        return "png"

    key = str(wks_type).strip().lower()

    if key in _SUPPORTED_WKS_TYPES:
        return _SUPPORTED_WKS_TYPES[key]

    raise ValueError(
        f"Unsupported workstation type: {wks_type!r}. "
        f"Supported types are: {sorted(_SUPPORTED_WKS_TYPES)}"
    )


def _normalize_output_path(path, default_suffix):
    path = Path(path)

    if path.suffix == "":
        path = path.with_suffix(f".{default_suffix}")

    return path


@dataclass
class NclWorkstation:
    """Small NCL-like workstation wrapper around matplotlib savefig."""

    wks_type: str = "png"
    name: str = "climara"
    output_dir: str | Path = "."
    dpi: int = 100
    bbox_inches: str | None = None
    transparent: bool = False
    close_on_frame: bool = False
    use_frame_number: bool = False

    # NCL-style workstation/page resources.
    # If not specified, png-like outputs use a 1024 x 1024 page.
    # Vector outputs use a letter portrait page, 8.5 x 11 inch.
    wkWidth: int | None = None
    wkHeight: int | None = None
    wkDpi: int | None = None
    wkPaperWidthF: float | None = None
    wkPaperHeightF: float | None = None
    wkOrientation: str = "portrait"
    savefig_kwargs: dict = field(default_factory=dict)
    page_primitives: list = field(default_factory=list)

    def __post_init__(self):
        self.wks_type = _normalize_wks_type(self.wks_type)
        self.output_dir = Path(self.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        if self.wkDpi is not None:
            self.dpi = int(self.wkDpi)

        self.wkOrientation = str(self.wkOrientation or "portrait").lower()
        self._init_page_resources()

        self.frame_count = 0

    def _init_page_resources(self):
        """Initialize NCL-style workstation page resources.

        This does not create a Matplotlib figure.
        It only defines the workstation/page geometry.
        """
        if self.wks_type in {"png", "jpg", "jpeg", "tif", "tiff"}:
            if self.wkWidth is None:
                self.wkWidth = 1024
            if self.wkHeight is None:
                self.wkHeight = 1024
            return

        if self.wkPaperWidthF is None:
            self.wkPaperWidthF = 8.5

        if self.wkPaperHeightF is None:
            self.wkPaperHeightF = 11.0

        if self.wkOrientation in {"landscape", "horizontal"}:
            if self.wkPaperHeightF > self.wkPaperWidthF:
                self.wkPaperWidthF, self.wkPaperHeightF = (
                    self.wkPaperHeightF,
                    self.wkPaperWidthF,
                )

        if self.wkOrientation in {"portrait", "vertical"}:
            if self.wkPaperWidthF > self.wkPaperHeightF:
                self.wkPaperWidthF, self.wkPaperHeightF = (
                    self.wkPaperHeightF,
                    self.wkPaperWidthF,
                )

    @property
    def suffix(self):
        return self.wks_type

    def page_size_pixels(self):
        """Return the raster workstation page size in pixels when available."""
        if self.wkWidth is None or self.wkHeight is None:
            return None

        return int(self.wkWidth), int(self.wkHeight)

    def page_size_inches(self):
        """Return the NCL-style workstation page size in inches.

        For raster workstations, the inch size is derived from
        wkWidth / wkDpi and wkHeight / wkDpi.

        For vector workstations, the paper resources are used.
        """
        if self.wkWidth is not None and self.wkHeight is not None:
            return (
                float(self.wkWidth) / float(self.dpi),
                float(self.wkHeight) / float(self.dpi),
            )

        width = 8.5 if self.wkPaperWidthF is None else float(self.wkPaperWidthF)
        height = 11.0 if self.wkPaperHeightF is None else float(self.wkPaperHeightF)

        return width, height

    def figure_size_inches(self):
        """Temporary Matplotlib bridge for the current renderer."""
        return self.page_size_inches()

    def ndc_to_page(self, x, y):
        """Convert NDC coordinates to page coordinates.

        This is backend independent. For raster workstations, the page
        coordinates are pixels. For vector workstations, they are inches.
        """
        width, height = self.page_size_pixels() or self.page_size_inches()
        return float(x) * width, float(y) * height

    def page_to_ndc(self, x, y):
        """Convert page coordinates back to NDC."""
        width, height = self.page_size_pixels() or self.page_size_inches()
        return float(x) / width, float(y) / height

    def figure(self):
        """Create a Matplotlib figure from the NCL-style workstation page.

        This is only a temporary renderer bridge. Layout code must not depend
        on Matplotlib figure geometry.
        """
        return plt.figure(
            figsize=self.figure_size_inches(),
            dpi=self.dpi,
        )

    def _default_filename(self):
        base = Path(str(self.name))

        if self.use_frame_number:
            stem = base.stem
            suffix = base.suffix

            if suffix:
                base = Path(f"{stem}_{self.frame_count + 1:03d}{suffix}")
            else:
                base = Path(f"{stem}_{self.frame_count + 1:03d}")

        return _normalize_output_path(base, self.suffix)

    def _resolve_filename(self, filename=None):
        if filename is None:
            path = self._default_filename()
        else:
            path = _normalize_output_path(filename, self.suffix)

        if not path.is_absolute():
            path = self.output_dir / path

        path.parent.mkdir(parents=True, exist_ok=True)

        return path

    def add_primitive(self, primitive):
        """Store a workstation-level primitive.

        This is the NCL-like page primitive store. It does not draw by itself.
        """
        self.page_primitives.append(primitive)
        return primitive

    def draw_ndc_text_item(self, item, fig=None):
        """Temporary Matplotlib bridge for workstation-level NDC text."""
        if fig is None:
            fig = plt.gcf()

        return draw_text_item_ndc_mpl(fig, item)

    def draw_ndc_polyline(self, primitive, fig=None):
        """Temporary Matplotlib bridge for workstation-level NDC polyline."""
        if fig is None:
            fig = plt.gcf()

        return draw_polyline_ndc_mpl(fig, primitive)

    def draw_ndc_marker(self, primitive, fig=None):
        """Temporary Matplotlib bridge for workstation-level NDC marker."""
        if fig is None:
            fig = plt.gcf()

        return draw_marker_ndc_mpl(fig, primitive)

    def draw_ndc_polygon(self, primitive, fig=None):
        """Temporary Matplotlib bridge for workstation-level NDC polygon."""
        if fig is None:
            fig = plt.gcf()

        return draw_polygon_ndc_mpl(fig, primitive)

    def draw(self, fig=None):
        """Draw a figure without saving it."""
        if fig is None:
            fig = plt.gcf()

        try:
            fig.canvas.draw_idle()
        except Exception:
            try:
                fig.canvas.draw()
            except Exception:
                pass

        return fig

    def frame(self, fig=None, filename=None, **kwargs):
        """Save a figure and advance the workstation frame counter."""
        if fig is None:
            fig = plt.gcf()

        path = self._resolve_filename(filename)

        savefig_kwargs = dict(self.savefig_kwargs)
        savefig_kwargs.update(kwargs)

        savefig_kwargs.setdefault("dpi", self.dpi)
        savefig_kwargs.setdefault("bbox_inches", self.bbox_inches)
        savefig_kwargs.setdefault("transparent", self.transparent)

        fig.savefig(path, **savefig_kwargs)

        self.frame_count += 1

        if self.close_on_frame:
            plt.close(fig)

        return path

    def close(self):
        """Close all matplotlib figures."""
        plt.close("all")


def gsn_open_wks(wks_type="png", name="climara", output_dir=".", **kwargs):
    """Create an NCL-style workstation."""
    return NclWorkstation(
        wks_type=wks_type,
        name=name,
        output_dir=output_dir,
        **kwargs,
    )


def ncl_draw(obj=None):
    """NCL-style draw helper."""
    if isinstance(obj, NclWorkstation):
        return obj.draw()

    if obj is None:
        obj = plt.gcf()

    try:
        obj.canvas.draw_idle()
    except Exception:
        try:
            obj.canvas.draw()
        except Exception:
            pass

    return obj


def ncl_frame(wks=None, fig=None, filename=None, **kwargs):
    """NCL-style frame helper."""
    if isinstance(wks, NclWorkstation):
        return wks.frame(fig=fig, filename=filename, **kwargs)

    if fig is None:
        fig = plt.gcf()

    if filename is None:
        filename = "climara.png"

    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)

    fig.savefig(path, **kwargs)

    return path


def ncl_close(wks=None):
    """Close figures associated with a workstation-like workflow."""
    if isinstance(wks, NclWorkstation):
        return wks.close()

    plt.close("all")


draw = ncl_draw
frame = ncl_frame
close = ncl_close


__all__ = [
    "NclWorkstation",
    "gsn_open_wks",
    "ncl_draw",
    "ncl_frame",
    "ncl_close",
    "draw",
    "frame",
    "close",
]
