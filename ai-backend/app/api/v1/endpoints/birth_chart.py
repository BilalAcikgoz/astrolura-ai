from fastapi import APIRouter, HTTPException, status, Response
from loguru import logger
from typing import Dict

from app.api.models import BirthChartRequest, BirthChartInterpretRequest
from app.api.models import (
    BirthChartResponse,
    InterpretationResponse
)
from app.core.astrology.calculations.calculator import get_calculator
from app.core.astrology.geocoding import GeocodingError
from app.rag import get_astrology_rag_service_manager

router = APIRouter()

# In-memory cache for charts (in production, use Redis)
chart_cache: Dict[str, dict] = {}

@router.post(
    "/birth-chart/calculate",
    response_model=BirthChartResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate Birth Chart",
    description="Calculate a complete natal birth chart with planet positions, houses, and aspects"
)
async def calculate_birth_chart(request: BirthChartRequest):
    # Calculate birth chart from birth data
    try:
        logger.info(f"Calculating birth chart for {request.name}")

        # Get calculator
        calculator = get_calculator()

        # Calculate chart
        chart_id, chart_data = calculator.calculate_birth_chart(
            name=request.name,
            birth_date=request.birth_date,
            birth_time=request.birth_time,
            birth_place=request.birth_place,
            house_system=request.house_system
        )

        # Cache the chart data
        chart_cache[chart_id] = chart_data.model_dump()

        logger.info(f"Successfully calculated chart for {request.name}, ID: {chart_id}")

        # Return response
        return BirthChartResponse(
            success=True,
            chart_id=chart_id,
            chart_data=chart_data
        )

    except GeocodingError as e:
        logger.error(f"Geocoding error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Location error: {str(e)}"
        )
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid data: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error calculating birth chart: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate birth chart: {str(e)}"
        )

@router.post(
    "/birth-chart/interpret",
    response_model=InterpretationResponse,
    status_code=status.HTTP_200_OK,
    summary="Interpret Birth Chart",
    description="Generate AI-powered interpretation of a birth chart using RAG"
)
async def interpret_birth_chart(request: BirthChartInterpretRequest):
    # Generate interpretation for a calculated birth chart
    try:
        logger.info(f"Interpreting chart {request.chart_id}")

        # Check if chart exists in cache
        if request.chart_id not in chart_cache:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chart not found. Please calculate the chart first."
            )

        # Get chart data
        chart_data = chart_cache[request.chart_id]

        # Get RAG service manager
        rag_manager = get_astrology_rag_service_manager()

        # Check if RAG services are available
        if not rag_manager.is_connected:
            logger.warning("RAG services not available, using placeholder interpretation")
            interpretation = _generate_placeholder_interpretation(
                chart_data,
                request.interpretation_style,
                request.language
            )
        else:
            # Use RAG pipeline for interpretation
            interpretation = await _generate_rag_interpretation(
                rag_manager,
                chart_data,
                request.interpretation_style,
                request.language
            )

        logger.info(f"Successfully generated interpretation for chart {request.chart_id}")

        return InterpretationResponse(
            success=True,
            chart_id=request.chart_id,
            interpretation=interpretation,
            interpretation_style=request.interpretation_style,
            language=request.language
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error interpreting birth chart: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to interpret birth chart: {str(e)}"
        )


async def _generate_rag_interpretation(
    rag_manager,
    chart_data: dict,
    style: str,
    language: str
) -> str:
    """Generate interpretation using RAG pipeline."""
    try:
        logger.info(f"Generating RAG interpretation for {chart_data['chart_info']['name']}")

        # Get retrieval service
        retrieval_service = rag_manager.get_retrieval_service(
            top_k=5,
            similarity_threshold=1.5  # L2 distance threshold
        )

        # Retrieve relevant context from vector database
        logger.info("Retrieving context from knowledge base...")
        results = retrieval_service.retrieve_context(
            chart_data,
            max_queries=12,
            deduplicate=True
        )

        # Format context for LLM
        context = retrieval_service.format_context(results, max_chunks=15)

        logger.info(f"Retrieved {len(results)} relevant chunks for interpretation")

        # Generate interpretation using LLM
        generation_service = rag_manager.generation_service
        interpretation = generation_service.generate_interpretation(
            chart_data=chart_data,
            context=context,
            language=language
        )

        return interpretation

    except Exception as e:
        logger.error(f"RAG interpretation failed: {str(e)}", exc_info=True)
        # Fallback to placeholder if RAG fails
        logger.warning("Falling back to placeholder interpretation")
        return _generate_placeholder_interpretation(chart_data, style, language)

