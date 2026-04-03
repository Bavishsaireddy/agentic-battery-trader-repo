import asyncio
import logging
import pandas as pd

from agent.anomaly_agent import AnomalyAgent
from agent.analyst_agent import AnalystAgent
from agent.market_agent import MarketAgent
from agent.economics_agent import EconomicsAgent
from agent.writer_agent import WriterAgent
from agent.critic_agents import QuantCritic, StrategyCritic

logger = logging.getLogger(__name__)

class PipelineResult:
    def __init__(self, report: str, eval_score: float, revision_count: int):
        self.report = report
        self.eval_score = eval_score
        self.revision_count = revision_count

class Orchestrator:
    """Executes the pipeline completely in parallel via asyncio."""
    def __init__(self, df: pd.DataFrame):
        self.df = df
        
    async def run_pipeline_sync(self) -> PipelineResult:
        # 1. Pre-Flight Check (Synchronous execution)
        anomaly = AnomalyAgent(self.df)
        anomaly_findings = anomaly.check_anomalies()
        
        # 2. Parallel Metrics Launch
        logger.info("Orchestrator: Launching Analyst, Market, and Economics agents in parallel...")
        analyst = AnalystAgent(self.df)
        market = MarketAgent(self.df)
        economics = EconomicsAgent(self.df)
        
        a_task = asyncio.create_task(analyst.run())
        m_task = asyncio.create_task(market.run())
        e_task = asyncio.create_task(economics.run())
        
        analyst_out, market_out, economics_out = await asyncio.gather(a_task, m_task, e_task)
        
        logger.info("Orchestrator: Merging findings...")
        merged_findings = {**analyst_out, **market_out, **economics_out, "anomaly_checks": anomaly_findings}
        
        logger.info("Orchestrator: Awaiting WriterAgent generation...")
        writer = WriterAgent(merged_findings)
        draft = await writer.run()
        
        revision_count = 0
        final_score = 0.0
        
        logger.info("Orchestrator: Entering Dual Critic Loop...")
        for i in range(2):
            q_critic = QuantCritic(merged_findings, draft)
            s_critic = StrategyCritic(merged_findings, draft)
            
            logger.info("Critic pass %d: Awaiting Quant and Strategy eval...", i+1)
            q_task = asyncio.create_task(q_critic.evaluate())
            s_task = asyncio.create_task(s_critic.evaluate())
            
            (q_score, q_feed), (s_score, s_feed) = await asyncio.gather(q_task, s_task)
            
            avg_score = (q_score + s_score) / 2
            final_score = avg_score
            logger.info("  -> Quant Score=%.2f | Strategy Score=%.2f | Avg=%.2f", q_score, s_score, avg_score)
            
            if avg_score >= 7.5:
                logger.info("Draft unconditionally approved by Dual Critics.")
                break
                
            logger.info("Score below 7.5. Aggregating feedback and requesting Writer revision...")
            combined_feedback = f"[QUANT FEEDBACK]: {q_feed}\n[STRATEGY FEEDBACK]: {s_feed}"
            revision_count += 1
            writer = WriterAgent(merged_findings, combined_feedback)
            draft = await writer.run()
            
        logger.info("Orchestrator sequence complete.")
        return PipelineResult(report=draft, eval_score=final_score, revision_count=revision_count)
