"""
NCL-style plot strings.

Plot strings are annotation objects attached to a plot. Their coordinates are
defined inside the plot annotation area, not inside the contour/map data area.
"""

from __future__ import annotations

from typing import Any, Mapping

from ._text_item import HluTextItem


def _merge_resources(
    resources: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    out: dict[str, Any] = {}
    if resources:
        out.update(dict(resources))
    out.update(kwargs)
    return out


def _add_child(target: Any, item: Any):
    if hasattr(target, "add_child"):
        target.add_child(item)
    elif hasattr(target, "children"):
        target.children.append(item)
    return item


def create_plot_string(
    text: str,
    x: float,
    y: float,
    resources: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> HluTextItem:
    res = _merge_resources(resources, **kwargs)
    res.setdefault("coordinate_system", "ndc")
    res.setdefault("climaraTextRegion", "annotation")
    return HluTextItem(text=str(text), x=float(x), y=float(y), resources=res)


def gsn_left_string(
    target: Any,
    text: str,
    resources: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> HluTextItem:
    res = _merge_resources(resources, **kwargs)
    res.setdefault("txJust", "CenterLeft")
    res.setdefault("txFontHeightF", 0.016)
    item = create_plot_string(str(text), 0.0, 0.25, res)
    return _add_child(target, item)


def gsn_center_string(
    target: Any,
    text: str,
    resources: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> HluTextItem:
    res = _merge_resources(resources, **kwargs)
    res.setdefault("txJust", "CenterCenter")
    res.setdefault("txFontHeightF", 0.018)
    item = create_plot_string(str(text), 0.5, 0.25, res)
    return _add_child(target, item)


def gsn_right_string(
    target: Any,
    text: str,
    resources: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> HluTextItem:
    res = _merge_resources(resources, **kwargs)
    res.setdefault("txJust", "CenterRight")
    res.setdefault("txFontHeightF", 0.016)
    item = create_plot_string(str(text), 1.0, 0.25, res)
    return _add_child(target, item)


def build_plot_strings(
    target: Any,
    resources: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> list[HluTextItem]:
    res = _merge_resources(resources, **kwargs)
    items: list[HluTextItem] = []

    main_string = res.get("tiMainString")
    if main_string not in (None, ""):
        items.append(
            create_plot_string(
                str(main_string),
                0.5,
                0.72,
                {
                    "txJust": "CenterCenter",
                    "txFontHeightF": float(res.get("tiMainFontHeightF", 0.020)),
                    "txFontColor": res.get("tiMainFontColor", "#111111"),
                },
            )
        )

    left_string = res.get("gsnLeftString")
    if left_string not in (None, ""):
        items.append(
            create_plot_string(
                str(left_string),
                0.0,
                0.25,
                {
                    "txJust": "CenterLeft",
                    "txFontHeightF": float(res.get("gsnLeftStringFontHeightF", 0.016)),
                    "txFontColor": res.get("gsnLeftStringFontColor", "#111111"),
                },
            )
        )

    center_string = res.get("gsnCenterString")
    if center_string not in (None, ""):
        items.append(
            create_plot_string(
                str(center_string),
                0.5,
                0.25,
                {
                    "txJust": "CenterCenter",
                    "txFontHeightF": float(res.get("gsnCenterStringFontHeightF", 0.018)),
                    "txFontColor": res.get("gsnCenterStringFontColor", "#111111"),
                },
            )
        )

    right_string = res.get("gsnRightString")
    if right_string not in (None, ""):
        items.append(
            create_plot_string(
                str(right_string),
                1.0,
                0.25,
                {
                    "txJust": "CenterRight",
                    "txFontHeightF": float(res.get("gsnRightStringFontHeightF", 0.016)),
                    "txFontColor": res.get("gsnRightStringFontColor", "#111111"),
                },
            )
        )

    return items


def add_plot_strings(
    target: Any,
    resources: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> list[HluTextItem]:
    items = build_plot_strings(target, resources, **kwargs)
    for item in items:
        _add_child(target, item)
    return items


__all__ = [
    "add_plot_strings",
    "build_plot_strings",
    "create_plot_string",
    "gsn_center_string",
    "gsn_left_string",
    "gsn_right_string",
]
