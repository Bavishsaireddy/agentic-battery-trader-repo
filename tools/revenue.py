"""
tools/revenue.py — compute_revenue_summary
High-level financial overview comparing historical vs optimal scenarios.
"""

from typing import Dict, Union

import pandas as pd

from core.registry import registry

@registry.register
def compute_revenue_summary(
    df: pd.DataFrame
) -> Dict[str, Union[float, Dict[str, float]]]:
    """
    Compute daily and total revenue, comparing the historical performance
    against the perfect foresight scenario.
    """
    
    # Calculate historical and perfect cleared revenues
    hist_cleared_rev = float(df["historical_cleared_REVENUE"].sum())
    perf_cleared_rev = float(df["perfect_cleared_REVENUE"].sum())
    
    # Opportunity Cost = Revenue left on the table
    opportunity_cost = perf_cleared_rev - hist_cleared_rev
    
    # Total historical energy cycled
    hist_discharge = float(df["historical_cleared_DISCHARGE_ENERGY"].sum())
    perf_discharge = float(df["perfect_cleared_DISCHARGE_ENERGY"].sum())

    return {
        "historical_revenue": round(hist_cleared_rev, 2),
        "perfect_revenue": round(perf_cleared_rev, 2),
        "opportunity_cost": round(opportunity_cost, 2),
        "historical_total_discharge_mwh": round(hist_discharge, 2),
        "perfect_total_discharge_mwh": round(perf_discharge, 2),
        "efficiency_pct": round((hist_cleared_rev / perf_cleared_rev * 100), 2) if perf_cleared_rev else 0.0
    }
