from typing import Dict, Optional
from loguru import logger
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
import json

from config import llm_settings
from src.prompts import get_astrology_system_prompt, get_transit_system_prompt


class LLMService:
    """astrolura-ai LLM generation service using OpenRouter API."""

    def __init__(self):
        self.model = llm_settings.llm_model
        self.temperature = llm_settings.llm_temperature
        self.max_tokens = llm_settings.llm_max_completion_tokens
        self.top_p = llm_settings.llm_top_p
        self.frequency_penalty = llm_settings.llm_frequency_penalty
        self.presence_penalty = llm_settings.llm_presence_penalty

        self.client = OpenAI(
            api_key=llm_settings.openrouter_api_key,
            base_url=llm_settings.openrouter_base_url,
        )

        logger.info(
            f"Initialized LLMService with model={self.model}, "
            f"temperature={self.temperature}, max_tokens={self.max_tokens}"
        )

    def create_user_prompt(self, chart_data: Dict, context: str) -> str:
        chart_json = json.dumps(chart_data, indent=2, ensure_ascii=False)

        user_prompt = f"""Aşağıdaki kişinin doğum haritasını, verilen astroloji bilgi kaynaklarını kullanarak profesyonel bir şekilde yorumla.

## ASTROLOJI BİLGİ KAYNAKLARI

{context}

## DOĞUM HARITASI VERİLERİ

```json
{chart_json}
```

Lütfen yukarıdaki natal harita verilerini detaylı analiz et ve sistem talimatlarına göre kapsamlı bir yorum hazırla."""

        return user_prompt

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def generate_interpretation(
        self, chart_data: Dict, context: str, language: str = "tr"
    ) -> str:
        person_name = chart_data.get("chart_info", {}).get("name", "Unknown")
        logger.info(f"Generating interpretation in {language} for {person_name}")

        system_prompt = get_astrology_system_prompt(language)
        user_prompt = self.create_user_prompt(chart_data, context)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=self.top_p,
                frequency_penalty=self.frequency_penalty,
                presence_penalty=self.presence_penalty,
                extra_headers={
                    "HTTP-Referer": "https://astrolura.ai",
                    "X-Title": "astrolura-ai",
                },
            )

            interpretation = response.choices[0].message.content

            usage = response.usage
            # Pricing per 1M tokens (USD) — update as OpenRouter rates change
            MODEL_PRICING = {
                "google/gemini-2.5-flash-lite": {"input": 0.075, "output": 0.30},
                "google/gemini-2.5-flash-preview": {"input": 0.15, "output": 0.60},
                "google/gemini-2.5-flash": {"input": 0.15, "output": 0.60},
            }
            model_key = response.model or self.model
            pricing = MODEL_PRICING.get(model_key, MODEL_PRICING.get(self.model))
            if pricing:
                input_cost = (usage.prompt_tokens / 1_000_000) * pricing["input"]
                output_cost = (usage.completion_tokens / 1_000_000) * pricing["output"]
                total_cost = input_cost + output_cost
                cost_line = f"\n  Estimated Cost: ${total_cost:.6f} (input=${input_cost:.6f}, output=${output_cost:.6f})"
            else:
                cost_line = f"\n  Estimated Cost: N/A (no pricing for model '{model_key}')"

            logger.info(
                f"LLM Generation Complete\n"
                f"  Model: {response.model}\n"
                f"  Input Tokens: {usage.prompt_tokens:,}\n"
                f"  Output Tokens: {usage.completion_tokens:,}\n"
                f"  Total Tokens: {usage.total_tokens:,}"
                f"{cost_line}"
            )

            return interpretation

        except Exception as e:
            logger.error(f"Error generating interpretation: {str(e)}")
            raise


    def create_transit_user_prompt(
        self, natal_chart_data: Dict, transit_data: Dict, context: str
    ) -> str:
        natal_json = json.dumps(natal_chart_data, indent=2, ensure_ascii=False)
        transit_json = json.dumps(
            {
                "transit_date": transit_data.get("transit_date"),
                "transit_planets": transit_data.get("transit_planets", []),
                "transit_aspects": transit_data.get("transit_aspects", []),
            },
            indent=2,
            ensure_ascii=False,
        )

        prompt = f"""Aşağıdaki natal harita ve transit verilerini kullanarak dönemsel bir transit yorumu hazırla.

## TRANSIT ASTROLOJİ BİLGİ KAYNAKLARI

{context}

## NATAL HARITA VERİLERİ

```json
{natal_json}
```

## TRANSİT VERİLERİ

```json
{transit_json}
```

Sistem talimatlarına göre kapsamlı bir transit yorumu hazırla."""

        return prompt

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def generate_transit_interpretation(
        self,
        natal_chart_data: Dict,
        transit_data: Dict,
        context: str,
        language: str = "tr",
    ) -> str:
        person_name = natal_chart_data.get("chart_info", {}).get("name", "Unknown")
        transit_date = transit_data.get("transit_date", "unknown date")
        logger.info(
            f"Generating transit interpretation in {language} for {person_name} on {transit_date}"
        )

        system_prompt = get_transit_system_prompt(language)
        user_prompt = self.create_transit_user_prompt(natal_chart_data, transit_data, context)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=self.top_p,
                frequency_penalty=self.frequency_penalty,
                presence_penalty=self.presence_penalty,
                extra_headers={
                    "HTTP-Referer": "https://astrolura.ai",
                    "X-Title": "astrolura-ai",
                },
            )

            interpretation = response.choices[0].message.content

            usage = response.usage
            MODEL_PRICING = {
                "google/gemini-2.5-flash-lite": {"input": 0.075, "output": 0.30},
                "google/gemini-2.5-flash-preview": {"input": 0.15, "output": 0.60},
                "google/gemini-2.5-flash": {"input": 0.15, "output": 0.60},
            }
            model_key = response.model or self.model
            pricing = MODEL_PRICING.get(model_key, MODEL_PRICING.get(self.model))
            if pricing:
                input_cost = (usage.prompt_tokens / 1_000_000) * pricing["input"]
                output_cost = (usage.completion_tokens / 1_000_000) * pricing["output"]
                total_cost = input_cost + output_cost
                cost_line = f"\n  Estimated Cost: ${total_cost:.6f} (input=${input_cost:.6f}, output=${output_cost:.6f})"
            else:
                cost_line = f"\n  Estimated Cost: N/A (no pricing for model '{model_key}')"

            logger.info(
                f"Transit LLM Generation Complete\n"
                f"  Model: {response.model}\n"
                f"  Input Tokens: {usage.prompt_tokens:,}\n"
                f"  Output Tokens: {usage.completion_tokens:,}\n"
                f"  Total Tokens: {usage.total_tokens:,}"
                f"{cost_line}"
            )

            return interpretation

        except Exception as e:
            logger.error(f"Error generating transit interpretation: {str(e)}")
            raise


def get_llm_service() -> LLMService:
    return LLMService()
