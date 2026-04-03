"""
tools/soc.py — analyze_soc_constraints
Where did state-of-charge artificially limit our ability to act?
"""

from typing import Dict, Any

import pandas as pd

from core.registry import registry

@registry.register
def analyze_soc_constraints(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Dynamically deduce limits of SOC capacity from the whole dataset, 
    then identify tracking bounds to monitor artificial constraints.
    """
    # Deduce max capacity dynamically
    max_capacity = max(df["historical_cleared_SOC"].max(), df["perfect_cleared_SOC"].max())
    
    # Treat top 5% as max SOC limit, bottom 5% as min SOC limit realistically
    soc_max_bound = max_capacity * 0.95
    soc_min_bound = max_capacity * 0.05
    
    hist_constrained_min = df[df["historical_cleared_SOC"] <= soc_min_bound]
    hist_constrained_max = df[df["historical_cleared_SOC"] >= soc_max_bound]
    
    perf_constrained_min = df[df["perfect_cleared_SOC"] <= soc_min_bound]
    perf_constrained_max = df[df["perfect_cleared_SOC"] >= soc_max_bound]
    
    return {
        "implied_max_capacity_mwh": float(max_capacity),
        "historical_intervals_at_min_soc": len(hist_constrained_min),
        "historical_intervals_at_max_soc": len(hist_constrained_max),
        "perfect_intervals_at_min_soc": len(perf_constrained_min),
        "perfect_intervals_at_max_soc": len(perf_constrained_max),
    }