@router.get(
    "/birth-chart/{chart_id}",
    status_code=status.HTTP_200_OK,
    summary="Get Birth Chart",
    description="Retrieve a previously calculated birth chart"
)
async def get_birth_chart(chart_id: str):
    # Retrieve a calculated birth chart by ID
    try:
        if chart_id not in chart_cache:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chart not found"
            )

        chart_data = chart_cache[chart_id]

        return {
            "success": True,
            "chart_id": chart_id,
            "chart_data": chart_data
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving birth chart: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve birth chart: {str(e)}"
        )

def _generate_placeholder_interpretation(
    chart_data: dict,
    _style: str,
    language: str
) -> str:
    # Generate placeholder interpretation. TODO: Replace with RAG-powered interpretation
    # Note: _style parameter reserved for future RAG implementation

    # Find Ascendant in planets list
    ascendant = next((p for p in chart_data['planets'] if p['name_en'] == 'Ascendant'), None)

    if language == "tr":
        interpretation = f"""# {chart_data['chart_info']['name']} - Doğum Haritası Yorumu

## Genel Bakış
Bu yorum henüz yapay zeka tarafından oluşturulmamaktadır. RAG sistemi implement edildiğinde, detaylı ve kişiselleştirilmiş yorumlar sunulacaktır.

## Temel Bilgiler
- **Doğum Tarihi**: {chart_data['chart_info']['birth_date']}
- **Doğum Saati**: {chart_data['chart_info']['birth_time']}
- **Doğum Yeri**: {chart_data['chart_info']['location']['city']}, {chart_data['chart_info']['location']['country']}
- **Yükselen Burç**: {ascendant['sign'] if ascendant else 'N/A'}
- **Güneş Burcu**: {chart_data['planets'][0]['sign']}
- **Ay Burcu**: {chart_data['planets'][1]['sign']}

## Element Dengesi
- Ateş: {chart_data['elements']['fire']}%
- Toprak: {chart_data['elements']['earth']}%
- Hava: {chart_data['elements']['air']}%
- Su: {chart_data['elements']['water']}%

## Nitelik Dengesi
- Öncü: {chart_data['qualities']['cardinal']}%
- Sabit: {chart_data['qualities']['fixed']}%
- Değişken: {chart_data['qualities']['mutable']}%

---

*Bu yorum otomatik olarak oluşturulmuştur. RAG sistemi aktif olduğunda daha detaylı yorumlar sunulacaktır.*
"""
    else:
        interpretation = f"""# {chart_data['chart_info']['name']} - Birth Chart Interpretation

## Overview
This is a placeholder interpretation. Once the RAG system is implemented, detailed and personalized interpretations will be provided.

## Basic Information
- **Birth Date**: {chart_data['chart_info']['birth_date']}
- **Birth Time**: {chart_data['chart_info']['birth_time']}
- **Birth Place**: {chart_data['chart_info']['location']['city']}, {chart_data['chart_info']['location']['country']}
- **Rising Sign**: {ascendant['sign_en'] if ascendant else 'N/A'}
- **Sun Sign**: {chart_data['planets'][0]['sign_en']}
- **Moon Sign**: {chart_data['planets'][1]['sign_en']}

## Element Balance
- Fire: {chart_data['elements']['fire']}%
- Earth: {chart_data['elements']['earth']}%
- Air: {chart_data['elements']['air']}%
- Water: {chart_data['elements']['water']}%

## Quality Balance
- Cardinal: {chart_data['qualities']['cardinal']}%
- Fixed: {chart_data['qualities']['fixed']}%
- Mutable: {chart_data['qualities']['mutable']}%

---

*This is an automatically generated interpretation. More detailed interpretations will be available once the RAG system is active.*
"""

    return interpretation
