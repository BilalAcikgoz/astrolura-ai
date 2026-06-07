# Astro-Fala AI Backend

AI-powered astrology and fortune-telling platform backend service.

## Features

### Phase 1: Birth Chart Module (Implemented)

- **Birth Chart Calculation**
  - Accurate planet positions using Swiss Ephemeris
  - 12 house systems (Placidus, Koch, Equal, Whole Sign, etc.)
  - Aspect calculations with orbs
  - Element and quality distribution analysis
  - Planetary dignities (rulership, exaltation, detriment, fall)

- **Location Services**
  - Geocoding support (Nominatim/Google Maps/Mapbox)
  - Automatic timezone detection
  - DST handling

### Phase 2: RAG Interpretation (Coming Soon)

- AI-powered chart interpretation
- Multi-language support (Turkish/English)
- Personalized readings using RAG

## Technology Stack

- **Framework**: FastAPI 0.115.0
- **Astrology**: pyswisseph 2.10.3.2
- **Geocoding**: geopy 2.4.1, timezonefinder 6.5.2
- **Vector DB**: Milvus (via pymilvus 2.4.9)
- **LLM**: OpenAI GPT-4o
- **Embeddings**: OpenAI text-embedding-3-small (1536d)

## Installation

### Prerequisites

- Python 3.10+
- Virtual environment (recommended)

### Setup

1. **Clone the repository**
   ```bash
   cd astro-fala/ai-backend
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   # Copy .env and update with your keys
   # Important: Set your OPENAI_API_KEY
   ```

5. **Download Swiss Ephemeris data**
   ```bash
   python scripts/download_ephemeris.py
   ```

## Usage

### Running the Server

```bash
# Development mode (with hot reload)
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc

### Testing Birth Chart Calculation

```bash
python scripts/test_birth_chart.py
```

### API Endpoints

#### Calculate Birth Chart
```bash
POST /api/v1/birth-chart/calculate
Content-Type: application/json

{
  "name": "Test User",
  "birth_date": "1990-07-15",
  "birth_time": "14:30",
  "birth_place": "Istanbul, Turkey",
  "house_system": "placidus"
}
```

#### Interpret Birth Chart
```bash
POST /api/v1/birth-chart/interpret
Content-Type: application/json

{
  "chart_id": "550e8400-e29b-41d4-a716-446655440000",
  "interpretation_style": "detailed",
  "language": "tr"
}
```

#### Get Birth Chart
```bash
GET /api/v1/birth-chart/{chart_id}
```

## Project Structure

```
ai-backend/
├── app/
│   ├── api/
│   │   ├── models/
│   │   │   ├── request.py      # Request schemas
│   │   │   └── response.py     # Response schemas
│   │   └── v1/
│   │       └── endpoints/
│   │           └── birth_chart.py  # Birth chart endpoints
│   ├── core/
│   │   ├── astrology/
│   │   │   ├── calculator.py   # Birth chart calculator
│   │   │   └── constants.py    # Astrology constants
│   │   ├── geocoding/
│   │   │   └── service.py      # Geocoding service
│   │   └── visualization/
│   │       └── chart_svg.py    # Chart visualization (TODO)
│   ├── rag/
│   │   ├── embeddings/         # Embedding models (TODO)
│   │   ├── generation/         # LLM generation (TODO)
│   │   ├── knowledge_base/     # Astrology knowledge (TODO)
│   │   └── retrieval/          # RAG retrieval (TODO)
│   ├── utils/
│   └── config.py               # Configuration
├── scripts/
│   ├── download_ephemeris.py   # Download ephemeris data
│   └── test_birth_chart.py     # Test script
├── .env                        # Environment variables
├── main.py                     # FastAPI application
└── requirements.txt            # Dependencies
```

## Configuration

Key environment variables in `.env`:

```bash
# OpenAI
# ========================================
# Application Settings
# ========================================
APP_NAME=astrolura-ai Backend
APP_VERSION=1.0.0
DEBUG=True
ENVIRONMENT=development
LOG_LEVEL=INFO
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# ========================================
# Server Settings
# ========================================
HOST=0.0.0.0
PORT=8000
WORKERS=4

# ========================================
# Geocoding & Ephemeris
# ========================================
GEOCODING_PROVIDER=nominatim
EPHE_PATH=./src/astrology/ephe

# ========================================
# OpenRouter API Configuration
# ========================================
OPENROUTER_API_KEY=your-key-here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# ========================================
# LLM Configuration
# ========================================
LLM_MODEL=google/gemini-2.5-flash-lite
LLM_MAX_COMPLETION_TOKENS=16000
LLM_TIMEOUT=120
LLM_MAX_RETRIES=3
LLM_TEMPERATURE=0.7
LLM_TOP_P=0.9
LLM_FREQUENCY_PENALTY=0.0
LLM_PRESENCE_PENALTY=0.0

# ========================================
# Embedding Configuration
# ========================================
EMBEDDING_MODEL=openai/text-embedding-3-small
EMBEDDING_DIMENSION=1536
EMBEDDING_BATCH_SIZE=50
EMBEDDING_MAX_TOKENS=8191
EMBEDDING_RATE_LIMIT_PAUSE=0.1

# ========================================
# MILVUS Vector Database Configuration
# ========================================
MILVUS_HOST=localhost
MILVUS_PORT=19531
MILVUS_DATABASE=astrolura_db
MILVUS_BIRTH_CHART_COLLECTION=birthchart_documents
MILVUS_TRANSIT_CHART_COLLECTION=transitchart_documents
MILVUS_INDEX_TYPE=HNSW
MILVUS_METRIC_TYPE=COSINE
MILVUS_HNSW_M=16
MILVUS_HNSW_EF_CONSTRUCTION=256
MILVUS_HNSW_EF_SEARCH=200

# ========================================
# RAG Pipeline Configuration
# ========================================
SEARCH_TOP_K=5
SIMILARITY_THRESHOLD=0.5
MAX_CONTEXT_CHUNKS=15
MAX_QUERIES=12

# ========================================
# Cache Settings
# ========================================
CACHE_DIR=./cache
CACHE_TTL_SECONDS=3600

# ========================================
# Rate Limiting
# ========================================
RATE_LIMIT_ENABLED=True
RATE_LIMIT_REQUESTS_PER_MINUTE=60
RATE_LIMIT_REQUESTS_PER_DAY=1000

# ========================================
# Logging
# ========================================
LOG_FILE=logs/app.log
LOG_ROTATION=10 MB
LOG_RETENTION=30 days
```

## Development Roadmap

### ✅ Phase 1: Core Calculation (Completed)
- [x] Project setup
- [x] Swiss Ephemeris integration
- [x] Geocoding service
- [x] Birth chart calculation
- [x] API endpoints
- [x] Request/response validation

### 🔄 Phase 2: RAG System (In Progress)
- [ ] Knowledge base creation
- [ ] Embedding generation
- [ ] Vector store (Milvus) integration
- [ ] RAG retrieval pipeline
- [ ] LLM interpretation
- [ ] Prompt engineering

### 📋 Phase 3: Enhancements (Planned)
- [ ] SVG chart visualization
- [ ] Caching with Redis
- [ ] Rate limiting
- [ ] User authentication
- [ ] Database integration
- [ ] Chart comparison (synastry)

### 📋 Phase 4: Fortune Telling (Planned)
- [ ] Tarot card module
- [ ] Coffee fortune module
- [ ] Dream interpretation

## Testing

```bash
# Run tests (coming soon)
pytest

# Run with coverage
pytest --cov=app
```

## License

Proprietary - All rights reserved

## Contact

For questions or support, please contact the development team.
