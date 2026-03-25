from fastapi import APIRouter, HTTPException, Request, status
from loguru import logger
from typing import Dict

from api.models import BirthChartRequest, BirthChartInterpretRequest
from api.models import BirthChartResponse, InterpretationResponse
from src.astrology.calculator import get_calculator
from src.astrology.geocoding import GeocodingError

router = APIRouter()

# In-memory chart cache (replace with Redis in production)
chart_cache: Dict[str, dict] = {}


@router.post(
    "/birth-chart/calculate",
    response_model=BirthChartResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate Birth Chart",
    description="Calculate a complete natal birth chart with planet positions, houses, and aspects",
)
async def calculate_birth_chart(request: BirthChartRequest):
    try:
        logger.info(f"Calculating birth chart for {request.name}")
        calculator = get_calculator()
        chart_id, chart_data = calculator.calculate_birth_chart(
            name=request.name,
            birth_date=request.birth_date,
            birth_time=request.birth_time,
            birth_place=request.birth_place,
            house_system=request.house_system,
        )
        chart_cache[chart_id] = chart_data.model_dump()
        logger.info(f"Successfully calculated chart for {request.name}, ID: {chart_id}")
        return BirthChartResponse(success=True, chart_id=chart_id, chart_data=chart_data)

    except GeocodingError as e:
        logger.error(f"Geocoding error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Location error: {str(e)}",
        )
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid data: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Error calculating birth chart: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate birth chart: {str(e)}",
        )


@router.post(
    "/birth-chart/interpret",
    response_model=InterpretationResponse,
    status_code=status.HTTP_200_OK,
    summary="Interpret Birth Chart",
    description="Generate AI-powered interpretation of a birth chart using RAG pipeline",
)
async def interpret_birth_chart(body: BirthChartInterpretRequest, request: Request):
    try:
        logger.info(f"Interpreting chart {body.chart_id}")

        if body.chart_id not in chart_cache:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chart not found. Please calculate the chart first.",
            )

        chart_data = chart_cache[body.chart_id]
        pipeline = getattr(request.app.state, "birth_chart_pipeline", None)

        if pipeline is None:
            logger.warning("Pipeline not available, using placeholder interpretation")
            interpretation = _generate_placeholder_interpretation(
                chart_data, body.interpretation_style, body.language
            )
        else:
            try:
                interpretation = pipeline.run(
                    chart_data=chart_data, language=body.language
                )
            except Exception as e:
                logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
                logger.warning("Falling back to placeholder interpretation")
                interpretation = _generate_placeholder_interpretation(
                    chart_data, body.interpretation_style, body.language
                )

        logger.info(f"Successfully generated interpretation for chart {body.chart_id}")
        return InterpretationResponse(
            success=True,
            chart_id=body.chart_id,
            interpretation=interpretation,
            interpretation_style=body.interpretation_style,
            language=body.language,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error interpreting birth chart: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to interpret birth chart: {str(e)}",
        )


@router.get(
    "/birth-chart/{chart_id}",
    status_code=status.HTTP_200_OK,
    summary="Get Birth Chart",
    description="Retrieve a previously calculated birth chart",
)
async def get_birth_chart(chart_id: str):
    try:
        if chart_id not in chart_cache:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chart not found",
            )
        return {"success": True, "chart_id": chart_id, "chart_data": chart_cache[chart_id]}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving birth chart: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve birth chart: {str(e)}",
        )


def _generate_placeholder_interpretation(
    chart_data: dict,
    _style: str,
    language: str,
) -> str:
    ascendant = next(
        (p for p in chart_data["planets"] if p["name_en"] == "Ascendant"), None
    )

    if language == "tr":
        return f"""# {chart_data['chart_info']['name']} - Doğum Haritası Yorumu

## Genel Bakış
RAG pipeline bağlantısı kurulamadı. Lütfen Milvus bağlantısını kontrol edin.

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

---
*Pipeline bağlantısı aktif olduğunda detaylı yorum sunulacaktır.*
"""
    else:
        return f"""# {chart_data['chart_info']['name']} - Birth Chart Interpretation

## Overview
RAG pipeline connection unavailable. Please check the Milvus connection.

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

---
*Detailed interpretation will be available once the pipeline connection is active.*
"""
