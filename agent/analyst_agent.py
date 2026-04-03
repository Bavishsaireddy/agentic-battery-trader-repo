import pandas as pd

from tools.revenue import compute_revenue_summary
from tools.dispatch import compare_dispatch_alignment
from tools.soc import analyze_soc_constraints
from tools.capture_timeline import capture_timeline_by_hour

class AnalystAgent:
    """Runs internal battery logic sequentially."""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        
    async def run(self) -> dict:
        """
        Executes analytical tools returning key finding dictionary.
        Wrapped in async to fit pipeline structure.
        """
        # Execute synchronously
        performance_summary = compute_revenue_summary(self.df)
        dispatch_summary = compare_dispatch_alignment(self.df)
        soc_summary = analyze_soc_constraints(self.df)
        timeline_summary = capture_timeline_by_hour(self.df)
        
        return {
            "performance_summary": performance_summary,
            "dispatch_summary": dispatch_summary,
            "soc_summary": soc_summary,
            "timeline_summary": timeline_summary
        }
