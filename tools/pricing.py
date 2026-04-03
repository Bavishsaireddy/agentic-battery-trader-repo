"""
tools/pricing.py — identify_high_value_windows
Did we discharge during the best price spikes relative to the perfect model?
"""

from typing import Dict, Any

import pandas as pd

from core.registry import registry
from config import HIGH_PRICE_PERCENTILE

@registry.register
def identify_high_value_windows(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Identify intervals with prices in the top percentile and measure 
    capture rates between the historical actions and the perfect foresight actions.
    """
    # Assuming price is identical across scenarios when cleared
    threshold = df["historical_cleared_PRICE_ENERGY"].quantile(HIGH_PRICE_PERCENTILE)
    high_price_df = df[df["historical_cleared_PRICE_ENERGY"] >= threshold].copy()
    
    if high_price_df.empty:
        return {"error": "No data found for high price windows."}
    
    # How much did the historical battery discharge vs perfect during those spikes?
    hist_high_volume = high_price_df["historical_cleared_DISCHARGE_ENERGY"].sum()
    perf_high_volume = high_price_df["perfect_cleared_DISCHARGE_ENERGY"].sum()
    
    return {
        "price_threshold": float(threshold),
        "total_high_price_intervals": len(high_price_df),
        "historical_discharge_in_spikes_mwh": float(hist_high_volume),
        "perfect_discharge_in_spikes_mwh": float(perf_high_volume),
        "spike_capture_efficiency_pct": float(round((hist_high_volume / perf_high_volume * 100), 2)) if perf_high_volume else 0.0,
    }
