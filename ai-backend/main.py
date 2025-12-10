from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import uvicorn
from contextlib import asynccontextmanager
import logging
from loguru import logger as loguru_logger
import sys

from app.config import get_settings
from app.api.v1.endpoints import birth_chart
from app.api.models import ErrorResponse, HealthCheckResponse
from app.rag import get_astrology_rag_service_manager

settings = get_settings()

# Configure logging
def setup_logging():
    # Remove default handler
    loguru_logger.remove()

    # Add console handler with color
    loguru_logger.add(
        sys.stdout,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=settings.log_level
    )

    # Add file handler
    loguru_logger.add(
        settings.log_file,
        rotation=settings.log_rotation,
        retention=settings.log_retention,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
        level=settings.log_level
    )

    # Bridge standard logging to loguru
    class InterceptHandler(logging.Handler):
        def emit(self, record):
            try:
                level = loguru_logger.level(record.levelname).name
            except ValueError:
                level = record.levelno
            loguru_logger.opt(depth=6, exception=record.exc_info).log(level, record.getMessage())

    logging.basicConfig(handlers=[InterceptHandler()], level=0)

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    setup_logging()
    loguru_logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    loguru_logger.info(f"Environment: {settings.environment}")
    loguru_logger.info(f"Debug mode: {settings.debug}")

    # Initialize RAG services
    rag_manager = get_astrology_rag_service_manager()
    rag_initialized = await rag_manager.initialize()
    if rag_initialized:
        loguru_logger.info("RAG services initialized successfully")
    else:
        loguru_logger.warning(
            "RAG services failed to initialize. "
            "AI interpretation will not be available."
        )

    yield

    # Shutdown
    loguru_logger.info("Shutting down application")

    # Cleanup RAG services
    await rag_manager.shutdown()

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered astrology and fortune telling platform",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            error="Validation Error",
            error_code="VALIDATION_ERROR",
            details={"errors": errors}
        ).model_dump()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    loguru_logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Internal Server Error",
            error_code="INTERNAL_ERROR",
            details={"message": str(exc) if settings.debug else "An error occurred"}
        ).model_dump()
    )


# Health check endpoint
@app.get("/health", response_model=HealthCheckResponse, tags=["System"])
async def health_check():
    rag_manager = get_astrology_rag_service_manager()
    return HealthCheckResponse(
        status="ok",
        version=settings.app_version,
        environment=settings.environment,
        rag_status="connected" if rag_manager.is_connected else "disconnected"
    )


# Root endpoint
@app.get("/", tags=["System"])
async def root():
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs" if settings.debug else None
    }


# Include routers
app.include_router(
    birth_chart.router,
    prefix="/api/v1",
    tags=["Birth Chart"]
)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        workers=1 if settings.debug else settings.workers,
        log_level=settings.log_level.lower()
    )
