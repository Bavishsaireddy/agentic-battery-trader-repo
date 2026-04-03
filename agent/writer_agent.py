import json
import logging

from openai import AsyncOpenAI
import anthropic

from config import LLM_PROVIDER, LLM_MODEL, LLM_TEMPERATURE, OPENAI_API_KEY, ANTHROPIC_API_KEY, GROQ_API_KEY, OPENROUTER_API_KEY
from prompts.report import REPORT_SYSTEM_PROMPT, REPORT_USER_PROMPT

logger = logging.getLogger(__name__)

class WriterAgent:
    """Formats the JSON findings dict and optional critic feedback into Markdown report."""
    def __init__(self, findings: dict, feedback: str = ""):
        self.findings = findings
        self.feedback = feedback
        
    async def run(self) -> str:
        findings_str = json.dumps(self.findings, indent=2)
        feedback_str = f"CRITIC FEEDBACK TO INCORPORATE:\n{self.feedback}" if self.feedback else ""
        
        system_prompt = REPORT_SYSTEM_PROMPT
        user_prompt = REPORT_USER_PROMPT.format(analysis=findings_str, feedback=feedback_str)
        
        logger.info("Calling LLM (%s:%s) for final report draft...", LLM_PROVIDER, LLM_MODEL)
        
        if LLM_PROVIDER == "openai" or LLM_PROVIDER == "groq" or LLM_PROVIDER == "openrouter":
            base_url = None
            api_key = OPENAI_API_KEY
            if LLM_PROVIDER == "groq":
                base_url = "https://api.groq.com/openai/v1"
                api_key = GROQ_API_KEY
            elif LLM_PROVIDER == "openrouter":
                base_url = "https://openrouter.ai/api/v1"
                api_key = OPENROUTER_API_KEY
                
            client = AsyncOpenAI(api_key=api_key, base_url=base_url)
            response = await client.chat.completions.create(
                model=LLM_MODEL,
                temperature=LLM_TEMPERATURE,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            content = response.choices[0].message.content
            
        elif LLM_PROVIDER == "anthropic":
            client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
            response = await client.messages.create(
                model=LLM_MODEL,
                temperature=LLM_TEMPERATURE,
                max_tokens=4096,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            content = response.content[0].text
        else:
            raise ValueError(f"Unknown LLM_PROVIDER: {LLM_PROVIDER}")

        return content
