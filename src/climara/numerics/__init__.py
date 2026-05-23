"""NCL-style numerical function layer.

This subpackage follows the function-family organization of NCL's
``ni/src/lib/nfp`` and ``ni/src/lib/nfpfort`` sources, while implementing the
algorithms in pure Python.
"""

from .eof import eofunc, eofunc_ts
from .stat import dim_standardize, remove_monthly_climatology, calc_monthly_anomaly
from .dtrend import dtrend, lintrend, lintrend_total
from .regcoef import regcoef
from .covcorm import escorc, pattern_cor, pattern_cor_weighted
from .dimavgwgt import dim_avg_wgt, coslat_weights, sqrt_coslat_weights
from .runave import runave, wrunave, running_mean_3
from .linint2 import linint2, linint2_like, interpolate_like

__all__ = [
    "eofunc", "eofunc_ts",
    "dim_standardize", "remove_monthly_climatology", "calc_monthly_anomaly",
    "dtrend", "lintrend", "lintrend_total",
    "regcoef",
    "escorc", "pattern_cor", "pattern_cor_weighted",
    "dim_avg_wgt", "coslat_weights", "sqrt_coslat_weights",
    "runave", "wrunave", "running_mean_3",
    "linint2", "linint2_like", "interpolate_like",
]
