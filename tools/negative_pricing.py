"""
tools/negative_pricing.py — Negative Pricing Detection
Identify intervals where the market clearing price dropped below zero.
Measures accidental discharging (paying to discharge) or optimal charging (getting paid to charge).
"""

from typing import Dict, Any
import pandas as pd
from core.registry import registry

@registry.register
def identify_negative_pricing(df: pd.DataFrame) -> Dict[str, Any]:
    working_df = df.copy()
    
    # Filter to intervals where cleared price is negative
    negative_events = working_df[working_df["historical_cleared_PRICE_ENERGY"] < 0].copy()
    
    if negative_events.empty:
        return {
            "total_negative_intervals": 0,
            "max_negative_price": 0.0,
            "total_mwh_charged_at_negative": 0.0,
            "total_mwh_discharged_at_negative": 0.0
        }
        
    return {
        "total_negative_intervals": len(negative_events),
        "max_negative_price": float(negative_events["historical_cleared_PRICE_ENERGY"].min()),
        "total_mwh_charged_at_negative": float(negative_events["historical_cleared_CHARGE_ENERGY"].sum()),
        "total_mwh_discharged_at_negative": float(negative_events["historical_cleared_DISCHARGE_ENERGY"].sum())
    }
