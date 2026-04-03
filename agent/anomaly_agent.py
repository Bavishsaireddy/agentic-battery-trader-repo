import logging
import pandas as pd

logger = logging.getLogger(__name__)

class AnomalyAgent:
    """Deterministic Pre-Flight validator to scan the Pandas DataFrame for corrupted logic."""
    def __init__(self, df: pd.DataFrame):
        self.df = df
        
    def check_anomalies(self) -> dict:
        logger.info("Running Pre-Flight Data Validation...")
        anomalies = []
        
        # 1. Null Value Check
        null_count = self.df.isnull().sum().sum()
        if null_count > 0:
            anomalies.append(f"CRITICAL: Found {null_count} total null/NaN values across the CSV payload.")
            
        # 2. Impossible SOC (Below Zero) Check
        if "SOC" in self.df.columns:
            sub_zero_soc = len(self.df[self.df["SOC"] < 0])
            if sub_zero_soc > 0:
                anomalies.append(f"WARNING: SOC dropped below 0 MWh for {sub_zero_soc} intervals. Possible telemetry error.")
                
        # 3. Simultaneous Charge/Discharge Check
        if "CHARGE_ENERGY" in self.df.columns and "DISCHARGE_ENERGY" in self.df.columns:
            simultaneous_ops = len(self.df[(self.df["CHARGE_ENERGY"] > 0) & (self.df["DISCHARGE_ENERGY"] > 0)])
            if simultaneous_ops > 0:
                anomalies.append(f"WARNING: Found {simultaneous_ops} intervals attempting to simultaneously charge and discharge. This signifies a scheduling collision.")
        
        if not anomalies:
            logger.info("Pre-Flight Check Passed: Zero critical anomalies detected.")
            return {"anomalies_found": "None"}
        else:
            logger.warning("Pre-Flight Check flagged anomalies: %s", anomalies)
            return {"anomalies_found": anomalies}
