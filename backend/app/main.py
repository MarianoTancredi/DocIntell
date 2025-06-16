from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
import structlog
import time

from app.core.config import settings
from app.api.api_v1.api import api_router
from app.core.database import engine, Base
from app.core.logging import setup_logging, MetricsMiddleware, log_request_response

setup_logging()
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up DocIntell API", version=settings.VERSION)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    logger.info("Shutting down DocIntell API")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(MetricsMiddleware)

@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    
    log_request_response(
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        duration=process_time,
        client_ip=request.client.host if request.client else None
    )
    
    response.headers["X-Process-Time"] = str(process_time)
    return response

app.include_router(api_router, prefix=settings.API_V1_STR)

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.VERSION}