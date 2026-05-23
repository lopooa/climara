from __future__ import annotations

import numpy as np


_PREFIX_GROUPS = {
    "cn": "contour",
    "mp": "map",
    "lb": "labelbar",
    "pm": "plotmanager",
    "ti": "title",
    "tm": "tickmark",
    "vp": "viewport",
    "gsn": "gsn",
    "tx": "text",
    "gs": "graphicstyle",
    "vc": "vector",
    "sf": "scalarfield",
    "tr": "transform",
}


def split_resources(res: dict | None = None) -> dict:
    groups = {
        "contour": {},
        "map": {},
        "labelbar": {},
        "plotmanager": {},
        "title": {},
        "tickmark": {},
        "viewport": {},
        "gsn": {},
        "text": {},
        "graphicstyle": {},
        "vector": {},
        "scalarfield": {},
        "transform": {},
        "other": {},
    }

    if res is None:
        return groups

    for key, value in res.items():
        matched = False

        for prefix, group_name in _PREFIX_GROUPS.items():
            if key.startswith(prefix):
                groups[group_name][key] = value
                matched = True
                break

        if not matched:
            groups["other"][key] = value

    return groups


def resolve_contour_levels(cnres: dict | None = None):
    if cnres is None:
        return None

    mode = cnres.get("cnLevelSelectionMode", None)

    if mode == "ExplicitLevels":
        levels = cnres.get("cnLevels", None)

        if levels is None:
            return None

        return np.asarray(levels, dtype=float)

    if mode == "ManualLevels":
        vmin = cnres.get("cnMinLevelValF", None)
        vmax = cnres.get("cnMaxLevelValF", None)
        step = cnres.get("cnLevelSpacingF", None)

        if vmin is None or vmax is None or step is None:
            return None

        return np.arange(
            float(vmin),
            float(vmax) + float(step) * 0.5,
            float(step),
            dtype=float,
        )

    if mode == "EqualSpacedLevels":
        vmin = cnres.get("cnMinLevelValF", None)
        vmax = cnres.get("cnMaxLevelValF", None)
        count = cnres.get("cnMaxLevelCount", None)

        if vmin is None or vmax is None or count is None:
            return None

        return np.linspace(float(vmin), float(vmax), int(count))

    if "cnLevels" in cnres:
        return np.asarray(cnres["cnLevels"], dtype=float)

    return None


def bool_resource(res: dict, key: str, default: bool = False) -> bool:
    value = res.get(key, default)

    if isinstance(value, str):
        return value.lower() in ["true", "yes", "on", "1"]

    return bool(value)


def merge_resources(*items: dict | None) -> dict:
    out = {}

    for item in items:
        if item:
            out.update(item)

    return out


class NclResources(dict):
    """
    Small convenience wrapper around an NCL-style resource dictionary.
    """

    def split(self):
        return split_resources(self)

    def merged(self, *others):
        return NclResources(merge_resources(self, *others))

    def get_group(self, group_name: str):
        return self.split().get(group_name, {})
