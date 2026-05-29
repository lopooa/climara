from __future__ import annotations

import os
from pathlib import Path

from climara.graphics._labelbar_object import HluLabelBar
from climara.graphics._plotchar_python_live_engine import python_plotchar_mainline_status
from climara.graphics._render_svg import render_svg


def build_labelbar(title="Python adjusted LabelBar") -> HluLabelBar:
    return HluLabelBar(
        rect=(0.18, 0.20, 0.64, 0.18),
        colors=("#2166ac", "#67a9cf", "#fddbc7", "#b2182b"),
        labels=("Cold", "Cool", "Warm", "Hot", "Very hot"),
        resources={
            "lbTitleString": title,
            "lbTitleOn": True,
            "lbTitlePosition": "Top",
            "lbTitleDirection": "Across",
            "lbTitleFuncCode": "~",
            "lbLabelDirection": "Across",
            "lbLabelFuncCode": "~",
            "lbAutoManage": True,
        },
    )


def main():
    status = python_plotchar_mainline_status()
    svg = render_svg(build_labelbar(), width=900, height=280)
    assert "<svg" in svg
    assert "<polygon" in svg
    assert "Python adjusted LabelBar" in svg

    if status.available:
        assert 'data-climara-labelbar-render-mode="adjusted-python-plotchar"' in svg
    else:
        assert 'data-climara-labelbar-render-mode="adjusted-python-plotchar"' not in svg
        assert "fixed-width" not in status.report.lower() or "No fixed-width" in status.report

    if status.available:
        bad = build_labelbar(title="A~S~B")
        try:
            render_svg(bad, width=900, height=280)
        except Exception as exc:
            message = str(exc)
            assert (
                "function" in message.lower()
                or "Plotchar" in message
                or "unsupported" in message.lower()
            ), message
        else:
            raise AssertionError(
                "Renderer must not silently fall back when Python Plotchar mainline sees "
                "unsupported inline function-code text."
            )

    print("✅ Python mainline renderer LabelBar AdjustGeometry smoke passed")


if __name__ == "__main__":
    main()
