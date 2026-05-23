"""NCL-style numerical function layer.

The module names and public function names follow NCL's numerical function
families where practical, while implementations are written in Python.
"""

from .runave import runave, runave_n, wgt_runave, wgt_runave_n
from .stat import (
    dim_rmvmean,
    dim_rmvmean_n,
    dim_standardize,
    dim_standardize_n,
    dim_rmsd,
    dim_rmsd_n,
    dim_stat4,
    dim_stat4_n,
)
from .eof import eofunc, eofunc_n, eofunc_ts, eofunc_ts_n, eofcov, eofcor, eof2data
from .dtrend import dtrend, dtrend_n, dtrend_msg, dtrend_msg_n, dtrend_quadratic
from .regcoef import regcoef, regcoef_n, regline, reg_multlin
from .covcorm import covcorm, covcorm_xy, escorc, esccr, pattern_cor
from .dimavgwgt import (
    dim_avg_wgt,
    dim_avg_wgt_n,
    dim_sum_wgt,
    dim_sum_wgt_n,
    coslat_weights,
    sqrt_coslat_weights,
)
from .linint2 import linint1, linint1_n, linint2, linint2_points, area_hi2lores


__all__ = [
    "runave",
    "runave_n",
    "wgt_runave",
    "wgt_runave_n",
    "dim_rmvmean",
    "dim_rmvmean_n",
    "dim_standardize",
    "dim_standardize_n",
    "dim_rmsd",
    "dim_rmsd_n",
    "dim_stat4",
    "dim_stat4_n",
    "eofunc",
    "eofunc_n",
    "eofunc_ts",
    "eofunc_ts_n",
    "eofcov",
    "eofcor",
    "eof2data",
    "dtrend",
    "dtrend_n",
    "dtrend_msg",
    "dtrend_msg_n",
    "dtrend_quadratic",
    "regcoef",
    "regcoef_n",
    "regline",
    "reg_multlin",
    "covcorm",
    "covcorm_xy",
    "escorc",
    "esccr",
    "pattern_cor",
    "dim_avg_wgt",
    "dim_avg_wgt_n",
    "dim_sum_wgt",
    "dim_sum_wgt_n",
    "coslat_weights",
    "sqrt_coslat_weights",
    "linint1",
    "linint1_n",
    "linint2",
    "linint2_points",
    "area_hi2lores",
]
