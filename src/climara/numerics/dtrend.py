"""Detrend and trend numerical functions.

NCL reference:
- ni/src/lib/nfp/dtrendW.c
- ni/src/lib/nfpfort/dtrend_dp.f
"""

def dtrend(data, dim="time", return_info=False, **kwargs):
    """Remove a linear trend along a dimension."""
    raise NotImplementedError("dtrend is not implemented yet.")


def lintrend(data, dim="time", **kwargs):
    """Estimate a linear trend along a dimension."""
    raise NotImplementedError("lintrend is not implemented yet.")


def lintrend_total(data, dim="time", **kwargs):
    """Estimate total linear change across the full time span."""
    raise NotImplementedError("lintrend_total is not implemented yet.")
