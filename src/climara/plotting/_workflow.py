from __future__ import annotations

from pathlib import Path

from ._resources import bool_resource
from ._workstation import NclWorkstation


def apply_gsn_maximize(fig, ax=None, gsnres=None):
    """Apply a simple NCL-style gsnMaximize layout adjustment."""
    gsnres = dict(gsnres or {})

    if not bool_resource(gsnres, "gsnMaximize", False):
        return fig, ax

    left = float(gsnres.get("gsnMaximizeLeft", 0.06))
    right = float(gsnres.get("gsnMaximizeRight", 0.96))
    bottom = float(gsnres.get("gsnMaximizeBottom", 0.08))
    top = float(gsnres.get("gsnMaximizeTop", 0.92))

    try:
        fig.subplots_adjust(left=left, right=right, bottom=bottom, top=top)
    except Exception:
        pass

    return fig, ax


def apply_gsn_draw(fig, gsnres=None, wks=None):
    """Apply NCL-style gsnDraw behavior."""
    gsnres = dict(gsnres or {})

    if not bool_resource(gsnres, "gsnDraw", True):
        return None

    if isinstance(wks, NclWorkstation):
        return wks.draw(fig)

    try:
        fig.canvas.draw_idle()
    except Exception:
        pass

    return fig


def apply_gsn_frame(fig, gsnres=None, wks=None):
    """Apply NCL-style gsnFrame behavior."""
    gsnres = dict(gsnres or {})

    if not bool_resource(gsnres, "gsnFrame", False):
        return None

    filename = (
        gsnres.get("gsnFrameFileName")
        or gsnres.get("gsnFrameFilename")
        or gsnres.get("gsnFrameFile")
    )

    if isinstance(wks, NclWorkstation):
        return wks.frame(fig=fig, filename=filename)

    if filename is None:
        return None

    path = Path(filename)
    dpi = int(gsnres.get("gsnFrameDpi", 300))
    bbox_inches = gsnres.get("gsnFrameBBoxInches", "tight")

    fig.savefig(path, dpi=dpi, bbox_inches=bbox_inches)

    return path


def apply_gsn_workflow(fig, ax=None, out=None, gsnres=None, wks=None):
    """Apply gsnMaximize, gsnDraw, and gsnFrame in one place."""
    gsnres = dict(gsnres or {})
    out = dict(out or {})

    fig, ax = apply_gsn_maximize(fig, ax=ax, gsnres=gsnres)
    draw_result = apply_gsn_draw(fig, gsnres=gsnres, wks=wks)
    frame_file = apply_gsn_frame(fig, gsnres=gsnres, wks=wks)

    out["frame_file"] = frame_file
    out["gsn_workflow"] = {
        "draw": bool_resource(gsnres, "gsnDraw", True),
        "frame": bool_resource(gsnres, "gsnFrame", False),
        "maximize": bool_resource(gsnres, "gsnMaximize", False),
        "draw_result": draw_result is not None,
    }

    return fig, ax, out
