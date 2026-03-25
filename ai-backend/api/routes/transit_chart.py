from fastapi import APIRouter, HTTPException, Request, status
from loguru import logger
from typing import Dict
import uuid
from datetime import datetime, timezone

from api.models import TransitRequest, TransitInterpretRequest
from api.models import TransitChartResponse, TransitInterpretationResponse, TransitPlanet, TransitAspect
from api.routes.birth_chart import chart_cache
from src.astrology.calculator import get_transit_calculator

router = APIRouter()

# In-memory transit cache (replace with Redis in production)
transit_cache: Dict[str, dict] = {}


@router.post(
    "/transit-chart/calculate",
    response_model=TransitChartResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate Transit Chart",
    description="Calculate transit planet positions and aspects to a natal chart for a given date",
)
async def calculate_transit_chart(body: TransitRequest):
    try:
        logger.info(f"Calculating transit chart for natal chart {body.chart_id} on {body.transit_date}")

        if body.chart_id not in chart_cache:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Natal chart not found. Please calculate the birth chart first.",
            )

        natal_chart_data = chart_cache[body.chart_id]
        calculator = get_transit_calculator()
        result = calculator.calculate_transits(
            natal_chart_data, body.transit_date, body.transit_time
        )

        # Strip internal-only fields before model construction
        transit_planet_fields = set(TransitPlanet.model_fields.keys())
        planet_dicts = [
            {k: v for k, v in p.items() if k in transit_planet_fields}
            for p in result["transit_planets"]
        ]
        transit_planets = [TransitPlanet(**p) for p in planet_dicts]
        transit_aspects = [TransitAspect(**a) for a in result["transit_aspects"]]

        # Cache full data (with longitude etc.) for pipeline use
        full_planet_dicts = [
            {k: v for k, v in p.items() if k != "planet_enum"}
            for p in result["transit_planets"]
        ]
        transit_id = str(uuid.uuid4())
        transit_cache[transit_id] = {
            "transit_id": transit_id,
            "natal_chart_id": body.chart_id,
            "transit_date": body.transit_date,
            "transit_time": body.transit_time,
            "transit_planets": full_planet_dicts,
            "transit_aspects": result["transit_aspects"],
        }

        logger.info(
            f"Transit chart calculated: ID={transit_id}, "
            f"{len(transit_planets)} planets, {len(transit_aspects)} aspects"
        )

        return TransitChartResponse(
            success=True,
            transit_id=transit_id,
            natal_chart_id=body.chart_id,
            transit_date=body.transit_date,
            transit_time=body.transit_time,
            transit_planets=transit_planets,
            transit_aspects=transit_aspects,
        )

    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error calculating transit chart: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate transit chart: {str(e)}",
        )


@router.post(
    "/transit-chart/interpret",
    response_model=TransitInterpretationResponse,
    status_code=status.HTTP_200_OK,
    summary="Interpret Transit Chart",
    description="Generate AI-powered transit interpretation using RAG pipeline",
)
async def interpret_transit_chart(body: TransitInterpretRequest, request: Request):
    try:
        logger.info(f"Interpreting transit chart {body.transit_id}")

        if body.transit_id not in transit_cache:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transit chart not found. Please calculate the transit chart first.",
            )

        transit_data = transit_cache[body.transit_id]
        natal_chart_id = transit_data["natal_chart_id"]

        if natal_chart_id not in chart_cache:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Natal chart not found.",
            )

        natal_chart_data = chart_cache[natal_chart_id]
        pipeline = getattr(request.app.state, "transit_pipeline", None)

        if pipeline is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Transit pipeline not initialized.",
            )

        interpretation = pipeline.run(
            natal_chart_data=natal_chart_data,
            transit_data=transit_data,
            language=body.language,
        )

        logger.info(f"Successfully generated transit interpretation for {body.transit_id}")

        return TransitInterpretationResponse(
            success=True,
            transit_id=body.transit_id,
            natal_chart_id=natal_chart_id,
            transit_date=transit_data["transit_date"],
            interpretation=interpretation,
            language=body.language,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error interpreting transit chart: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to interpret transit chart: {str(e)}",
        )


@router.get(
    "/transit-chart/{transit_id}",
    status_code=status.HTTP_200_OK,
    summary="Get Transit Chart",
    description="Retrieve a previously calculated transit chart",
)
async def get_transit_chart(transit_id: str):
    try:
        if transit_id not in transit_cache:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transit chart not found",
            )
        return {"success": True, "transit_id": transit_id, **transit_cache[transit_id]}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving transit chart: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve transit chart: {str(e)}",
        )
