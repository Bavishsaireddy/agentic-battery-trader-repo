"""
tools/capture_timeline.py — capture_timeline_by_hour
Buckets discharge capture rate by hour of day to show WHEN performance degraded.
"""

from typing import Dict, Any, List

import pandas as pd

from core.registry import registry


@registry.register
def capture_timeline_by_hour(df: pd.DataFrame) -> Dict[str, Any]:
    """
    For each hour of the day, compute:
      - historical discharge vs. perfect discharge (MWh)
      - capture rate (%) = historical / perfect * 100
      - average price during that hour

    Returns a sorted list of hourly buckets so the LLM can identify
    specific time windows where performance was weakest.
    """
    df = df.copy()

    # Ensure START_DATETIME is parsed as datetime
    df["START_DATETIME"] = pd.to_datetime(df["START_DATETIME"], utc=True)
    df["hour"] = df["START_DATETIME"].dt.hour

    hourly = (
        df.groupby("hour")
        .agg(
            hist_discharge=("historical_cleared_DISCHARGE_ENERGY", "sum"),
            perf_discharge=("perfect_cleared_DISCHARGE_ENERGY", "sum"),
            hist_revenue=("historical_cleared_REVENUE", "sum"),
            avg_price=("historical_cleared_PRICE_ENERGY", "mean"),
        )
        .reset_index()
    )

    timeline: List[Dict[str, Any]] = []
    for _, row in hourly.iterrows():
        hist = float(row["hist_discharge"])
        perf = float(row["perf_discharge"])
        capture_pct = round((hist / perf * 100), 2) if perf > 0 else 0.0

        timeline.append(
            {
                "hour": int(row["hour"]),
                "label": f"{int(row['hour']):02d}:00–{int(row['hour']):02d}:59",
                "historical_discharge_mwh": round(hist, 4),
                "perfect_discharge_mwh": round(perf, 4),
                "capture_pct": capture_pct,
                "historical_revenue_usd": round(float(row["hist_revenue"]), 2),
                "avg_price_per_mwh": round(float(row["avg_price"]), 4),
            }
        )

    # Identify worst 3 capture hours (where perfect discharge > 0)
    active_hours = [h for h in timeline if h["perfect_discharge_mwh"] > 0]
    worst_hours = sorted(active_hours, key=lambda h: h["capture_pct"])[:3]

    return {
        "hourly_breakdown": timeline,
        "worst_capture_hours": worst_hours,
        "best_capture_hours": sorted(active_hours, key=lambda h: h["capture_pct"], reverse=True)[:3],
    }
