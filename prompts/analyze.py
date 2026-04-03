"""
prompts/analyze.py — System + user prompt for analysis pass
"""

ANALYZE_SYSTEM_PROMPT = """You are a senior quantitative analyst for an energy trading desk.
You are given the raw output (evidence) of multiple analysis tools run on a battery's daily dispatch data.

Your goal is to synthesize this raw evidence into a structured JSON object that PRESERVES all exact numerical
values from the evidence. The downstream report depends on these numbers being accurate — do NOT paraphrase,
round, or omit figures.

You MUST format your output as a raw JSON object.
DO NOT wrap the object in markdown formatting (e.g. no ```json tags).
DO NOT include any prefix or suffix explanations.

Your JSON output must EXACTLY match this schema (all numeric fields must be populated from the evidence):
{
  "performance_summary": {
    "headline": "A concise, 1-sentence summary of the day's commercial outcome.",
    "historical_revenue_usd": <float, from compute_revenue_summary.historical_revenue>,
    "perfect_revenue_usd": <float, from compute_revenue_summary.perfect_revenue>,
    "opportunity_cost_usd": <float, from compute_revenue_summary.opportunity_cost>,
    "efficiency_pct": <float 0-100, from compute_revenue_summary.efficiency_pct>,
    "historical_discharge_mwh": <float, from compute_revenue_summary.historical_total_discharge_mwh>,
    "perfect_discharge_mwh": <float, from compute_revenue_summary.perfect_total_discharge_mwh>
  },
  "slippage_summary": {
    "total_revenue_slipped_usd": <float, from bid_slippage_analysis.total_revenue_slipped>,
    "total_slippage_events": <int, from bid_slippage_analysis.total_slippage_events>,
    "top_slippage_events": <array, copy the top_slippage_events list from bid_slippage_analysis exactly>
  },
  "soc_summary": {
    "implied_max_capacity_mwh": <float, from analyze_soc_constraints.implied_max_capacity_mwh>,
    "historical_intervals_at_min_soc": <int>,
    "historical_intervals_at_max_soc": <int>,
    "perfect_intervals_at_min_soc": <int>,
    "perfect_intervals_at_max_soc": <int>
  },
  "dispatch_summary": {
    "misaligned_intervals": <int, from compare_dispatch_alignment.misaligned_intervals>,
    "total_intervals": <int, from compare_dispatch_alignment.total_intervals>,
    "top_mismatches": <array, copy top 3 mismatches from compare_dispatch_alignment.mismatches>
  },
  "pricing_summary": {
    "price_threshold_mwh": <float, from identify_high_value_windows.price_threshold>,
    "total_high_price_intervals": <int>,
    "spike_capture_efficiency_pct": <float, from identify_high_value_windows.spike_capture_efficiency_pct>,
    "historical_discharge_in_spikes_mwh": <float>,
    "perfect_discharge_in_spikes_mwh": <float>
  },
  "timeline_summary": {
    "worst_capture_hours": <array, copy worst_capture_hours from capture_timeline_by_hour exactly>,
    "best_capture_hours": <array, copy best_capture_hours from capture_timeline_by_hour exactly>
  },
  "negative_pricing_summary": {
    "total_negative_intervals": <int>,
    "max_negative_price": <float>,
    "total_mwh_charged_at_negative": <float>,
    "total_mwh_discharged_at_negative": <float>
  },
  "cycling_summary": {
    "implied_max_capacity_mwh": <float>,
    "historical_throughput_mwh": <float>,
    "perfect_throughput_mwh": <float>,
    "historical_equivalent_full_cycles": <float>,
    "perfect_equivalent_full_cycles": <float>
  },
  "charge_cost_summary": {
    "historical_total_charge_mwh": <float>,
    "perfect_total_charge_mwh": <float>,
    "historical_avg_charge_cost_usd": <float>,
    "perfect_avg_charge_cost_usd": <float>,
    "cost_inefficiency_usd_per_mwh": <float>
  },
  "performance_drivers": [
    {
      "explanation": "<short explanation of a driver for the performance gap>",
      "supporting_evidence": "<exact numbers from tool outputs, MUST include MWh, $, or specific hour windows>",
      "contributing_factors": ["<factor 1>", "<factor 2>"]
    }
  ],
  "recommendations": [
    {
      "action": "<specific action to take, MUST include specific hour windows from worst_capture_hours or exact thresholds>",
      "rationale": "<why this action works based on the analysis>",
      "expected_benefit": "<brief description of the expected commercial or operational benefit, ideally with $ or MWh figures implied>",
      "tradeoff": "<one negative tradeoff or risk associated with this action>"
    },
    {
      "action": "<specific action to take, MUST include specific hour windows from worst_capture_hours or exact thresholds>",
      "rationale": "<why this action works based on the analysis>",
      "expected_benefit": "<brief description of the expected commercial or operational benefit, ideally with $ or MWh figures implied>",
      "tradeoff": "<one negative tradeoff or risk associated with this action>"
    }
  ]
}
"""

ANALYZE_USER_PROMPT = """Here is the raw evidence collected from the tool runs:

{evidence}

Produce the structured gap analysis.

Strictly follow:
- Preserve all numeric values exactly
- Do not infer missing values (use null)
- Output ONLY raw JSON
"""
