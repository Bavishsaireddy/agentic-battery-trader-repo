import pandas as pd

from tools.pricing import identify_high_value_windows
from tools.slippage import bid_slippage_analysis
from tools.negative_pricing import identify_negative_pricing

class MarketAgent:
    """Runs external market metrics sequentially."""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        
    async def run(self) -> dict:
        """
        Executes market tools returning findings dictionary.
        Wrapped in async to fit pipeline structure.
        """
        # Execute synchronously
        pricing_summary = identify_high_value_windows(self.df)
        slippage_summary = bid_slippage_analysis(self.df)
        negative_pricing_summary = identify_negative_pricing(self.df)
        
        return {
            "pricing_summary": pricing_summary,
            "slippage_summary": slippage_summary,
            "negative_pricing_summary": negative_pricing_summary
        }
