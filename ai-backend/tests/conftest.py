"""
Pytest configuration and fixtures for tests.
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


# Sample chart data for testing
@pytest.fixture
def sample_chart_data():
    """Provide sample birth chart data for testing."""
    return {
        "chart_info": {
            "name": "Test User",
            "birth_date": "1990-01-15",
            "birth_time": "14:30",
            "birth_datetime_local": "1990-01-15T14:30:00",
            "birth_datetime_utc": "1990-01-15T12:30:00Z",
            "location": {
                "city": "Istanbul",
                "country": "Turkey",
                "latitude": 41.0082,
                "longitude": 28.9784,
                "timezone": "Europe/Istanbul"
            },
            "house_system": "Placidus",
            "julian_day": 2447908.02083
        },
        "planets": [
            {
                "name": "Gunes",
                "name_en": "Sun",
                "symbol": "☉",
                "longitude": 295.5,
                "latitude": 0.0,
                "distance": 0.983,
                "speed": 1.019,
                "speed_display": "01°01'08\"",
                "sign": "Oglak",
                "sign_en": "Capricorn",
                "sign_symbol": "♑",
                "degree_in_sign": 25.5,
                "degree_display": "25°30'",
                "house": 10,
                "retrograde": False,
                "dignity": "neutral"
            },
            {
                "name": "Ay",
                "name_en": "Moon",
                "symbol": "☽",
                "longitude": 125.3,
                "latitude": 4.2,
                "distance": 0.0025,
                "speed": 13.5,
                "speed_display": "13°30'00\"",
                "sign": "Aslan",
                "sign_en": "Leo",
                "sign_symbol": "♌",
                "degree_in_sign": 5.3,
                "degree_display": "05°18'",
                "house": 5,
                "retrograde": False,
                "dignity": "neutral"
            },
            {
                "name": "Merkur",
                "name_en": "Mercury",
                "symbol": "☿",
                "longitude": 280.2,
                "latitude": -1.5,
                "distance": 1.32,
                "speed": 1.5,
                "speed_display": "01°30'00\"",
                "sign": "Oglak",
                "sign_en": "Capricorn",
                "sign_symbol": "♑",
                "degree_in_sign": 10.2,
                "degree_display": "10°12'",
                "house": 9,
                "retrograde": False,
                "dignity": "neutral"
            },
            {
                "name": "Venus",
                "name_en": "Venus",
                "symbol": "♀",
                "longitude": 310.5,
                "latitude": 2.1,
                "distance": 1.65,
                "speed": 1.2,
                "speed_display": "01°12'00\"",
                "sign": "Kova",
                "sign_en": "Aquarius",
                "sign_symbol": "♒",
                "degree_in_sign": 10.5,
                "degree_display": "10°30'",
                "house": 11,
                "retrograde": False,
                "dignity": "neutral"
            },
            {
                "name": "Mars",
                "name_en": "Mars",
                "symbol": "♂",
                "longitude": 250.8,
                "latitude": 1.8,
                "distance": 2.1,
                "speed": 0.7,
                "speed_display": "00°42'00\"",
                "sign": "Yay",
                "sign_en": "Sagittarius",
                "sign_symbol": "♐",
                "degree_in_sign": 10.8,
                "degree_display": "10°48'",
                "house": 8,
                "retrograde": False,
                "dignity": "neutral"
            },
            {
                "name": "Jupiter",
                "name_en": "Jupiter",
                "symbol": "♃",
                "longitude": 90.5,
                "latitude": 0.5,
                "distance": 5.2,
                "speed": 0.12,
                "speed_display": "00°07'12\"",
                "sign": "Yengec",
                "sign_en": "Cancer",
                "sign_symbol": "♋",
                "degree_in_sign": 0.5,
                "degree_display": "00°30'",
                "house": 4,
                "retrograde": False,
                "dignity": "exalted"
            },
            {
                "name": "Saturn",
                "name_en": "Saturn",
                "symbol": "♄",
                "longitude": 285.2,
                "latitude": 2.0,
                "distance": 10.5,
                "speed": 0.05,
                "speed_display": "00°03'00\"",
                "sign": "Oglak",
                "sign_en": "Capricorn",
                "sign_symbol": "♑",
                "degree_in_sign": 15.2,
                "degree_display": "15°12'",
                "house": 9,
                "retrograde": False,
                "dignity": "ruler"
            }
        ],
        "houses": [
            {"number": 1, "name": "1. Ev - Benlik", "cusp_longitude": 45.0, "sign": "Boga", "sign_en": "Taurus", "sign_symbol": "♉", "degree_in_sign": 15.0, "degree_display": "15°00'"},
            {"number": 2, "name": "2. Ev - Degerler", "cusp_longitude": 75.0, "sign": "Ikizler", "sign_en": "Gemini", "sign_symbol": "♊", "degree_in_sign": 15.0, "degree_display": "15°00'"},
            {"number": 3, "name": "3. Ev - Iletisim", "cusp_longitude": 105.0, "sign": "Yengec", "sign_en": "Cancer", "sign_symbol": "♋", "degree_in_sign": 15.0, "degree_display": "15°00'"},
            {"number": 4, "name": "4. Ev - Ev ve Aile", "cusp_longitude": 135.0, "sign": "Aslan", "sign_en": "Leo", "sign_symbol": "♌", "degree_in_sign": 15.0, "degree_display": "15°00'"},
            {"number": 5, "name": "5. Ev - Yaraticilik", "cusp_longitude": 165.0, "sign": "Basak", "sign_en": "Virgo", "sign_symbol": "♍", "degree_in_sign": 15.0, "degree_display": "15°00'"},
            {"number": 6, "name": "6. Ev - Saglik", "cusp_longitude": 195.0, "sign": "Terazi", "sign_en": "Libra", "sign_symbol": "♎", "degree_in_sign": 15.0, "degree_display": "15°00'"},
            {"number": 7, "name": "7. Ev - Iliskiler", "cusp_longitude": 225.0, "sign": "Akrep", "sign_en": "Scorpio", "sign_symbol": "♏", "degree_in_sign": 15.0, "degree_display": "15°00'"},
            {"number": 8, "name": "8. Ev - Donusum", "cusp_longitude": 255.0, "sign": "Yay", "sign_en": "Sagittarius", "sign_symbol": "♐", "degree_in_sign": 15.0, "degree_display": "15°00'"},
            {"number": 9, "name": "9. Ev - Felsefe", "cusp_longitude": 285.0, "sign": "Oglak", "sign_en": "Capricorn", "sign_symbol": "♑", "degree_in_sign": 15.0, "degree_display": "15°00'"},
            {"number": 10, "name": "10. Ev - Kariyer", "cusp_longitude": 315.0, "sign": "Kova", "sign_en": "Aquarius", "sign_symbol": "♒", "degree_in_sign": 15.0, "degree_display": "15°00'"},
            {"number": 11, "name": "11. Ev - Topluluk", "cusp_longitude": 345.0, "sign": "Balik", "sign_en": "Pisces", "sign_symbol": "♓", "degree_in_sign": 15.0, "degree_display": "15°00'"},
            {"number": 12, "name": "12. Ev - Manevi", "cusp_longitude": 15.0, "sign": "Koc", "sign_en": "Aries", "sign_symbol": "♈", "degree_in_sign": 15.0, "degree_display": "15°00'"}
        ],
        "aspects": [
            {"planet1": "Sun", "aspect": "Kavusma", "aspect_en": "Conjunction", "aspect_symbol": "☌", "planet2": "Mercury", "orb": 5.3, "angle": 0, "nature": "neutral"},
            {"planet1": "Sun", "aspect": "Kavusma", "aspect_en": "Conjunction", "aspect_symbol": "☌", "planet2": "Saturn", "orb": 10.3, "angle": 0, "nature": "neutral"},
            {"planet1": "Moon", "aspect": "Ucgen", "aspect_en": "Trine", "aspect_symbol": "△", "planet2": "Mars", "orb": 4.5, "angle": 120, "nature": "harmonious"},
            {"planet1": "Venus", "aspect": "Kare", "aspect_en": "Square", "aspect_symbol": "□", "planet2": "Mars", "orb": 0.3, "angle": 90, "nature": "challenging"},
            {"planet1": "Jupiter", "aspect": "Karsi", "aspect_en": "Opposition", "aspect_symbol": "☍", "planet2": "Saturn", "orb": 4.7, "angle": 180, "nature": "challenging"}
        ],
        "ascendant": {
            "name": "Yukselen",
            "name_en": "Ascendant",
            "sign": "Boga",
            "sign_en": "Taurus",
            "sign_symbol": "♉",
            "degree_in_sign": 15.0,
            "degree_display": "15°00'"
        },
        "elements": {
            "fire": 15.0,
            "earth": 45.0,
            "air": 20.0,
            "water": 20.0
        },
        "qualities": {
            "cardinal": 25.0,
            "fixed": 35.0,
            "mutable": 40.0
        }
    }


@pytest.fixture
def sample_documents():
    """Provide sample LangChain documents for testing."""
    from langchain.schema import Document
    return [
        Document(
            page_content="The Sun in Capricorn represents discipline, ambition, and a structured approach to life.",
            metadata={"source_file": "astrology_basics.pdf", "page_number": 1, "category": "general_astrology"}
        ),
        Document(
            page_content="Moon in Leo brings warmth, creativity, and a need for recognition in emotional expression.",
            metadata={"source_file": "lunar_positions.pdf", "page_number": 5, "category": "psychological_astrology"}
        ),
        Document(
            page_content="The Taurus Ascendant gives a grounded, sensual presence and values security and comfort.",
            metadata={"source_file": "rising_signs.pdf", "page_number": 12, "category": "chart_interpretation"}
        )
    ]


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    with patch('openai.OpenAI') as mock:
        client = MagicMock()
        mock.return_value = client
        yield client


@pytest.fixture
def mock_milvus_connection():
    """Mock Milvus connection for testing."""
    with patch('pymilvus.connections') as mock_conn:
        yield mock_conn


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    mock = MagicMock()
    mock.milvus_host = "localhost"
    mock.milvus_port = 19530
    mock.milvus_collection_name = "test_collection"
    mock.milvus_index_type = "IVF_FLAT"
    mock.milvus_metric_type = "L2"
    mock.milvus_nlist = 128
    mock.milvus_nprobe = 10
    mock.embedding_dimension = 1536
    mock.embedding_model = "text-embedding-3-small"
    mock.openai_api_key = "test-api-key"
    mock.openai_model = "gpt-4o-mini"
    mock.openai_temperature = 0.7
    mock.openai_max_tokens = 2000
    mock.openai_top_p = 0.9
    mock.openai_frequency_penalty = 0.0
    mock.openai_presence_penalty = 0.0
    mock.cache_dir = "/tmp/test_cache"
    return mock
