"""
FastAPI server for FLAMEHAVEN FileSearch v1.1.0

Production-ready API with:
- Rate limiting
- Request ID tracing
- Security headers
- Standardized error handling
- Input validation
- Enhanced monitoring
- LRU caching with TTL
- Prometheus metrics
- Structured JSON logging
"""

import logging
import os
import shutil
import tempfile
import time
import psutil
from typing import List, Optional
from datetime import datetime

from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile, Request, Depends
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .config import Config
from .core import FlamehavenFileSearch
from .exceptions import (
    FileSearchException,
    InvalidFilenameError,
    FileSizeExceededError,
    EmptySearchQueryError,
    ServiceUnavailableError,
    exception_to_response,
)
from .validators import (
    FilenameValidator,
    FileSizeValidator,
    SearchQueryValidator,
    validate_upload_file,
    validate_search_request,
)
from .middlewares import (
    RequestIDMiddleware,
    SecurityHeadersMiddleware,
    RequestLoggingMiddleware,
    get_request_id,
)
from .cache import get_search_cache, get_all_cache_stats
from .metrics import (
    MetricsCollector,
    get_metrics_text,
    get_metrics_content_type,
)
from .logging_config import setup_json_logging, setup_development_logging

# Configure structured JSON logging for production
# Use ENVIRONMENT=development for human-readable logs
if os.getenv("ENVIRONMENT", "production") == "development":
    setup_development_logging(level=logging.INFO)
else:
    setup_json_logging(level=logging.INFO)

logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Initialize app
app = FastAPI(
    title="FLAMEHAVEN FileSearch API",
    description="Open source semantic document search powered by Google Gemini - v1.1.0",
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Custom rate limit handler that records metrics
async def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Custom rate limit handler with metrics"""
    # Record rate limit exceeded metric
    endpoint = request.url.path
    MetricsCollector.record_rate_limit_exceeded(endpoint)

    # Call default handler
    return await _rate_limit_exceeded_handler(request, exc)

# Add rate limit handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, custom_rate_limit_handler)

# Add middlewares (order matters!)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestIDMiddleware)

# Global instances
searcher: Optional[FlamehavenFileSearch] = None
search_cache = None  # Initialized in startup
startup_time = time.time()


# Pydantic models
class SearchRequest(BaseModel):
    """Search request model"""

    query: str = Field(..., description="Search query", min_length=1, max_length=1000)
    store_name: str = Field(default="default", description="Store name to search in")
    model: Optional[str] = Field(None, description="Model to use for generation")
    max_tokens: Optional[int] = Field(None, description="Maximum output tokens", gt=0, le=8192)
    temperature: Optional[float] = Field(None, description="Model temperature", ge=0.0, le=2.0)


class SearchResponse(BaseModel):
    """Search response model"""

    status: str
    answer: Optional[str] = None
    sources: Optional[List[dict]] = None
    model: Optional[str] = None
    query: Optional[str] = None
    store: Optional[str] = None
    message: Optional[str] = None
    request_id: Optional[str] = None


class UploadResponse(BaseModel):
    """Upload response model"""

    status: str
    store: Optional[str] = None
    file: Optional[str] = None
    filename: Optional[str] = None
    size_mb: Optional[float] = None
    message: Optional[str] = None
    request_id: Optional[str] = None


class MultipleUploadResponse(BaseModel):
    """Multiple upload response"""

    status: str
    files: List[dict]
    total: int
    successful: int
    failed: int
    request_id: Optional[str] = None


class StoreRequest(BaseModel):
    """Store creation request"""

    name: str = Field(default="default", description="Store name", min_length=1, max_length=100)


class HealthResponse(BaseModel):
    """Enhanced health check response"""

    status: str
    version: str
    uptime_seconds: float
    uptime_formatted: str
    searcher_initialized: bool
    timestamp: str
    system: dict


class MetricsResponse(BaseModel):
    """Enhanced metrics response"""

    stores_count: int
    stores: List[str]
    config: dict
    system: dict
    uptime_seconds: float


class ErrorResponse(BaseModel):
    """Standardized error response"""

    error: str
    message: str
    status_code: int
    details: Optional[dict] = None
    request_id: Optional[str] = None
    timestamp: str


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize the searcher and caching on startup"""
    global searcher, search_cache, startup_time
    startup_time = time.time()

    try:
        config = Config.from_env()
        searcher = FlamehavenFileSearch(config=config)

        # Initialize search cache (1000 items, 1 hour TTL)
        search_cache = get_search_cache(maxsize=1000, ttl=3600)

        # Update initial system metrics
        MetricsCollector.update_system_metrics()

        logger.info("FLAMEHAVEN FileSearch v1.1.0 initialized successfully")
        logger.info("Caching enabled: 1000 items, 3600s TTL")
        logger.info("Prometheus metrics enabled at /prometheus")
    except Exception as e:
        logger.error(f"Failed to initialize FLAMEHAVEN FileSearch: {e}")
        raise


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down FLAMEHAVEN FileSearch API")


# Helper functions
def format_uptime(seconds: float) -> str:
    """Format uptime in human-readable format"""
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if days > 0:
        return f"{days}d {hours}h {minutes}m {secs}s"
    elif hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"


def get_system_info() -> dict:
    """Get system information"""
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        return {
            "cpu_percent": round(cpu_percent, 2),
            "memory_percent": round(memory.percent, 2),
            "memory_available_mb": round(memory.available / (1024 * 1024), 2),
            "disk_percent": round(disk.percent, 2),
            "disk_free_gb": round(disk.free / (1024 * 1024 * 1024), 2),
        }
    except Exception as e:
        logger.warning(f"Failed to get system info: {e}")
        return {"error": "unavailable"}


# Health check endpoint
@app.get("/health", response_model=HealthResponse, tags=["Health"])
@limiter.limit("100/minute")
async def health_check(request: Request):
    """
    Enhanced health check endpoint with system information

    Returns:
        Detailed service health status
    """
    uptime = time.time() - startup_time

    return {
        "status": "healthy" if searcher else "unhealthy",
        "version": "1.1.0",
        "uptime_seconds": round(uptime, 2),
        "uptime_formatted": format_uptime(uptime),
        "searcher_initialized": searcher is not None,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "system": get_system_info(),
    }


# Upload endpoints
@app.post("/api/upload/single", response_model=UploadResponse, tags=["Files"])
@limiter.limit("10/minute")
async def upload_single_file(
    request: Request,
    file: UploadFile = File(..., description="File to upload"),
    store: str = Form(default="default", description="Store name"),
):
    """
    Upload a single file to a store (Rate limited: 10/min)

    Args:
        file: File to upload (max 50MB)
        store: Store name (creates if doesn't exist)

    Returns:
        Upload result with status and file info

    Raises:
        InvalidFilenameError: If filename is invalid
        FileSizeExceededError: If file size exceeds limit
        ServiceUnavailableError: If service not initialized
    """
    request_id = get_request_id(request)
    start_time = time.time()

    if not searcher:
        raise ServiceUnavailableError("FileSearch", "Service not initialized")

    temp_dir = tempfile.mkdtemp()
    try:
        # Get file size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning

        # Validate file upload
        config = Config.from_env()
        validated_filename, _ = validate_upload_file(
            file.filename, file_size, file.content_type or "application/octet-stream", config.max_file_size_mb
        )

        file_path = os.path.join(temp_dir, validated_filename)

        # Save uploaded file
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        logger.info(f"[{request_id}] Uploaded file to temp: {file_path}")

        # Upload to searcher
        result = searcher.upload_file(file_path, store_name=store)
        result["request_id"] = request_id
        result["filename"] = validated_filename

        # Record metrics
        duration = time.time() - start_time
        MetricsCollector.record_file_upload(
            store=store,
            size_bytes=file_size,
            duration=duration,
            success=True
        )

        return result

    except FileSearchException as e:
        # Record failed upload metric
        duration = time.time() - start_time
        MetricsCollector.record_file_upload(store=store, size_bytes=0, duration=duration, success=False)
        MetricsCollector.record_error(error_type=e.__class__.__name__, endpoint="/api/upload/single")
        raise
    except Exception as e:
        # Record failed upload metric
        duration = time.time() - start_time
        MetricsCollector.record_file_upload(store=store, size_bytes=0, duration=duration, success=False)
        MetricsCollector.record_error(error_type="UnexpectedError", endpoint="/api/upload/single")
        logger.error(f"[{request_id}] Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup temp file
        try:
            shutil.rmtree(temp_dir)
        except Exception as e:
            logger.warning(f"[{request_id}] Failed to cleanup temp dir: {e}")


@app.post("/api/upload/multiple", response_model=MultipleUploadResponse, tags=["Files"])
@limiter.limit("5/minute")
async def upload_multiple_files(
    request: Request,
    files: List[UploadFile] = File(..., description="Files to upload"),
    store: str = Form(default="default", description="Store name"),
):
    """
    Upload multiple files to a store (Rate limited: 5/min)

    Args:
        files: List of files to upload
        store: Store name (creates if doesn't exist)

    Returns:
        Upload results for all files

    Raises:
        ServiceUnavailableError: If service not initialized
    """
    request_id = get_request_id(request)

    if not searcher:
        raise ServiceUnavailableError("FileSearch", "Service not initialized")

    temp_dir = tempfile.mkdtemp()
    file_paths = []
    results = []
    successful = 0
    failed = 0

    try:
        config = Config.from_env()

        # Save all files
        for file in files:
            try:
                # Get file size
                file.file.seek(0, 2)
                file_size = file.file.tell()
                file.file.seek(0)

                # Validate
                validated_filename, _ = validate_upload_file(
                    file.filename, file_size, file.content_type or "application/octet-stream", config.max_file_size_mb
                )

                file_path = os.path.join(temp_dir, validated_filename)
                with open(file_path, "wb") as f:
                    shutil.copyfileobj(file.file, f)

                file_paths.append(file_path)
                results.append({"filename": validated_filename, "status": "saved", "size_mb": round(file_size / (1024 * 1024), 2)})

            except FileSearchException as e:
                failed += 1
                results.append({"filename": file.filename, "status": "failed", "error": str(e)})
                logger.warning(f"[{request_id}] File validation failed for {file.filename}: {e}")

        logger.info(f"[{request_id}] Saved {len(file_paths)} files to temp")

        # Upload all valid files
        if file_paths:
            upload_result = searcher.upload_files(file_paths, store_name=store)
            successful = len(file_paths)
        else:
            upload_result = {"status": "no_valid_files"}

        return {
            "status": "success" if successful > 0 else "failed",
            "files": results,
            "total": len(files),
            "successful": successful,
            "failed": failed,
            "request_id": request_id,
        }

    except Exception as e:
        logger.error(f"[{request_id}] Multiple upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        try:
            shutil.rmtree(temp_dir)
        except Exception as e:
            logger.warning(f"[{request_id}] Failed to cleanup temp dir: {e}")


# Search endpoints
@app.post("/api/search", response_model=SearchResponse, tags=["Search"])
@limiter.limit("100/minute")
async def search(request: Request, search_request: SearchRequest):
    """
    Search files and get AI-generated answers (Rate limited: 100/min)

    Uses LRU caching with 1-hour TTL for improved performance.

    Args:
        search_request: Search request with query and parameters

    Returns:
        Answer with citations from uploaded files

    Raises:
        EmptySearchQueryError: If query is empty
        InvalidSearchQueryError: If query is invalid
        ServiceUnavailableError: If service not initialized
    """
    request_id = get_request_id(request)
    start_time = time.time()

    if not searcher:
        raise ServiceUnavailableError("FileSearch", "Service not initialized")

    try:
        # Validate search request
        validated_query, _ = validate_search_request(search_request.query)

        # Check cache first
        cache_key_params = {
            "model": search_request.model,
            "max_tokens": search_request.max_tokens,
            "temperature": search_request.temperature,
        }
        cached_result = search_cache.get(
            validated_query,
            search_request.store_name,
            **cache_key_params
        )

        if cached_result:
            # Cache hit - return cached result
            cached_result["request_id"] = request_id
            duration = time.time() - start_time

            # Record metrics
            MetricsCollector.record_cache_hit("search")
            results_count = len(cached_result.get("sources", []))
            MetricsCollector.record_search(
                store=search_request.store_name,
                duration=duration,
                results_count=results_count,
                success=True
            )

            logger.info(f"[{request_id}] Cache HIT for query: {validated_query[:50]}...")
            return cached_result

        # Cache miss - perform search
        MetricsCollector.record_cache_miss("search")
        logger.info(f"[{request_id}] Cache MISS for query: {validated_query[:50]}...")

        result = searcher.search(
            query=validated_query,
            store_name=search_request.store_name,
            model=search_request.model,
            max_tokens=search_request.max_tokens,
            temperature=search_request.temperature,
        )

        result["request_id"] = request_id

        if result["status"] == "error":
            # Record failed search
            duration = time.time() - start_time
            MetricsCollector.record_search(
                store=search_request.store_name,
                duration=duration,
                results_count=0,
                success=False
            )
            MetricsCollector.record_error(error_type="SearchError", endpoint="/api/search")
            raise HTTPException(status_code=400, detail=result["message"])

        # Cache the successful result
        search_cache.set(
            validated_query,
            search_request.store_name,
            result,
            **cache_key_params
        )

        # Record metrics
        duration = time.time() - start_time
        results_count = len(result.get("sources", []))
        MetricsCollector.record_search(
            store=search_request.store_name,
            duration=duration,
            results_count=results_count,
            success=True
        )

        # Update cache size metrics
        cache_stats = search_cache.get_stats()
        MetricsCollector.update_cache_size("search", cache_stats["current_size"])

        return result

    except FileSearchException as e:
        duration = time.time() - start_time
        MetricsCollector.record_search(
            store=search_request.store_name,
            duration=duration,
            results_count=0,
            success=False
        )
        MetricsCollector.record_error(error_type=e.__class__.__name__, endpoint="/api/search")
        raise
    except HTTPException:
        raise
    except Exception as e:
        duration = time.time() - start_time
        MetricsCollector.record_search(
            store=search_request.store_name,
            duration=duration,
            results_count=0,
            success=False
        )
        MetricsCollector.record_error(error_type="UnexpectedError", endpoint="/api/search")
        logger.error(f"[{request_id}] Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/search", response_model=SearchResponse, tags=["Search"])
@limiter.limit("100/minute")
async def search_get(
    request: Request,
    q: str = Query(..., description="Search query", min_length=1),
    store: str = Query(default="default", description="Store name"),
    model: Optional[str] = Query(None, description="Model to use"),
):
    """
    Search files - GET method for simple queries (Rate limited: 100/min)

    Args:
        q: Search query
        store: Store name
        model: Optional model override

    Returns:
        Answer with citations
    """
    search_request = SearchRequest(query=q, store_name=store, model=model)
    return await search(request, search_request)


# Store management endpoints
@app.post("/api/stores", tags=["Stores"])
@limiter.limit("20/minute")
async def create_store(request: Request, store_request: StoreRequest):
    """
    Create a new file search store (Rate limited: 20/min)

    Args:
        store_request: Store creation request

    Returns:
        Store resource name
    """
    request_id = get_request_id(request)

    if not searcher:
        raise ServiceUnavailableError("FileSearch", "Service not initialized")

    try:
        store_name = searcher.create_store(name=store_request.name)
        return {
            "status": "success",
            "store_name": store_request.name,
            "resource": store_name,
            "request_id": request_id,
        }
    except Exception as e:
        logger.error(f"[{request_id}] Store creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stores", tags=["Stores"])
@limiter.limit("100/minute")
async def list_stores(request: Request):
    """
    List all created stores (Rate limited: 100/min)

    Returns:
        Dictionary of store names to resource names
    """
    request_id = get_request_id(request)

    if not searcher:
        raise ServiceUnavailableError("FileSearch", "Service not initialized")

    stores = searcher.list_stores()
    return {
        "status": "success",
        "count": len(stores),
        "stores": stores,
        "request_id": request_id,
    }


@app.delete("/api/stores/{store_name}", tags=["Stores"])
@limiter.limit("20/minute")
async def delete_store(request: Request, store_name: str):
    """
    Delete a store (Rate limited: 20/min)

    Args:
        store_name: Name of store to delete

    Returns:
        Deletion result
    """
    request_id = get_request_id(request)

    if not searcher:
        raise ServiceUnavailableError("FileSearch", "Service not initialized")

    result = searcher.delete_store(store_name)
    result["request_id"] = request_id

    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result["message"])

    return result


# Metrics endpoints
@app.get("/prometheus", tags=["Monitoring"])
@limiter.limit("100/minute")
async def prometheus_metrics(request: Request):
    """
    Prometheus metrics endpoint (Rate limited: 100/min)

    Returns:
        Metrics in Prometheus text format

    Exports:
        - HTTP request metrics (counter, histogram)
        - File upload metrics (counter, size, duration)
        - Search metrics (counter, duration, results count)
        - Cache metrics (hits, misses, size)
        - Rate limit metrics
        - Error metrics
        - System metrics (CPU, memory, disk)
    """
    # Update stores count
    if searcher:
        stores = searcher.list_stores()
        MetricsCollector.update_stores_count(len(stores))

    # Get metrics in Prometheus format
    metrics_text = get_metrics_text()
    return Response(content=metrics_text, media_type=get_metrics_content_type())


@app.get("/metrics", response_model=MetricsResponse, tags=["Monitoring"])
@limiter.limit("100/minute")
async def get_metrics(request: Request):
    """
    Get enhanced service metrics with cache statistics (Rate limited: 100/min)

    Returns:
        Current metrics, configuration, system info, and cache statistics
    """
    if not searcher:
        raise ServiceUnavailableError("FileSearch", "Service not initialized")

    metrics = searcher.get_metrics()
    metrics["system"] = get_system_info()
    metrics["uptime_seconds"] = round(time.time() - startup_time, 2)

    # Add cache statistics
    cache_stats = get_all_cache_stats()
    if cache_stats:
        metrics["cache"] = cache_stats

    return metrics


# Root endpoint
@app.get("/", tags=["Info"])
async def root():
    """
    API information endpoint

    Returns:
        API information and available endpoints
    """
    return {
        "name": "FLAMEHAVEN FileSearch API",
        "version": "1.1.0",
        "description": "Open source semantic document search powered by Google Gemini",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "upload_single": "POST /api/upload/single (10/min)",
            "upload_multiple": "POST /api/upload/multiple (5/min)",
            "search": "POST /api/search or GET /api/search?q=... (100/min)",
            "stores": "GET /api/stores (100/min)",
            "metrics": "GET /metrics (100/min)",
            "prometheus": "GET /prometheus (100/min)",
        },
        "features": {
            "caching": "LRU cache with 1-hour TTL (1000 items)",
            "monitoring": "Prometheus metrics at /prometheus",
            "logging": "Structured JSON logging",
            "security": "Rate limiting, request tracing, OWASP headers",
        },
        "rate_limits": {
            "upload_single": "10 requests per minute",
            "upload_multiple": "5 requests per minute",
            "search": "100 requests per minute",
            "general": "100 requests per minute",
        },
    }


# Enhanced error handlers
@app.exception_handler(FileSearchException)
async def filesearch_exception_handler(request: Request, exc: FileSearchException):
    """Handle FileSearch custom exceptions"""
    request_id = get_request_id(request)
    error_dict = exc.to_dict()
    error_dict["request_id"] = request_id
    error_dict["timestamp"] = datetime.utcnow().isoformat() + "Z"

    logger.warning(f"[{request_id}] FileSearchException: {exc.message}")

    return JSONResponse(status_code=exc.status_code, content=error_dict)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    request_id = get_request_id(request)

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP_ERROR",
            "message": exc.detail,
            "status_code": exc.status_code,
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    request_id = get_request_id(request)
    logger.error(f"[{request_id}] Unhandled exception: {exc}", exc_info=True)

    # Convert to standardized response
    error_response = exception_to_response(exc)
    error_response["request_id"] = request_id
    error_response["timestamp"] = datetime.utcnow().isoformat() + "Z"

    return JSONResponse(
        status_code=error_response.get("status_code", 500), content=error_response
    )


# CLI entry point
def main():
    """Main entry point for CLI"""
    import sys
    import uvicorn

    # Parse simple arguments
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    workers = int(os.getenv("WORKERS", "1"))
    reload = os.getenv("RELOAD", "false").lower() == "true"

    # Check for --help
    if "--help" in sys.argv or "-h" in sys.argv:
        print("FLAMEHAVEN FileSearch API Server v1.1.0")
        print("\nUsage: flamehaven-api [options]")
        print("\nOptions via environment variables:")
        print("  HOST=0.0.0.0        - Server host")
        print("  PORT=8000           - Server port")
        print("  WORKERS=4           - Number of workers (production)")
        print("  RELOAD=true         - Enable auto-reload (development)")
        print("  GEMINI_API_KEY=...  - Google Gemini API key (required)")
        print("\nExample:")
        print("  export GEMINI_API_KEY='your-key'")
        print("  flamehaven-api")
        print("\nDocs: http://localhost:8000/docs")
        print("Prometheus: http://localhost:8000/prometheus")
        print("\nNew in v1.1.0:")
        print("  [*] Security:")
        print("      - Path traversal vulnerability fixed")
        print("      - Rate limiting (slowapi): 10/min uploads, 100/min searches")
        print("      - Request ID tracing with X-Request-ID header")
        print("      - OWASP security headers (HSTS, CSP, X-Frame-Options)")
        print("      - Comprehensive input validation")
        print("  [*] Performance:")
        print("      - LRU caching with TTL (1000 items, 1-hour TTL)")
        print("      - Structured JSON logging (set ENVIRONMENT=development for readable logs)")
        print("  [*] Monitoring:")
        print("      - Prometheus metrics at /prometheus")
        print("      - System metrics (CPU, memory, disk)")
        print("      - Cache hit/miss tracking")
        return

    # Validate API key
    if not os.getenv("GEMINI_API_KEY") and not os.getenv("GOOGLE_API_KEY"):
        print("Error: GEMINI_API_KEY or GOOGLE_API_KEY must be set")
        print("Example: export GEMINI_API_KEY='your-api-key'")
        sys.exit(1)

    print(f"Starting FLAMEHAVEN FileSearch API v1.1.0 on {host}:{port}")
    print(f"Workers: {workers}, Reload: {reload}")
    print(f"\nEndpoints:")
    print(f"  - Docs:       http://{host}:{port}/docs")
    print(f"  - Health:     http://{host}:{port}/health")
    print(f"  - Metrics:    http://{host}:{port}/metrics")
    print(f"  - Prometheus: http://{host}:{port}/prometheus")
    print("\nFeatures:")
    print("  - Rate limiting: 10/min uploads, 100/min searches")
    print("  - Request tracing with X-Request-ID header")
    print("  - Security headers (OWASP compliant)")
    print("  - LRU caching with 1-hour TTL (1000 items)")
    print("  - Prometheus metrics export")
    print("  - Structured JSON logging")

    uvicorn.run(
        "flamehaven_filesearch.api:app",
        host=host,
        port=port,
        workers=workers if not reload else 1,
        reload=reload,
    )


# For development/testing
if __name__ == "__main__":
    main()
