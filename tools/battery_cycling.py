"""
tools/battery_cycling.py — Battery Wear / Equivalent Full Cycles (EFC)
Calculates throughput and equivalent full cycles to measure physical asset degradation.
"""

from typing import Dict, Any
import pandas as pd
from core.registry import registry

@registry.register
def analyze_battery_cycling(df: pd.DataFrame) -> Dict[str, Any]:
    working_df = df.copy()
    
    # Deduce max capacity (same methodology as soc.py)
    max_capacity = max(working_df["historical_cleared_SOC"].max(), working_df["perfect_cleared_SOC"].max())
    
    # Fallback if somehow 0
    if max_capacity <= 0:
        max_capacity = 1.0 
        
    hist_throughput_mwh = working_df["historical_cleared_DISCHARGE_ENERGY"].sum()
    perf_throughput_mwh = working_df["perfect_cleared_DISCHARGE_ENERGY"].sum()
    
    # Equivalent Full Cycles (EFC) = Total Discharge / Max Capacity
    hist_efc = hist_throughput_mwh / max_capacity
    perf_efc = perf_throughput_mwh / max_capacity
    
    return {
        "implied_max_capacity_mwh": float(max_capacity),
        "historical_throughput_mwh": float(hist_throughput_mwh),
        "perfect_throughput_mwh": float(perf_throughput_mwh),
        "historical_equivalent_full_cycles": float(hist_efc),
        "perfect_equivalent_full_cycles": float(perf_efc)
    }
