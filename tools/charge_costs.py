"""
tools/charge_costs.py — Weighted Average Cost of Charging
Determines the effective $/MWh cost to charge the battery. High charge cost means bad sourcing.
"""

from typing import Dict, Any
import pandas as pd
from core.registry import registry

@registry.register
def compute_charge_costs(df: pd.DataFrame) -> Dict[str, Any]:
    working_df = df.copy()
    
    hist_charge = working_df[working_df["historical_cleared_CHARGE_ENERGY"] > 0]
    perf_charge = working_df[working_df["perfect_cleared_CHARGE_ENERGY"] > 0]
    
    hist_total_mwh = hist_charge["historical_cleared_CHARGE_ENERGY"].sum()
    perf_total_mwh = perf_charge["perfect_cleared_CHARGE_ENERGY"].sum()
    
    # Total spend = Charge Energy * Price
    hist_spend = (hist_charge["historical_cleared_CHARGE_ENERGY"] * hist_charge["historical_cleared_PRICE_ENERGY"]).sum()
    perf_spend = (perf_charge["perfect_cleared_CHARGE_ENERGY"] * perf_charge["perfect_cleared_PRICE_ENERGY"]).sum()
    
    hist_avg_cost = hist_spend / hist_total_mwh if hist_total_mwh > 0 else 0.0
    perf_avg_cost = perf_spend / perf_total_mwh if perf_total_mwh > 0 else 0.0
    
    return {
        "historical_total_charge_mwh": float(hist_total_mwh),
        "perfect_total_charge_mwh": float(perf_total_mwh),
        "historical_avg_charge_cost_usd": float(hist_avg_cost),
        "perfect_avg_charge_cost_usd": float(perf_avg_cost),
        "cost_inefficiency_usd_per_mwh": float(hist_avg_cost - perf_avg_cost)
    }
