import sys
import structlog
from typing import Any, Dict
from prometheus_client import Counter, Histogram, Gauge
import time

REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

ACTIVE_CONNECTIONS = Gauge(
    'active_connections_total',
    'Total active connections'
)

DOCUMENT_PROCESSING_DURATION = Histogram(
    'document_processing_duration_seconds',
    'Document processing duration in seconds',
    ['file_type']
)

CHAT_REQUESTS = Counter(
    'chat_requests_total',
    'Total chat requests',
    ['user_id']
)

EMBEDDING_GENERATION_DURATION = Histogram(
    'embedding_generation_duration_seconds',
    'Embedding generation duration in seconds'
)


def setup_logging() -> None:
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


class MetricsMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start_time = time.time()
        method = scope["method"]
        path = scope["path"]
        
        ACTIVE_CONNECTIONS.inc()
        
        try:
            await self.app(scope, receive, send)
        finally:
            duration = time.time() - start_time
            ACTIVE_CONNECTIONS.dec()
            REQUEST_DURATION.labels(method=method, endpoint=path).observe(duration)


def log_request_response(
    method: str,
    url: str,
    status_code: int,
    duration: float,
    user_id: str = None,
    **kwargs: Any
) -> None:
    logger = structlog.get_logger()
    
    REQUEST_COUNT.labels(
        method=method,
        endpoint=url,
        status=status_code
    ).inc()
    
    log_data = {
        "method": method,
        "url": url,
        "status_code": status_code,
        "duration": duration,
        **kwargs
    }
    
    if user_id:
        log_data["user_id"] = user_id
    
    if status_code >= 400:
        logger.warning("HTTP request failed", **log_data)
    else:
        logger.info("HTTP request completed", **log_data)


def log_document_processing(
    filename: str,
    file_type: str,
    duration: float,
    status: str,
    user_id: int,
    error: str = None
) -> None:
    logger = structlog.get_logger()
    
    DOCUMENT_PROCESSING_DURATION.labels(file_type=file_type).observe(duration)
    
    log_data = {
        "filename": filename,
        "file_type": file_type,
        "duration": duration,
        "status": status,
        "user_id": user_id
    }
    
    if error:
        log_data["error"] = error
        logger.error("Document processing failed", **log_data)
    else:
        logger.info("Document processing completed", **log_data)


def log_chat_interaction(
    user_id: int,
    conversation_id: str,
    message_length: int,
    response_length: int,
    duration: float,
    sources_count: int
) -> None:
    logger = structlog.get_logger()
    
    CHAT_REQUESTS.labels(user_id=str(user_id)).inc()
    
    logger.info(
        "Chat interaction completed",
        user_id=user_id,
        conversation_id=conversation_id,
        message_length=message_length,
        response_length=response_length,
        duration=duration,
        sources_count=sources_count
    )