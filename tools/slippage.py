"""
tools/slippage.py — bid_slippage_analysis
Revenue gap between what we bid and what actually cleared historically.
"""

from typing import Dict, Any

import pandas as pd

from core.registry import registry
from config import SLIPPAGE_THRESHOLD_PCT

@registry.register
def bid_slippage_analysis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze historical bid slippage directly correlating to money lost.
    Returns total volume slipped and top affected intervals.
    """
    df = df.copy()
    
    # Slippage is when expected revenue was higher than cleared revenue
    df["slippage_revenue"] = df["historical_expected_REVENUE"] - df["historical_cleared_REVENUE"]
    
    # Filter rows where expected was > 0 to avoid basic zeroes producing div errors
    valid_expected = df[df["historical_expected_REVENUE"] > 0].copy()
    valid_expected["slippage_pct"] = valid_expected["slippage_revenue"] / valid_expected["historical_expected_REVENUE"]
    
    # Slippage cases thresholded
    slippage_events = valid_expected[valid_expected["slippage_pct"] > SLIPPAGE_THRESHOLD_PCT]
    
    total_dollar_slipped = slippage_events["slippage_revenue"].sum()
    
    top_events = slippage_events.sort_values(by="slippage_revenue", ascending=False).head(5)
    
    events_list = []
    for _, row in top_events.iterrows():
        events_list.append({
            "timestamp": str(row["START_DATETIME"]),
            "expected_revenue": float(row["historical_expected_REVENUE"]),
            "cleared_revenue": float(row["historical_cleared_REVENUE"]),
            "slippage_dollars": float(row["slippage_revenue"])
        })
        
    return {
        "total_revenue_slipped": float(total_dollar_slipped),
        "total_slippage_events": len(slippage_events),
        "top_slippage_events": events_list
    }
