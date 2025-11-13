# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2024-2025 Felipe Maya Muniz

"""
OpenTelemetry tracing configuration for AletheionGuard.

Provides distributed tracing with Jaeger backend.
"""

from typing import Optional
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from fastapi import FastAPI
import logging

logger = logging.getLogger(__name__)


def configure_tracing(
    app: FastAPI,
    service_name: str = "aletheion-guard",
    jaeger_host: str = "localhost",
    jaeger_port: int = 6831,
    enable_otlp: bool = False,
    otlp_endpoint: Optional[str] = None,
    enabled: bool = True
) -> Optional[TracerProvider]:
    """
    Configure OpenTelemetry distributed tracing.

    Args:
        app: FastAPI application instance
        service_name: Service name for tracing
        jaeger_host: Jaeger agent host
        jaeger_port: Jaeger agent port
        enable_otlp: Enable OTLP exporter
        otlp_endpoint: OTLP collector endpoint (e.g., "http://localhost:4317")
        enabled: Enable/disable tracing

    Returns:
        TracerProvider instance if enabled, None otherwise
    """
    if not enabled:
        logger.info("OpenTelemetry tracing is disabled")
        return None

    try:
        # Create resource with service name
        resource = Resource(attributes={
            SERVICE_NAME: service_name
        })

        # Create tracer provider
        provider = TracerProvider(resource=resource)

        # Add Jaeger exporter
        jaeger_exporter = JaegerExporter(
            agent_host_name=jaeger_host,
            agent_port=jaeger_port,
        )
        provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
        logger.info(f"Jaeger exporter configured: {jaeger_host}:{jaeger_port}")

        # Add OTLP exporter if enabled
        if enable_otlp and otlp_endpoint:
            otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
            provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
            logger.info(f"OTLP exporter configured: {otlp_endpoint}")

        # Set as global tracer provider
        trace.set_tracer_provider(provider)

        # Instrument FastAPI
        FastAPIInstrumentor.instrument_app(app)
        logger.info("FastAPI instrumentation enabled")

        logger.info(f"OpenTelemetry tracing configured for service: {service_name}")
        return provider

    except Exception as e:
        logger.error(f"Failed to configure OpenTelemetry tracing: {e}")
        return None


def get_tracer(name: str = __name__) -> trace.Tracer:
    """
    Get a tracer instance.

    Args:
        name: Tracer name (typically __name__)

    Returns:
        Tracer instance
    """
    return trace.get_tracer(name)
