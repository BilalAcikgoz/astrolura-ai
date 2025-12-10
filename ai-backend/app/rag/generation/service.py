from typing import Dict, Optional
from loguru import logger
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
import json

from app.config import get_settings
from app.rag.prompts import get_astrology_system_prompt

# OpenAI Pricing (per 1M tokens) - Updated as of December 2024
MODEL_PRICING = {
    "gpt-4o": {
        "input": 2.50,   # $2.50 per 1M input tokens
        "output": 10.00  # $10.00 per 1M output tokens
    },
    "gpt-4o-mini": {
        "input": 0.150,  # $0.150 per 1M input tokens
        "output": 0.600  # $0.600 per 1M output tokens
    },
    "gpt-4-turbo": {
        "input": 10.00,
        "output": 30.00
    },
    "gpt-4": {
        "input": 30.00,
        "output": 60.00
    },
    "gpt-3.5-turbo": {
        "input": 0.50,   # $0.50 per 1M input tokens
        "output": 1.50   # $1.50 per 1M output tokens
    },
}

class AstrologyGenerationService:
    # Service for generating astrological interpretations using LLM with RAG

    def __init__(
        self,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ):
        # Initialize generation service with OpenAI settings
        settings = get_settings()

        self.model = model or settings.openai_model
        self.temperature = temperature or settings.openai_temperature
        self.max_tokens = max_tokens or settings.openai_max_tokens
        self.top_p = settings.openai_top_p
        self.frequency_penalty = settings.openai_frequency_penalty
        self.presence_penalty = settings.openai_presence_penalty

        # Initialize OpenAI client
        self.client = OpenAI(api_key=settings.openai_api_key)

        logger.info(
            f"Initialized GenerationService with model={self.model}, "
            f"temperature={self.temperature}, max_tokens={self.max_tokens}"
        )

    def _calculate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> Dict[str, float]:
        """Calculate the cost of API call based on token usage."""
        # Find pricing for the model (check for base model name)
        pricing = None
        for model_key in MODEL_PRICING:
            if model.startswith(model_key):
                pricing = MODEL_PRICING[model_key]
                break

        if not pricing:
            # Default to gpt-4o-mini pricing if model not found
            pricing = MODEL_PRICING["gpt-4o-mini"]
            logger.warning(f"Model {model} not found in pricing table, using gpt-4o-mini pricing")

        # Calculate costs (pricing is per 1M tokens)
        input_cost = (prompt_tokens / 1_000_000) * pricing["input"]
        output_cost = (completion_tokens / 1_000_000) * pricing["output"]
        total_cost = input_cost + output_cost

        return {
            "input_cost": round(input_cost, 6),
            "output_cost": round(output_cost, 6),
            "total_cost": round(total_cost, 6)
        }

    def create_user_prompt(
        self,
        chart_data: Dict,
        context: str
    ) -> str:
        # Create user prompt with chart data and retrieved context from vector database

        # Convert chart data to formatted JSON string
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

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def generate_interpretation(
        self,
        chart_data: Dict,
        context: str,
        language: str = "tr"
    ) -> str:
        # Generate interpretation using OpenAI API with retry logic

        person_name = chart_data.get('chart_info', {}).get('name', 'Unknown')

        logger.info(
            f"Generating interpretation in {language} for {person_name}"
        )

        # Get system prompt based on language
        system_prompt = get_astrology_system_prompt(language)

        # Create user prompt
        user_prompt = self.create_user_prompt(chart_data, context)

        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=self.top_p,
                frequency_penalty=self.frequency_penalty,
                presence_penalty=self.presence_penalty
            )

            interpretation = response.choices[0].message.content

            # Log detailed token usage and cost
            usage = response.usage
            cost_info = self._calculate_cost(
                response.model,
                usage.prompt_tokens,
                usage.completion_tokens
            )

            logger.info(
                f"✨ LLM Generation Complete ✨\n"
                f"├─ Model: {response.model}\n"
                f"├─ Input Tokens: {usage.prompt_tokens:,}\n"
                f"├─ Output Tokens: {usage.completion_tokens:,}\n"
                f"├─ Total Tokens: {usage.total_tokens:,}\n"
                f"├─ Input Cost: ${cost_info['input_cost']:.6f}\n"
                f"├─ Output Cost: ${cost_info['output_cost']:.6f}\n"
                f"└─ Total Cost: ${cost_info['total_cost']:.6f}"
            )

            return interpretation

        except Exception as e:
            logger.error(f"Error generating interpretation: {str(e)}")
            raise


# Factory function to get a GenerationService instance
def get_astrology_generation_service(
    model: Optional[str] = None,
    temperature: Optional[float] = None
) -> AstrologyGenerationService:
    return AstrologyGenerationService(model=model, temperature=temperature)
