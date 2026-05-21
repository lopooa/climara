from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import matplotlib.pyplot as plt


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
    dpi: int = 300
    bbox_inches: str | None = "tight"
    transparent: bool = False
    close_on_frame: bool = False
    use_frame_number: bool = False
    savefig_kwargs: dict = field(default_factory=dict)

    def __post_init__(self):
        self.wks_type = _normalize_wks_type(self.wks_type)
        self.output_dir = Path(self.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.frame_count = 0

    @property
    def suffix(self):
        return self.wks_type

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
