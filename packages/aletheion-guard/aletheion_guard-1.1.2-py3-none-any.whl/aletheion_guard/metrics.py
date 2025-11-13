"""Prometheus metrics for AletheionGuard."""
from prometheus_client import Counter, Histogram, Gauge, Summary
from prometheus_fastapi_instrumentator import Instrumentator

# Request counters
audit_requests_total = Counter(
    'aletheion_audit_requests_total',
    'Total number of audit requests',
    ['verdict']  # Labels: ACCEPT, MAYBE, REFUSED
)

batch_requests_total = Counter(
    'aletheion_batch_requests_total',
    'Total number of batch requests',
    ['status']  # Labels: success, partial_failure, failure
)

# Error tracking
errors_total = Counter(
    'aletheion_errors_total',
    'Total number of errors',
    ['error_type']
)

# Latency tracking
audit_latency_seconds = Histogram(
    'aletheion_audit_latency_seconds',
    'Audit request latency in seconds',
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

embedding_latency_seconds = Histogram(
    'aletheion_embedding_latency_seconds',
    'Embedding generation latency in seconds',
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5]
)

# Model predictions
q1_predictions = Summary(
    'aletheion_q1_predictions',
    'Q1 (aleatoric uncertainty) predictions'
)

q2_predictions = Summary(
    'aletheion_q2_predictions',
    'Q2 (epistemic uncertainty) predictions'
)

height_predictions = Summary(
    'aletheion_height_predictions',
    'Height (epistemic proximity) predictions'
)

# Calibration metrics (runtime)
calibration_ece = Gauge(
    'aletheion_calibration_ece',
    'Expected Calibration Error (ECE) - runtime'
)

calibration_rce = Gauge(
    'aletheion_calibration_rce',
    'Regression Calibration Error (RCE) - runtime'
)

# System metrics
active_requests = Gauge(
    'aletheion_active_requests',
    'Number of requests currently being processed'
)

model_loaded = Gauge(
    'aletheion_model_loaded',
    'Whether the model is loaded (1) or not (0)'
)


def setup_metrics(app):
    """Setup Prometheus metrics for FastAPI app."""
    instrumentator = Instrumentator(
        should_group_status_codes=False,
        should_ignore_untemplated=True,
        should_respect_env_var=True,
        should_instrument_requests_inprogress=True,
        excluded_handlers=[".*admin.*", "/metrics"],
        env_var_name="ENABLE_METRICS",
        inprogress_name="aletheion_requests_inprogress",
        inprogress_labels=True,
    )

    instrumentator.instrument(app).expose(app, include_in_schema=False)

    return instrumentator
