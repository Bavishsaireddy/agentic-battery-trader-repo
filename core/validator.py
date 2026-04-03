"""
core/validator.py — OutputValidator
Validates the structural integrity of the Gap Analysis JSON coming from the LLM,
ensuring it meets the required schema before downstream processing.
"""

import logging
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator, ValidationError

logger = logging.getLogger(__name__)


# ── Sub-models ────────────────────────────────────────────────────────────────

class PerformanceSummary(BaseModel):
    headline: str = Field(description="A concise summary of the day's performance.")
    historical_revenue_usd: float
    perfect_revenue_usd: float
    opportunity_cost_usd: float
    efficiency_pct: float
    historical_discharge_mwh: float
    perfect_discharge_mwh: float

    @field_validator("efficiency_pct")
    @classmethod
    def must_be_percentage(cls, v: float) -> float:
        if not (0.0 <= v <= 100.0):
            raise ValueError(f"efficiency_pct must be 0–100, got {v}")
        return v

    @field_validator("opportunity_cost_usd")
    @classmethod
    def opportunity_cost_non_negative(cls, v: float) -> float:
        if v < 0:
            raise ValueError(f"opportunity_cost_usd should be >= 0, got {v}")
        return v


class SlippageEvent(BaseModel):
    timestamp: str
    expected_revenue: float
    cleared_revenue: float
    slippage_dollars: float


class SlippageSummary(BaseModel):
    total_revenue_slipped_usd: float
    total_slippage_events: int
    top_slippage_events: List[SlippageEvent] = Field(default_factory=list)


class SocSummary(BaseModel):
    implied_max_capacity_mwh: float
    historical_intervals_at_min_soc: int
    historical_intervals_at_max_soc: int
    perfect_intervals_at_min_soc: int
    perfect_intervals_at_max_soc: int


class DispatchMismatch(BaseModel):
    timestamp: str
    expected_mwh: float
    cleared_mwh: float
    delta_mwh: float
    price_mwh: float


class DispatchSummary(BaseModel):
    misaligned_intervals: int
    total_intervals: int
    top_mismatches: List[DispatchMismatch] = Field(default_factory=list)


class PricingSummary(BaseModel):
    price_threshold_mwh: float
    total_high_price_intervals: int
    spike_capture_efficiency_pct: float
    historical_discharge_in_spikes_mwh: float
    perfect_discharge_in_spikes_mwh: float


class CaptureHour(BaseModel):
    hour: int
    label: str
    historical_discharge_mwh: float
    perfect_discharge_mwh: float
    capture_pct: float
    historical_revenue_usd: float
    avg_price_per_mwh: float


class TimelineSummary(BaseModel):
    worst_capture_hours: List[CaptureHour] = Field(default_factory=list)
    best_capture_hours: List[CaptureHour] = Field(default_factory=list)


class NegativePricingSummary(BaseModel):
    total_negative_intervals: int
    max_negative_price: float
    total_mwh_charged_at_negative: float
    total_mwh_discharged_at_negative: float


class CyclingSummary(BaseModel):
    implied_max_capacity_mwh: float
    historical_throughput_mwh: float
    perfect_throughput_mwh: float
    historical_equivalent_full_cycles: float
    perfect_equivalent_full_cycles: float


class ChargeCostSummary(BaseModel):
    historical_total_charge_mwh: float
    perfect_total_charge_mwh: float
    historical_avg_charge_cost_usd: float
    perfect_avg_charge_cost_usd: float
    cost_inefficiency_usd_per_mwh: float


class PerformanceDriver(BaseModel):
    explanation: str
    supporting_evidence: str
    contributing_factors: List[str]


class Recommendation(BaseModel):
    action: str
    rationale: str
    expected_benefit: str
    tradeoff: str


class GapAnalysisSchema(BaseModel):
    """Full schema matching the structured output mandated by the Analyzer prompt."""
    performance_summary: PerformanceSummary
    slippage_summary: SlippageSummary
    soc_summary: SocSummary
    dispatch_summary: DispatchSummary
    pricing_summary: PricingSummary
    timeline_summary: TimelineSummary
    negative_pricing_summary: NegativePricingSummary
    cycling_summary: CyclingSummary
    charge_cost_summary: ChargeCostSummary
    performance_drivers: List[PerformanceDriver]
    recommendations: List[Recommendation]


# ── OutputValidator worker ─────────────────────────────────────────────────────

class OutputValidator:
    """Validates arbitrary output dicts against the Gap Analysis Schema."""

    @staticmethod
    def validate_analysis(raw_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate the raw dictionary returned by the LLM analysis call.
        Raises ValueError if corrupted, shielding the Reporter from bad data.
        Returns the validated, type-coerced dict.
        """
        logger.info("Validating LLM structured analysis output...")
        try:
            validated = GapAnalysisSchema(**raw_analysis)
            logger.info("Output validation successful. Structure conforms to expected schema.")
            return validated.model_dump()
        except ValidationError as e:
            logger.error("LLM Output failed JSON structure validation:\n%s", e)
            raise ValueError(
                f"OutputValidator failure: the LLM output violates the required schema.\n{e}"
            )
