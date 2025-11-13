# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2024-2025 Felipe Maya Muniz

"""
FastAPI REST API for AletheionGuard.

Supports both Managed and BYO-HF (Bring Your Own Hugging Face) modes.
"""

from fastapi import FastAPI, HTTPException, Header, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List
import time
import logging
import uuid
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import structlog

from .auditor import EpistemicAuditor, EpistemicAudit
from .api_proxy import HFClient
from .config import settings
from .security import validate_endpoint, verify_api_key
from .logging_config import configure_logging, get_logger
from .metrics import (
    setup_metrics,
    audit_requests_total,
    audit_latency_seconds,
    q1_predictions,
    q2_predictions,
    height_predictions,
    errors_total,
    active_requests,
    model_loaded
)
from .tracing_config import configure_tracing, get_tracer

# Configure structured logging
configure_logging(log_level="INFO")
logger = get_logger(__name__)

# Get tracer for manual instrumentation
tracer = get_tracer(__name__)


# Initialize rate limiter with Redis backend (SEC-003)
import os
redis_url = os.getenv("REDIS_URL")
if redis_url:
    try:
        from slowapi.util import get_remote_address
        from slowapi import Limiter
        from redis import Redis

        # Parse Redis URL
        redis_client = Redis.from_url(redis_url, decode_responses=True)
        limiter = Limiter(
            key_func=get_remote_address,
            storage_uri=redis_url
        )
        logger.info(f"Rate limiter using Redis backend: {redis_url}")
    except Exception as e:
        logger.warning(f"Failed to connect to Redis, falling back to in-memory: {e}")
        limiter = Limiter(key_func=get_remote_address)
else:
    limiter = Limiter(key_func=get_remote_address)
    logger.info("Rate limiter using in-memory backend")

# Initialize FastAPI app
app = FastAPI(
    title="AletheionGuard API",
    description="Epistemic auditor for LLM outputs with Managed and BYO-HF modes",
    version="1.1.0"
)

# Setup Prometheus metrics
setup_metrics(app)

# Configure OpenTelemetry tracing (optional)
import os
tracing_enabled = os.getenv("AG_TRACING_ENABLED", "false").lower() == "true"
if tracing_enabled:
    jaeger_host = os.getenv("AG_JAEGER_HOST", "localhost")
    jaeger_port = int(os.getenv("AG_JAEGER_PORT", "6831"))
    configure_tracing(
        app=app,
        service_name="aletheion-guard",
        jaeger_host=jaeger_host,
        jaeger_port=jaeger_port,
        enabled=True
    )

