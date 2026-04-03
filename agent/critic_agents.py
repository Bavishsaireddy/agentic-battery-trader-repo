import json
import logging
from typing import Tuple

from openai import AsyncOpenAI
import anthropic

from config import LLM_PROVIDER, LLM_MODEL, LLM_TEMPERATURE, OPENAI_API_KEY, ANTHROPIC_API_KEY, GROQ_API_KEY, OPENROUTER_API_KEY
from prompts.critic import QUANT_CRITIC_SYSTEM_PROMPT, STRATEGY_CRITIC_SYSTEM_PROMPT, CRITIC_USER_PROMPT

logger = logging.getLogger(__name__)

async def _call_critic_llm(system_prompt: str, user_prompt: str) -> str:
    if LLM_PROVIDER in ["openai", "groq", "openrouter"]:
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
        return response.choices[0].message.content
        
    elif LLM_PROVIDER == "anthropic":
        client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
        response = await client.messages.create(
            model=LLM_MODEL,
            temperature=LLM_TEMPERATURE,
            max_tokens=2048,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        return response.content[0].text
    else:
        raise ValueError(f"Unknown LLM_PROVIDER: {LLM_PROVIDER}")


class QuantCritic:
    """Evaluates mathematical grounding against the raw findings."""
    def __init__(self, findings: dict, draft: str):
        self.findings = findings
        self.draft = draft
        
    async def evaluate(self) -> Tuple[float, str]:
        findings_str = json.dumps(self.findings, indent=2)
        user_prompt = CRITIC_USER_PROMPT.format(findings=findings_str, draft=self.draft)
        
        content = await _call_critic_llm(QUANT_CRITIC_SYSTEM_PROMPT, user_prompt)
        
        try:
            content = content.replace("```json", "").replace("```", "").strip()
            data = json.loads(content)
            score = float(data.get("quant_score", 0.0))
            feedback = str(data.get("feedback", ""))
            return score, feedback
        except Exception as e:
            logger.error("QuantCritic JSON Parse error. Output: %s", content)
            return 0.0, "Quant Critic failed to parse output."


class StrategyCritic:
    """Evaluates the commercial logic and recommendation usefulness."""
    def __init__(self, findings: dict, draft: str):
        self.findings = findings
        self.draft = draft
        
    async def evaluate(self) -> Tuple[float, str]:
        findings_str = json.dumps(self.findings, indent=2)
        user_prompt = CRITIC_USER_PROMPT.format(findings=findings_str, draft=self.draft)
        
        content = await _call_critic_llm(STRATEGY_CRITIC_SYSTEM_PROMPT, user_prompt)
        
        try:
            content = content.replace("```json", "").replace("```", "").strip()
            data = json.loads(content)
            score = float(data.get("strategy_score", 0.0))
            feedback = str(data.get("feedback", ""))
            return score, feedback
        except Exception as e:
            logger.error("StrategyCritic JSON Parse error. Output: %s", content)
            return 0.0, "Strategy Critic failed to parse output."
