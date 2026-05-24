from __future__ import annotations

from ._text_item import HluTextItem


def _get_font_height(res, default=0.012):
    value = res.get("txFontHeightF", res.get("gsnTextFontHeightF", default))
    return float(value)


def gsn_create_text_ndc(wks, text, x, y, res=None):
    """Create an NCL-style TextItem in workstation NDC coordinates."""

    res = dict(res or {})

    item = HluTextItem(
        txString=str(text),
        txPosXF=float(x),
        txPosYF=float(y),
        txJust=res.get("txJust", res.get("gsnTextJust", "center_center")),
        txFontHeightF=_get_font_height(res),
        txFontColor=res.get("txFontColor", res.get("gsnTextFontColor", "black")),
        txAngleF=float(res.get("txAngleF", res.get("gsnTextAngleF", 0.0))),
        coord_system="ndc",
        name=res.get("txName", "text_ndc"),
        resources=res,
    )

    if hasattr(wks, "add_primitive"):
        wks.add_primitive(item)

    return item


def gsn_text_ndc(wks, text, x, y, res=None):
    """NCL-style gsn_text_ndc.

    For now this creates an HluTextItem and stores it on the workstation.
    Rendering will be handled later by the backend.
    """

    item = gsn_create_text_ndc(wks, text, x, y, res=res)

    if hasattr(wks, "draw_ndc_text_item"):
        return wks.draw_ndc_text_item(item)

    return item