# Configure CORS (SEC-008)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(",") if settings.CORS_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Request ID middleware (for tracing)
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add unique request ID for tracing."""
    request_id = str(uuid.uuid4())
    structlog.contextvars.bind_contextvars(request_id=request_id)

    logger.info(
        "request_received",
        method=request.method,
        url=str(request.url.path),
        client=request.client.host if request.client else None
    )

    start_time = time.time()
    response = await call_next(request)
    latency = time.time() - start_time

    logger.info(
        "request_completed",
        status_code=response.status_code,
        latency_ms=round(latency * 1000, 2)
    )

    structlog.contextvars.clear_contextvars()
    return response


# Authentication middleware (SEC-002)
@app.middleware("http")
async def authenticate_request(request: Request, call_next):
    """
    Middleware to authenticate requests using API key.

    Skips authentication for health check and root endpoints.
    """
    # Skip auth for public endpoints
    if request.url.path in ["/", "/health", "/docs", "/openapi.json", "/redoc", "/metrics"]:
        return await call_next(request)

    # Check if authentication is enabled
    if not settings.AG_API_KEY_SECRET:
        # Authentication not configured, allow request
        logger.warning("auth_disabled", message="AG_API_KEY_SECRET not configured - API is open to public")
        return await call_next(request)

    # Get API key from header
    api_key = request.headers.get("X-API-Key")

    if not api_key:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "unauthorized", "message": "Missing X-API-Key header"}
        )

    # Verify API key
    if not verify_api_key(api_key):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"error": "forbidden", "message": "Invalid API key"}
        )

    return await call_next(request)

# Initialize auditor (singleton)
auditor = EpistemicAuditor()

# Initialize HF client (singleton)
hf_client = HFClient(
    default_url=settings.HF_ENDPOINT_URL,
    default_token=settings.HF_TOKEN,
    timeout=settings.HF_TIMEOUT
)


# Request/Response models
class AuditRequest(BaseModel):
    """Request model for audit endpoint."""
    text: str = Field(..., max_length=10000, description="Text to audit (max 10,000 chars)")
    context: Optional[str] = Field(None, max_length=5000, description="Optional context (max 5,000 chars)")
    model_source: Optional[str] = Field(None, max_length=500, description="Model source identifier")


class AuditResponse(BaseModel):
    """Response model for audit endpoint."""
    q1: float
    q2: float
    height: float
    ece: float
    brier: float
    verdict: str
    confidence_interval: List[float]
    explanation: str
    metadata: dict
    mode: str  # "managed" or "byo-hf"
    upstream_latency_ms: Optional[float] = None  # HF upstream latency


class BatchAuditRequest(BaseModel):
    """Request model for batch audit."""
    items: List[AuditRequest] = Field(..., max_length=100, description="Batch items (max 100)")


class BatchAuditResponse(BaseModel):
    """Response model for batch audit."""
    audits: List[AuditResponse]
    summary: dict


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    version: str
    uptime_seconds: float


# Global state for uptime tracking
startup_time = time.time()


# API Endpoints
@app.get("/", response_model=dict)
async def root():
    """Root endpoint."""
    return {
        "name": "AletheionGuard API",
        "version": "1.1.0",
        "modes": ["managed", "byo-hf"],
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint."""
    return HealthResponse(
        status="operational",
        version="1.1.0",
        uptime_seconds=time.time() - startup_time
    )


@app.post("/v1/audit", response_model=AuditResponse)
@limiter.limit("100/minute")
async def audit_response(
    http_request: Request,
    request: AuditRequest,
    x_hf_token: Optional[str] = Header(None, alias="X-HF-Token"),
    x_hf_endpoint: Optional[str] = Header(None, alias="X-HF-Endpoint")
):
    """
    Audit a single LLM response.

    Supports both Managed and BYO-HF modes:
    - **Managed mode**: Uses default HF_ENDPOINT_URL and HF_TOKEN from env
    - **BYO-HF mode**: Uses X-HF-Token and X-HF-Endpoint headers from client

    Args:
        request: Audit request with text and optional context
        x_hf_token: Optional HF token for BYO-HF mode (header: X-HF-Token)
        x_hf_endpoint: Optional HF endpoint for BYO-HF mode (header: X-HF-Endpoint)

    Returns:
        Audit results with uncertainty metrics, mode, and upstream latency

    Raises:
        HTTPException: 400 if invalid endpoint, 502 if HF upstream fails, 500 if audit fails
    """
    # Validate BYO-HF endpoint if provided
    if x_hf_endpoint and not validate_endpoint(x_hf_endpoint):
        raise HTTPException(
            status_code=400,
            detail="Invalid HF endpoint. Must use HTTPS and be from allowed hosts."
        )

    try:
        start_time = time.time()

        # Call HF upstream (Managed or BYO-HF)
        upstream_latency_ms = None
        try:
            upstream_response = await hf_client.predict(
                text=request.text,
                context=request.context,
                hf_url=x_hf_endpoint,
                hf_token=x_hf_token
            )
            upstream_latency_ms = upstream_response.elapsed.total_seconds() * 1000

        except Exception as e:
            raise HTTPException(
                status_code=502,
                detail=f"HuggingFace upstream error: {str(e)}"
            )

        # Perform audit
        audit = auditor.evaluate(
            text=request.text,
            context=request.context,
            model_source=request.model_source
        )

        # Determine mode
        mode = "byo-hf" if (x_hf_token or x_hf_endpoint) else "managed"

        # Add processing time to metadata
        audit.metadata["processing_time_ms"] = (time.time() - start_time) * 1000

        return AuditResponse(
            q1=audit.q1,
            q2=audit.q2,
            height=audit.height,
            ece=audit.ece,
            brier=audit.brier,
            verdict=audit.verdict,
            confidence_interval=list(audit.confidence_interval),
            explanation=audit.explanation,
            metadata=audit.metadata,
            mode=mode,
            upstream_latency_ms=upstream_latency_ms
        )

    except HTTPException:
        # Re-raise HTTP exceptions (400, 502)
        raise

    except Exception as e:
        # SEC-007: Sanitize error messages to prevent information disclosure
        logger.error(f"Audit failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error occurred during audit"
        )


