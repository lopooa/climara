"""
Regression functions.

NCL reference
-------------
Wrapper source:
- ni/src/lib/nfp/regcoefW.c

Related Fortran routines include:
- dregcoef
- dregcoef_msg

Public NCL-style functions:
- regcoef
- regcoef_n
- regline
- reg_multlin
"""


def regcoef(x, y, dim="time", **kwargs):
    """Compute regression coefficient of y onto x."""
    raise NotImplementedError("regcoef is not implemented yet.")


def regcoef_n(x, y, dim="time", **kwargs):
    """Compute regression coefficient along a selected dimension."""
    return regcoef(x, y, dim=dim, **kwargs)


def regline(x, y, dim="time", **kwargs):
    """Fit a simple regression line."""
    raise NotImplementedError("regline is not implemented yet.")


def reg_multlin(x, y, dim="time", **kwargs):
    """Fit a multiple linear regression model."""
    raise NotImplementedError("reg_multlin is not implemented yet.")
