from fastapi import APIRouter, HTTPException, status, Response
from loguru import logger
from typing import Dict

from app.api.models.request import BirthChartRequest, BirthChartInterpretRequest
from app.api.models.response import (
    BirthChartResponse,
    InterpretationResponse
)
from app.core.astrology.calculator import get_calculator
from app.core.geocoding.service import GeocodingError
from app.core.visualization import generate_birth_chart_svg

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

        # Generate SVG chart visualization
        try:
            chart_svg = generate_birth_chart_svg(chart_data, language="en")
            logger.info(f"Successfully generated SVG chart for {request.name}")
        except Exception as svg_error:
            logger.warning(f"Failed to generate SVG: {svg_error}")
            chart_svg = None

        logger.info(f"Successfully calculated chart for {request.name}, ID: {chart_id}")

        # Return response
        return BirthChartResponse(
            success=True,
            chart_id=chart_id,
            chart_data=chart_data,
            chart_svg=chart_svg
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

        # TODO: Implement RAG-powered interpretation
        # For now, return a placeholder
        interpretation = _generate_placeholder_interpretation(
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

@router.get(
    "/birth-chart/{chart_id}/svg",
    status_code=status.HTTP_200_OK,
    summary="Get Birth Chart SVG",
    description="Retrieve the SVG visualization of a calculated birth chart",
    response_class=Response
)
async def get_birth_chart_svg(chart_id: str):
    """
    Get SVG visualization of a birth chart.
    Opens directly in browser for viewing.
    """
    try:
        if chart_id not in chart_cache:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chart not found"
            )

        # Get chart data from cache
        chart_data_dict = chart_cache[chart_id]

        # Convert dict back to BirthChartData object
        from app.api.models.response import BirthChartData
        chart_data = BirthChartData(**chart_data_dict)

        # Generate SVG
        svg_content = generate_birth_chart_svg(chart_data, language="en")

        # Return SVG with proper content type
        return Response(
            content=svg_content,
            media_type="image/svg+xml",
            headers={
                "Content-Disposition": f'inline; filename="birth_chart_{chart_id}.svg"'
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating SVG: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate SVG: {str(e)}"
        )

def _generate_placeholder_interpretation(
    chart_data: dict,
    _style: str,
    language: str
) -> str:
    # Generate placeholder interpretation. TODO: Replace with RAG-powered interpretation
    # Note: _style parameter reserved for future RAG implementation
    if language == "tr":
        interpretation = f"""# {chart_data['chart_info']['name']} - Doğum Haritası Yorumu

## Genel Bakış
Bu yorum henüz yapay zeka tarafından oluşturulmamaktadır. RAG sistemi implement edildiğinde, detaylı ve kişiselleştirilmiş yorumlar sunulacaktır.

## Temel Bilgiler
- **Doğum Tarihi**: {chart_data['chart_info']['birth_date']}
- **Doğum Saati**: {chart_data['chart_info']['birth_time']}
- **Doğum Yeri**: {chart_data['chart_info']['location']['city']}, {chart_data['chart_info']['location']['country']}
- **Yükselen Burç**: {chart_data['ascendant']['sign']}
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
- **Rising Sign**: {chart_data['ascendant']['sign_en']}
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
