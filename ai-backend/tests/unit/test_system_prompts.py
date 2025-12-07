"""
Unit tests for system prompts.
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.rag.prompts import get_system_prompt, TURKISH_SYSTEM_PROMPT, ENGLISH_SYSTEM_PROMPT


class TestSystemPrompts:
    """Tests for system prompts."""

    def test_turkish_prompt_exists(self):
        """Test that Turkish prompt is defined."""
        assert TURKISH_SYSTEM_PROMPT is not None
        assert len(TURKISH_SYSTEM_PROMPT) > 100

    def test_english_prompt_exists(self):
        """Test that English prompt is defined."""
        assert ENGLISH_SYSTEM_PROMPT is not None
        assert len(ENGLISH_SYSTEM_PROMPT) > 100

    def test_get_system_prompt_turkish(self):
        """Test getting Turkish system prompt."""
        prompt = get_system_prompt("tr")
        assert prompt == TURKISH_SYSTEM_PROMPT

    def test_get_system_prompt_english(self):
        """Test getting English system prompt."""
        prompt = get_system_prompt("en")
        assert prompt == ENGLISH_SYSTEM_PROMPT

    def test_get_system_prompt_default(self):
        """Test default language is Turkish."""
        prompt = get_system_prompt()
        assert prompt == TURKISH_SYSTEM_PROMPT

    def test_get_system_prompt_case_insensitive(self):
        """Test that language code is case insensitive."""
        assert get_system_prompt("EN") == ENGLISH_SYSTEM_PROMPT
        assert get_system_prompt("TR") == TURKISH_SYSTEM_PROMPT

    def test_turkish_prompt_content(self):
        """Test Turkish prompt contains key elements."""
        prompt = TURKISH_SYSTEM_PROMPT

        # Should mention astrology
        assert "astrolog" in prompt.lower()

        # Should have structure guidelines
        assert "YORUM YAPILANDIRMASI" in prompt or "yapılandırma" in prompt.lower()

        # Should mention Sun, Moon, Ascendant
        assert "Güneş" in prompt or "guneş" in prompt.lower()
        assert "Ay" in prompt
        assert "Yükselen" in prompt or "yukselen" in prompt.lower()

        # Should mention elements
        assert "Ateş" in prompt or "ates" in prompt.lower()
        assert "Toprak" in prompt
        assert "Hava" in prompt
        assert "Su" in prompt

        # Should mention aspects
        assert "Aspekt" in prompt or "aspekt" in prompt.lower()

        # Should be positive and constructive
        assert "POZİTİF" in prompt or "pozitif" in prompt.lower()

    def test_english_prompt_content(self):
        """Test English prompt contains key elements."""
        prompt = ENGLISH_SYSTEM_PROMPT

        # Should mention astrology
        assert "astrologer" in prompt.lower()

        # Should have structure guidelines
        assert "INTERPRETATION STRUCTURE" in prompt

        # Should mention Sun, Moon, Ascendant
        assert "Sun" in prompt
        assert "Moon" in prompt
        assert "Ascendant" in prompt or "Rising" in prompt

        # Should mention elements
        assert "Fire" in prompt
        assert "Earth" in prompt
        assert "Air" in prompt
        assert "Water" in prompt

        # Should mention aspects
        assert "Aspect" in prompt or "aspect" in prompt

        # Should be positive and constructive
        assert "POSITIVE" in prompt or "positive" in prompt.lower()

    def test_prompt_has_markdown_instructions(self):
        """Test that prompts include markdown formatting instructions."""
        assert "Markdown" in TURKISH_SYSTEM_PROMPT or "markdown" in TURKISH_SYSTEM_PROMPT.lower()
        assert "Markdown" in ENGLISH_SYSTEM_PROMPT or "markdown" in ENGLISH_SYSTEM_PROMPT.lower()

    def test_prompt_ethical_guidelines(self):
        """Test that prompts include ethical guidelines."""
        # Turkish
        tr_prompt = TURKISH_SYSTEM_PROMPT.lower()
        assert "deterministik" in tr_prompt or "etik" in tr_prompt

        # English
        en_prompt = ENGLISH_SYSTEM_PROMPT.lower()
        assert "deterministic" in en_prompt or "ethical" in en_prompt

    def test_unknown_language_falls_back_to_turkish(self):
        """Test that unknown language codes fall back to Turkish."""
        prompt = get_system_prompt("fr")  # French not supported
        assert prompt == TURKISH_SYSTEM_PROMPT

        prompt = get_system_prompt("unknown")
        assert prompt == TURKISH_SYSTEM_PROMPT
