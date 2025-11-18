"""Telemetry utilities (placeholder).

Provides a lightweight `optional_span` context manager so code can instrument blocks
without requiring a full tracing backend. When tracing is disabled or not yet
implemented, the span is a no-op. This maintains interface stability while
avoiding import errors.

Replace with real OpenTelemetry integration when ENABLE_OTEL=true.
"""

from contextlib import contextmanager
from typing import Any, Dict, Iterator


@contextmanager
def optional_span(
    name: str,
    tracer_name: str | None = None,
    attributes: Dict[str, Any] | None = None,
) -> Iterator[Any]:
    """Yield a no-op span placeholder.

    Args:
        name: Logical name of the traced operation.
        tracer_name: Name of tracer (unused placeholder).
        attributes: Optional mapping of attributes (ignored in placeholder).
    """
    # Real implementation would start a span and expose attribute setters.
    yield None


__all__ = ["optional_span"]
