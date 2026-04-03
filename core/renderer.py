"""
core/renderer.py — ReportRenderer
Saves Markdown, and safely structures trader output for review.
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ReportRenderer:
    """Renders formatting wrappers around the final report and saves execution state."""

    def __init__(self, output_path: Path):
        self.output_path = output_path

    def render(self, content_md: str) -> None:
        """
        Takes raw markdown, ensures directory structuring, writes it out to disk,
        and provides terminal pointers for the trader.
        Optionally, you could add HTML generation with `markdown` package here.
        """
        logger.info("ReportRenderer initialized. Writing to %s", self.output_path)
        
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.output_path, "w", encoding="utf-8") as f:
            f.write(content_md)
            
        logger.info("ReportRenderer successfully dumped final Trader Report.")
