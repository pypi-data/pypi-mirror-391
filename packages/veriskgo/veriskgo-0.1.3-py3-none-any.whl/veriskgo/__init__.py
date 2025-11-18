"""
VeriskGO Observability SDK
~~~~~~~~~~~~~~~~~~~~~~~~~~

A lightweight telemetry SDK that sends GenAI traces to Langfuse (and optionally
New Relic / OTEL collector). Provides:

• init_langfuse()    → enable Langfuse client
• start_trace()      → begin a trace
• start_span()       → begin a span
• end_span()         → finish a span
• end_trace()        → finish entire trace and send bundle

Used by GenAI apps to simplify observability integration.
"""

from .langfuse import (
    init_langfuse,
    send_bundle,
    is_enabled,
)

from .tracer import (
    start_trace,
    end_trace,
    start_span,
    end_span,
)

# Public interface of the SDK
__all__ = [
    "init_langfuse",
    "send_bundle",
    "is_enabled",
    "start_trace",
    "end_trace",
    "start_span",
    "end_span",
]
 