@app.post("/v1/batch", response_model=BatchAuditResponse)
@limiter.limit("20/minute")
async def batch_audit(http_request: Request, request: BatchAuditRequest):
    """
    Audit multiple responses in batch.

    Args:
        request: Batch audit request

    Returns:
        Batch audit results with summary

    Raises:
        HTTPException: If batch audit fails
    """
    try:
        start_time = time.time()

        # Extract texts and contexts
        texts = [item.text for item in request.items]
        contexts = [item.context for item in request.items]

        # Perform batch audit
        audits = auditor.batch_evaluate(texts, contexts)

        # Convert to response format
        audit_responses = []
        for audit in audits:
            audit_responses.append(AuditResponse(
                q1=audit.q1,
                q2=audit.q2,
                height=audit.height,
                ece=audit.ece,
                brier=audit.brier,
                verdict=audit.verdict,
                confidence_interval=list(audit.confidence_interval),
                explanation=audit.explanation,
                metadata=audit.metadata
            ))

        # Compute summary statistics
        accept_count = sum(1 for a in audits if a.verdict == "ACCEPT")
        maybe_count = sum(1 for a in audits if a.verdict == "MAYBE")
        refused_count = sum(1 for a in audits if a.verdict == "REFUSED")

        summary = {
            "total": len(audits),
            "accept": accept_count,
            "maybe": maybe_count,
            "refused": refused_count,
            "avg_q1": sum(a.q1 for a in audits) / len(audits),
            "avg_q2": sum(a.q2 for a in audits) / len(audits),
            "avg_height": sum(a.height for a in audits) / len(audits),
            "processing_time_ms": (time.time() - start_time) * 1000
        }

        return BatchAuditResponse(
            audits=audit_responses,
            summary=summary
        )

    except Exception as e:
        # SEC-007: Sanitize error messages to prevent information disclosure
        logger.error(f"Batch audit failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error occurred during batch audit"
        )


class CompareRequest(BaseModel):
    """Request model for model comparison endpoint."""
    prompt: str = Field(..., max_length=5000, description="Original prompt")
    responses: List[dict] = Field(..., min_items=2, max_items=10, description="Model responses [{model: str, text: str}]")


class CompareResponse(BaseModel):
    """Response model for model comparison."""
    prompt: str
    comparisons: List[dict]
    ranking: List[dict]
    best_model: str
    summary: dict


