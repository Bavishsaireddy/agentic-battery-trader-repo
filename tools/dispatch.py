"""
tools/dispatch.py — compare_dispatch_alignment
Where did our expected bid diverge from the cleared reality historically?
"""

from typing import Dict, Any

import pandas as pd

from core.registry import registry
from config import DISPATCH_DELTA_THRESHOLD

@registry.register
def compare_dispatch_alignment(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Compare historical expected vs. historical cleared Energy to find dispatch misalignment.
    Returns the top mismatched intervals where delta exceeds threshold.
    """
    df = df.copy()
    
    # Analyze alignment purely using historical dataset
    df["delta_mwh"] = (df["historical_expected_DISCHARGE_ENERGY"] - df["historical_cleared_DISCHARGE_ENERGY"]).abs()
    
    mismatches = df[df["delta_mwh"] >= DISPATCH_DELTA_THRESHOLD]
    
    if mismatches.empty:
        return {"misaligned_intervals": 0, "mismatches": []}
    
    top_mismatches = mismatches.sort_values(by="delta_mwh", ascending=False).head(10)
    
    results = []
    for _, row in top_mismatches.iterrows():
        results.append({
            "timestamp": str(row["START_DATETIME"]),
            "expected_mwh": float(row["historical_expected_DISCHARGE_ENERGY"]),
            "cleared_mwh": float(row["historical_cleared_DISCHARGE_ENERGY"]),
            "delta_mwh": float(row["delta_mwh"]),
            "price_mwh": float(row["historical_cleared_PRICE_ENERGY"])
        })
        
    return {
        "misaligned_intervals": len(mismatches),
        "total_intervals": len(df),
        "mismatches": results
    }
