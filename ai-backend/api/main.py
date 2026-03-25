from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import uvicorn
from contextlib import asynccontextmanager
import logging
import sys
from loguru import logger as loguru_logger

from config import app_settings
from api.models import ErrorResponse, HealthCheckResponse
from api.routes import birth_chart
from api.routes import transit_chart
from src.vectordb.store import get_birth_chart_store, get_transit_chart_store
from src.retrieval.service import get_retrieval_service, get_transit_retrieval_service
from src.llm.service import get_llm_service
from src.pipeline.pipeline import (
    BirthChartPipeline, set_birth_chart_pipeline,
    TransitPipeline, set_transit_pipeline,
)


def setup_logging():
    loguru_logger.remove()
    loguru_logger.add(
        sys.stdout,
        colorize=True,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan> - "
            "<level>{message}</level>"
        ),
        level=app_settings.log_level,
    )
    loguru_logger.add(
        app_settings.log_file,
        rotation=app_settings.log_rotation,
        retention=app_settings.log_retention,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
        level=app_settings.log_level,
    )

    class InterceptHandler(logging.Handler):
        def emit(self, record):
            try:
                level = loguru_logger.level(record.levelname).name
            except ValueError:
                level = record.levelno
            loguru_logger.opt(depth=6, exception=record.exc_info).log(
                level, record.getMessage()
            )

    logging.basicConfig(handlers=[InterceptHandler()], level=0)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    loguru_logger.info(f"Starting {app_settings.app_name} v{app_settings.app_version}")
    loguru_logger.info(f"Environment: {app_settings.environment}")
    loguru_logger.info(f"Debug mode: {app_settings.debug}")

    llm_service = get_llm_service()

    # Initialize Birth Chart RAG pipeline
    birth_chart_store = get_birth_chart_store()
    try:
        birth_chart_store.connect()
        birth_chart_store.load_collection()
        birth_chart_retrieval = get_retrieval_service(vector_store=birth_chart_store)
        birth_chart_pipeline = BirthChartPipeline(
            retrieval_service=birth_chart_retrieval,
            llm_service=llm_service,
        )
        set_birth_chart_pipeline(birth_chart_pipeline)
        app.state.birth_chart_pipeline = birth_chart_pipeline
        app.state.birth_chart_rag_connected = True
        loguru_logger.info("BirthChart RAG pipeline initialized successfully")
    except Exception as e:
        loguru_logger.warning(
            f"Failed to initialize BirthChart RAG pipeline: {e}. "
            "AI interpretation will fall back to placeholder."
        )
        app.state.birth_chart_pipeline = None
        app.state.birth_chart_rag_connected = False

    # Initialize Transit RAG pipeline
    transit_store = get_transit_chart_store()
    try:
        transit_store.connect()
        transit_store.load_collection()
        transit_retrieval = get_transit_retrieval_service()
        transit_retrieval.vector_store = transit_store
        transit_pipeline = TransitPipeline(
            retrieval_service=transit_retrieval,
            llm_service=llm_service,
        )
        set_transit_pipeline(transit_pipeline)
        app.state.transit_pipeline = transit_pipeline
        app.state.transit_rag_connected = True
        loguru_logger.info("Transit RAG pipeline initialized successfully")
    except Exception as e:
        loguru_logger.warning(
            f"Failed to initialize Transit RAG pipeline: {e}. "
            "Transit interpretation will use LLM directly."
        )
        app.state.transit_pipeline = None
        app.state.transit_rag_connected = False

    app.state.rag_connected = (
        getattr(app.state, "birth_chart_rag_connected", False)
        or getattr(app.state, "transit_rag_connected", False)
    )

    yield

    loguru_logger.info("Shutting down astrolura-ai")
    if getattr(app.state, "birth_chart_rag_connected", False):
        try:
            birth_chart_store.disconnect()
        except Exception:
            pass
    if getattr(app.state, "transit_rag_connected", False):
        try:
            transit_store.disconnect()
        except Exception:
            pass


app = FastAPI(
    title=app_settings.app_name,
    version=app_settings.app_version,
    description="astrolura-ai — AI-powered astrological birth chart interpretation",
    docs_url="/docs" if app_settings.debug else None,
    redoc_url="/redoc" if app_settings.debug else None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=app_settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = [
        {
            "field": " -> ".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        }
        for error in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            error="Validation Error",
            error_code="VALIDATION_ERROR",
            details={"errors": errors},
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    loguru_logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Internal Server Error",
            error_code="INTERNAL_ERROR",
            details={"message": str(exc) if app_settings.debug else "An error occurred"},
        ).model_dump(),
    )


@app.get("/health", response_model=HealthCheckResponse, tags=["System"])
async def health_check(request: Request):
    rag_connected = getattr(request.app.state, "rag_connected", False)
    return HealthCheckResponse(
        status="ok",
        version=app_settings.app_version,
        environment=app_settings.environment,
        rag_status="connected" if rag_connected else "disconnected",
    )


@app.get("/", tags=["System"])
async def root():
    return {
        "message": f"Welcome to {app_settings.app_name}",
        "version": app_settings.app_version,
        "docs": "/docs" if app_settings.debug else None,
    }


app.include_router(birth_chart.router, prefix="/api/v1", tags=["Birth Chart"])
app.include_router(transit_chart.router, prefix="/api/v1", tags=["Transit Chart"])


if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host=app_settings.host,
        port=app_settings.port,
        reload=app_settings.debug,
        workers=1 if app_settings.debug else app_settings.workers,
        log_level=app_settings.log_level.lower(),
    )
