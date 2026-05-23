"""
Detrend and trend functions.

NCL reference
-------------
Wrapper source:
- ni/src/lib/nfp/dtrendW.c

Related Fortran routines include:
- dtrend
- dtrend_msg
- dtrend_lsq_msg

Public NCL-style functions:
- dtrend
- dtrend_n
- dtrend_msg
- dtrend_msg_n
- dtrend_quadratic
"""


def dtrend(data, dim="time", return_info=False, **kwargs):
    """Remove a linear trend along a dimension."""
    raise NotImplementedError("dtrend is not implemented yet.")


def dtrend_n(data, dim="time", return_info=False, **kwargs):
    """Remove a linear trend along a selected dimension."""
    return dtrend(data, dim=dim, return_info=return_info, **kwargs)


def dtrend_msg(data, dim="time", return_info=False, **kwargs):
    """Remove a linear trend while handling missing values."""
    raise NotImplementedError("dtrend_msg is not implemented yet.")


def dtrend_msg_n(data, dim="time", return_info=False, **kwargs):
    """Remove a linear trend along a selected dimension while handling missing values."""
    return dtrend_msg(data, dim=dim, return_info=return_info, **kwargs)


def dtrend_quadratic(data, dim="time", return_info=False, **kwargs):
    """Remove a quadratic trend along a dimension."""
    raise NotImplementedError("dtrend_quadratic is not implemented yet.")
