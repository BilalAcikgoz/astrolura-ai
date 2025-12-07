from typing import Dict, Optional
from loguru import logger
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
import json

from app.config import get_settings
from app.rag.prompts import get_system_prompt


class GenerationService:
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
        system_prompt = get_system_prompt(language)

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

            # Log token usage
            usage = response.usage
            logger.info(
                f"Generated interpretation: {usage.completion_tokens} tokens "
                f"(total: {usage.total_tokens}, prompt: {usage.prompt_tokens})"
            )

            return interpretation

        except Exception as e:
            logger.error(f"Error generating interpretation: {str(e)}")
            raise


# Factory function to get a GenerationService instance
def get_generation_service(
    model: Optional[str] = None,
    temperature: Optional[float] = None
) -> GenerationService:
    return GenerationService(model=model, temperature=temperature)