@app.post("/v1/compare", response_model=CompareResponse)
@limiter.limit("50/minute")
async def compare_models(http_request: Request, request: CompareRequest):
    """
    Compare calibration quality across multiple model outputs.

    Ranks models by epistemic uncertainty (Q2) and calibration metrics.
    Lower Q2 = more confident/reliable prediction.

    Args:
        request: Comparison request with prompt and multiple model responses

    Returns:
        Comparison results with rankings and detailed metrics

    Raises:
        HTTPException: 400 if invalid input, 500 if comparison fails
    """
    try:
        start_time = time.time()

        comparisons = []
        for response_item in request.responses:
            model_name = response_item.get("model", "unknown")
            text = response_item.get("text", "")

            if not text:
                continue

            # Audit each model's response
            audit = auditor.evaluate(
                text=text,
                context=request.prompt,
                model_source=model_name
            )

            comparisons.append({
                "model": model_name,
                "q1": float(audit.q1),
                "q2": float(audit.q2),
                "height": float(audit.height),
                "ece": float(audit.ece),
                "brier": float(audit.brier),
                "verdict": audit.verdict,
                "explanation": audit.explanation
            })

        # Rank by composite score (Q2 primary, Q1 secondary, ECE tertiary)
        # Lower Q2 = better (more confident), lower ECE = better calibration
        ranking = sorted(
            comparisons,
            key=lambda x: (x["q2"], x["q1"], x["ece"])
        )

        # Add rank field
        for i, item in enumerate(ranking):
            item["rank"] = i + 1

        best_model = ranking[0]["model"] if ranking else "none"

        # Compute summary
        summary = {
            "total_models": len(comparisons),
            "best_model": best_model,
            "best_q2": ranking[0]["q2"] if ranking else None,
            "avg_q2": sum(c["q2"] for c in comparisons) / len(comparisons) if comparisons else 0,
            "q2_range": (
                min(c["q2"] for c in comparisons),
                max(c["q2"] for c in comparisons)
            ) if comparisons else (0, 0),
            "processing_time_ms": (time.time() - start_time) * 1000
        }

        logger.info(
            "model_comparison_completed",
            prompt_length=len(request.prompt),
            num_models=len(comparisons),
            best_model=best_model
        )

        return CompareResponse(
            prompt=request.prompt,
            comparisons=comparisons,
            ranking=ranking,
            best_model=best_model,
            summary=summary
        )

    except Exception as e:
        logger.error(f"Model comparison failed: {str(e)}", exc_info=True)
        errors_total.labels(error_type="comparison_error").inc()
        raise HTTPException(
            status_code=500,
            detail="Internal server error occurred during model comparison"
        )


class CalibrateRequest(BaseModel):
    """Request model for calibration endpoint."""
    text: str = Field(..., max_length=10000, description="Text to audit")
    context: Optional[str] = Field(None, max_length=5000, description="Optional context")
    ground_truth: Optional[float] = Field(None, ge=0.0, le=1.0, description="Ground truth uncertainty [0-1]")
    feedback: Optional[str] = Field(None, description="Human feedback (correct/incorrect)")


class CalibrateResponse(BaseModel):
    """Response model for calibration endpoint."""
    q1: float
    q2: float
    height: float
    verdict: str
    calibration_adjustment: Optional[float] = None
    feedback_recorded: bool = False


@app.post("/v1/calibrate", response_model=CalibrateResponse)
@limiter.limit("100/minute")
async def calibrate(http_request: Request, request: CalibrateRequest):
    """
    Perform audit with optional online calibration feedback.

    Supports optional ground truth or human feedback for online learning.
    Future versions will use this feedback to improve calibration.

    Args:
        request: Calibration request with text, optional ground truth, and feedback

    Returns:
        Audit results with calibration info

    Raises:
        HTTPException: 500 if calibration fails
    """
    try:
        start_time = time.time()

        # Perform standard audit
        audit = auditor.evaluate(
            text=request.text,
            context=request.context
        )

        # Calculate calibration adjustment if ground truth provided
        calibration_adjustment = None
        if request.ground_truth is not None:
            # Compare predicted Q2 with ground truth
            calibration_adjustment = float(audit.q2 - request.ground_truth)

            logger.info(
                "calibration_feedback",
                predicted_q2=float(audit.q2),
                ground_truth=request.ground_truth,
                adjustment=calibration_adjustment
            )

        # Record feedback if provided
        feedback_recorded = False
        if request.feedback:
            # TODO: Store feedback for future online learning
            logger.info(
                "human_feedback_recorded",
                text_length=len(request.text),
                feedback=request.feedback,
                predicted_verdict=audit.verdict
            )
            feedback_recorded = True

        return CalibrateResponse(
            q1=float(audit.q1),
            q2=float(audit.q2),
            height=float(audit.height),
            verdict=audit.verdict,
            calibration_adjustment=calibration_adjustment,
            feedback_recorded=feedback_recorded
        )

    except Exception as e:
        logger.error(f"Calibration failed: {str(e)}", exc_info=True)
        errors_total.labels(error_type="calibration_error").inc()
        raise HTTPException(
            status_code=500,
            detail="Internal server error occurred during calibration"
        )


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors."""
    return {
        "error": "not_found",
        "message": "Endpoint not found",
        "path": str(request.url)
    }


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors."""
    return {
        "error": "internal_error",
        "message": "An unexpected error occurred",
        "detail": str(exc)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
