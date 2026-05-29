from __future__ import annotations

import os
from pathlib import Path

import climara.graphics._render_svg as render_module
from climara.graphics._labelbar_adjust_plotchar_provider import (
    compute_labelbar_adjusted_geometry_from_plotchar_provider_bboxes,
)
from climara.graphics._labelbar_object import HluLabelBar
from climara.graphics._labelbar_svg_adapter import labelbar_to_svg_primitives
from climara.graphics._ncl_plotchar_ctypes_backend import NclPlotcharCtypesBackendError
from climara.graphics._ncl_plotchar_real_library import (
    NCL_PLOTCHAR_LIBRARY_DIRS_ENV,
    NCL_PLOTCHAR_LIBRARY_ENV,
)
from climara.graphics._plotchar_metrics import PlotcharExtentMetrics
from climara.graphics._render_svg import render_svg


def build_labelbar() -> HluLabelBar:
    return HluLabelBar(
        rect=(0.18, 0.20, 0.64, 0.18),
        colors=("#2166ac", "#67a9cf", "#fddbc7", "#b2182b"),
        labels=("Cold", "Cool", "Warm", "Hot", "Very hot"),
        resources={
            "lbTitleString": "Live adjusted LabelBar",
            "lbTitleOn": True,
            "lbTitlePosition": "Top",
            "lbTitleDirection": "Across",
            "lbTitleFuncCode": "~",
            "lbLabelDirection": "Across",
            "lbLabelFuncCode": "~",
            "lbAutoManage": True,
        },
    )


def clear_library_env():
    old_lib = os.environ.pop(NCL_PLOTCHAR_LIBRARY_ENV, None)
    old_dirs = os.environ.pop(NCL_PLOTCHAR_LIBRARY_DIRS_ENV, None)
    return old_lib, old_dirs


def restore_library_env(old_lib, old_dirs):
    if old_lib is None:
        os.environ.pop(NCL_PLOTCHAR_LIBRARY_ENV, None)
    else:
        os.environ[NCL_PLOTCHAR_LIBRARY_ENV] = old_lib

    if old_dirs is None:
        os.environ.pop(NCL_PLOTCHAR_LIBRARY_DIRS_ENV, None)
    else:
        os.environ[NCL_PLOTCHAR_LIBRARY_DIRS_ENV] = old_dirs


def no_library_path_stays_unadjusted():
    old_lib, old_dirs = clear_library_env()
    try:
        svg = render_svg(build_labelbar(), width=900, height=280)
        assert "<svg" in svg
        assert "<polygon" in svg
        assert 'data-climara-labelbar-render-mode="adjusted-live-plotchar"' not in svg
    finally:
        restore_library_env(old_lib, old_dirs)


def invalid_explicit_library_does_not_fall_back():
    old_lib, old_dirs = clear_library_env()
    try:
        os.environ[NCL_PLOTCHAR_LIBRARY_ENV] = str(
            Path("/tmp/climara_missing_real_ncar_plotchar_library_for_renderer.so")
        )
        try:
            render_svg(build_labelbar(), width=900, height=280)
        except NclPlotcharCtypesBackendError as exc:
            message = str(exc)
            assert "shared library" in message or "validation" in message
            assert "c_pcseti" in message
            assert "c_plchhq" in message
        else:
            raise AssertionError(
                "Default renderer must not fall back to unadjusted or heuristic metrics "
                "when a live Plotchar library was explicitly requested but invalid."
            )
    finally:
        restore_library_env(old_lib, old_dirs)


def renderer_consumes_adjusted_primitives_from_live_hook():
    old_hook = render_module._labelbar_live_adjusted_primitives_if_configured

    def fake_live_hook(obj, doc, *, stroke, text_fill):
        requests = render_module._resources(obj)
        title_metrics = PlotcharExtentMetrics(dl=0.20, dr=0.24, db=0.035, dt=0.075)
        label_metrics = PlotcharExtentMetrics(dl=0.035, dr=0.035, db=0.010, dt=0.022)

        def provider(plotchar_request):
            real_string = plotchar_request.semantics.real_string
            if "Live adjusted LabelBar" in real_string:
                return title_metrics
            return label_metrics

        geometry = compute_labelbar_adjusted_geometry_from_plotchar_provider_bboxes(
            obj,
            provider,
        )

        class AdjustedView:
            def __init__(self, source, geometry):
                self._source = source
                self._geometry = geometry

            def compute_geometry(self):
                return self._geometry

            def __getattr__(self, name):
                return getattr(self._source, name)

        return labelbar_to_svg_primitives(
            AdjustedView(obj, geometry),
            doc.width,
            doc.height,
            stroke=stroke,
            text_fill=text_fill,
        )

    try:
        render_module._labelbar_live_adjusted_primitives_if_configured = fake_live_hook
        svg = render_module.render_svg(build_labelbar(), width=900, height=280)
        assert 'data-climara-labelbar-render-mode="adjusted-live-plotchar"' in svg
        assert "Live adjusted LabelBar" in svg
        assert "<polygon" in svg
    finally:
        render_module._labelbar_live_adjusted_primitives_if_configured = old_hook


def main():
    no_library_path_stays_unadjusted()
    invalid_explicit_library_does_not_fall_back()
    renderer_consumes_adjusted_primitives_from_live_hook()
    print("✅ Default renderer LabelBar live-adjust gate smoke passed")


if __name__ == "__main__":
    main()
