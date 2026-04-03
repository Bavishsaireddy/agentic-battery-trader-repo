"""
tests/test_tools.py — Unit tests against synthetic fixture data matching the pivoted schema.
"""

import pandas as pd
import pytest

from tools.revenue import compute_revenue_summary
from tools.dispatch import compare_dispatch_alignment
from tools.pricing import identify_high_value_windows
from tools.soc import analyze_soc_constraints
from tools.slippage import bid_slippage_analysis

@pytest.fixture
def synthetic_data():
    """Provides a minimal dataframe representing pivoted SCENARIO_NAME+SCHEDULE_TYPE."""
    data = {
        "START_DATETIME": pd.date_range("2026-01-26 00:00", periods=5, freq="5min", tz="UTC"),
        
        # Historical Expected
        "historical_expected_SOC": [100.0, 95.0, 90.0, 80.0, 70.0],
        "historical_expected_CHARGE_ENERGY": [0.0, 0.0, 0.0, 0.0, 0.0],
        "historical_expected_DISCHARGE_ENERGY": [5.0, 5.0, 10.0, 10.0, 0.0],
        "historical_expected_PRICE_ENERGY": [50.0, 60.0, 30.0, 40.0, 10.0],
        "historical_expected_REVENUE": [250.0, 300.0, 300.0, 400.0, 0.0],

        # Historical Cleared
        "historical_cleared_SOC": [100.0, 96.0, 91.0, 82.0, 72.0],
        "historical_cleared_CHARGE_ENERGY": [0.0, 0.0, 0.0, 0.0, 0.0],
        "historical_cleared_DISCHARGE_ENERGY": [4.0, 5.0, 9.0, 10.0, 0.0],
        "historical_cleared_PRICE_ENERGY": [55.0, 60.0, 32.0, 40.0, 10.0],
        "historical_cleared_REVENUE": [220.0, 300.0, 288.0, 400.0, 0.0],

        # Perfect Expected
        "perfect_expected_SOC": [100.0, 95.0, 90.0, 80.0, 70.0],
        "perfect_expected_CHARGE_ENERGY": [0.0, 0.0, 0.0, 0.0, 0.0],
        "perfect_expected_DISCHARGE_ENERGY": [5.0, 5.0, 10.0, 10.0, 0.0],
        "perfect_expected_PRICE_ENERGY": [55.0, 60.0, 32.0, 40.0, 10.0],
        "perfect_expected_REVENUE": [275.0, 300.0, 320.0, 400.0, 0.0],

        # Perfect Cleared
        "perfect_cleared_SOC": [100.0, 90.0, 80.0, 70.0, 60.0],
        "perfect_cleared_CHARGE_ENERGY": [0.0, 0.0, 0.0, 0.0, 0.0],
        "perfect_cleared_DISCHARGE_ENERGY": [10.0, 10.0, 10.0, 10.0, 0.0],
        "perfect_cleared_PRICE_ENERGY": [55.0, 60.0, 32.0, 40.0, 10.0],
        "perfect_cleared_REVENUE": [550.0, 600.0, 320.0, 400.0, 0.0],
    }
    return pd.DataFrame(data)

def test_revenue_tool(synthetic_data):
    result = compute_revenue_summary(synthetic_data)
    assert "historical_revenue" in result
    assert result["opportunity_cost"] > 0

def test_dispatch_tool(synthetic_data):
    result = compare_dispatch_alignment(synthetic_data)
    assert "misaligned_intervals" in result
    # We have misalignments on interval 0 and 2
    assert result["misaligned_intervals"] >= 1

def test_pricing_tool(synthetic_data):
    result = identify_high_value_windows(synthetic_data)
    assert "spike_capture_efficiency_pct" in result
    assert result["historical_discharge_in_spikes_mwh"] <= result["perfect_discharge_in_spikes_mwh"]

def test_soc_tool(synthetic_data):
    result = analyze_soc_constraints(synthetic_data)
    assert "implied_max_capacity_mwh" in result
    assert result["implied_max_capacity_mwh"] == 100.0

def test_slippage_tool(synthetic_data):
    result = bid_slippage_analysis(synthetic_data)
    assert "total_revenue_slipped" in result
    assert result["total_slippage_events"] > 0
