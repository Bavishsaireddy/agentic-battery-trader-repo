import pandas as pd

from tools.battery_cycling import analyze_battery_cycling
from tools.charge_costs import compute_charge_costs

class EconomicsAgent:
    """Runs external hardware economic degradation and tariff tools sequentially."""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        
    async def run(self) -> dict:
        """
        Executes economic tools returning findings dictionary.
        Wrapped in async to fit parallel pipeline structure.
        """
        cycling_summary = analyze_battery_cycling(self.df)
        charge_cost_summary = compute_charge_costs(self.df)
        
        return {
            "cycling_summary": cycling_summary,
            "charge_cost_summary": charge_cost_summary
        }
