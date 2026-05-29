from __future__ import annotations

import ctypes
import os

from climara.graphics._ncl_plotchar_ctypes_backend import (
    NclPlotcharCRoutines,
    NclPlotcharCtypesBackend,
    NclPlotcharCtypesBackendError,
)
from climara.graphics._ncl_plotchar_textitem import (
    build_ncl_plotchar_metrics_provider,
    build_ncl_plotchar_textitem_measurement_call,
)
from climara.graphics._plotchar_metrics import has_plotchar_metrics_engine
from climara.graphics._text_bbox import build_text_item_bbox_request
from climara.graphics._text_bbox_plotchar_bridge import (
    build_plotchar_metrics_request_from_text_bbox_request,
)
from climara.graphics._text_semantics import build_text_item_semantics


def almost_equal(value, expected, tol=1e-7):
    assert abs(value - expected) <= tol, (value, expected)


class FakePlotcharCRoutines:
    def __init__(self):
        self.calls = []
        self.metrics = {
            b"DL": 0.011,
            b"DR": 0.033,
            b"DT": 0.027,
            b"DB": 0.006,
        }

    def pcseti(self, name, value):
        self.calls.append(("pcseti", name, int(value)))

    def pcsetr(self, name, value):
        self.calls.append(("pcsetr", name, round(float(value), 12)))

    def pcsetc(self, name, value):
        self.calls.append(("pcsetc", name, value))

    def plchhq(self, xpos, ypos, chrs, size, angd, cntr):
        self.calls.append(
            (
                "plchhq",
                round(float(xpos), 12),
                round(float(ypos), 12),
                chrs,
                round(float(size), 12),
                round(float(angd), 12),
                round(float(cntr), 12),
            )
        )

    def pcgetr(self, name, out):
        self.calls.append(("pcgetr", name))
        out.contents.value = self.metrics[name]


class PointerCompatibleFakePlotcharCRoutines(FakePlotcharCRoutines):
    def pcgetr(self, name, out):
        self.calls.append(("pcgetr", name))
        ctypes.cast(out, ctypes.POINTER(ctypes.c_float)).contents.value = self.metrics[name]


def build_call():
    semantics = build_text_item_semantics(
        "ABC",
        func_code="~",
        font=21,
        font_height=0.04,
        font_aspect=2.0,
        font_quality="High",
        constant_spacing=0.125,
    )
    bbox_request = build_text_item_bbox_request(semantics, x=0.2, y=0.8)
    plotchar_request = build_plotchar_metrics_request_from_text_bbox_request(
        bbox_request
    )
    return plotchar_request, build_ncl_plotchar_textitem_measurement_call(
        plotchar_request
    )


def main():
    plotchar_request, call = build_call()

    fake = PointerCompatibleFakePlotcharCRoutines()
    routines = NclPlotcharCRoutines(
        pcseti=fake.pcseti,
        pcsetr=fake.pcsetr,
        pcsetc=fake.pcsetc,
        plchhq=fake.plchhq,
        pcgetr=fake.pcgetr,
    )
    metrics = routines.metrics_for_call(call)

    expected_prefix = [
        ("pcseti", b"TE", 1),
        ("pcsetr", b"CS", 0.125),
        ("pcsetc", b"FC", b"~"),
        ("pcsetr", b"PH", 21.0),
        ("pcsetr", b"PW", 10.5),
        ("pcseti", b"QU", 0),
        ("pcseti", b"FN", 21),
        ("pcseti", b"QU", 0),
        ("plchhq", 0.5, 0.5, b"~A~ABC", 0.0225, 360.0, -1.0),
        ("pcgetr", b"DL"),
        ("pcgetr", b"DR"),
        ("pcgetr", b"DT"),
        ("pcgetr", b"DB"),
    ]

    assert fake.calls == expected_prefix
    almost_equal(metrics.dl, 0.011)
    almost_equal(metrics.dr, 0.033)
    almost_equal(metrics.dt, 0.027)
    almost_equal(metrics.db, 0.006)

    backend = NclPlotcharCtypesBackend(routines=routines)
    provider = build_ncl_plotchar_metrics_provider(backend=backend)
    provider_metrics = provider.metrics_for_request(plotchar_request)
    almost_equal(provider_metrics.dl, 0.011)
    almost_equal(provider_metrics.dr, 0.033)
    almost_equal(provider_metrics.dt, 0.027)
    almost_equal(provider_metrics.db, 0.006)

    old = os.environ.pop("CLIMARA_NCL_PLOTCHAR_LIB", None)
    try:
        try:
            NclPlotcharCtypesBackend.from_env()
        except NclPlotcharCtypesBackendError as exc:
            assert "will not guess or approximate" in str(exc)
        else:
            raise AssertionError("from_env must stay guarded without explicit library path")
    finally:
        if old is not None:
            os.environ["CLIMARA_NCL_PLOTCHAR_LIB"] = old

    bad_semantics = build_text_item_semantics("汉字", func_code="~")
    bad_bbox_request = build_text_item_bbox_request(bad_semantics, x=0.2, y=0.8)
    bad_plotchar_request = build_plotchar_metrics_request_from_text_bbox_request(
        bad_bbox_request
    )
    bad_call = build_ncl_plotchar_textitem_measurement_call(bad_plotchar_request)
    try:
        routines.metrics_for_call(bad_call)
    except NclPlotcharCtypesBackendError as exc:
        assert "must be ASCII" in str(exc)
    else:
        raise AssertionError("Non-ASCII Plotchar wrapper strings must stay guarded")

    assert isinstance(has_plotchar_metrics_engine(), bool)

    print("✅ NCL Plotchar ctypes backend boundary smoke passed")


if __name__ == "__main__":
    main()
