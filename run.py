"""
run.py — Thin CLI orchestrator — wires it all together.
"""

import asyncio
import logging

from config import REPORT_PATH, DATA_FILE_PATH
from core.loader import DataLoader
from core.renderer import ReportRenderer
from agent.orchestrator import Orchestrator

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

async def main_async():
    logger.info("Starting up powerline-battery-agent orchestration...")
    
    if not DATA_FILE_PATH:
        logger.error("DATA_FILE_PATH is not set in config / .env file.")
        return
        
    # 1. Load Data (DataLoader)
    logger.info("--- PHASE 0: Data Ingestion (DataLoader) ---")
    loader = DataLoader(DATA_FILE_PATH)
    df = loader.load()
    
    # 2. Run Pipeline (Orchestrator)
    logger.info("--- PHASE 1: Agent Pipeline Execution ---")
    orchestrator = Orchestrator(df)
    result = await orchestrator.run_pipeline_sync()
    
    logger.info("Pipeline Complete. Score: %.2f | Revisions: %d", result.eval_score, result.revision_count)
    
    # 3. ReportRenderer (File Dump)
    logger.info("--- PHASE 2: ReportRenderer ---")
    renderer = ReportRenderer(REPORT_PATH)
    renderer.render(result.report)
    logger.info("✅ Report written to: %s", REPORT_PATH)

def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
