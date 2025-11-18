# tracer.py
import uuid
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from .langfuse import send_bundle, is_enabled


# Global active trace
_ACTIVE_TRACE: Dict[str, Any] = {
    "trace_id": None,
    "spans": [],
    "active_span_stack": [],
}


# =======================
# Utility helpers
# =======================

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id() -> str:
    return str(uuid.uuid4())


# =======================
# Trace API
# =======================

def start_trace(
    name: str,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Creates a NEW trace + root span.
    """
    trace_id = new_id()
    span_id = new_id()

    root_span = {
        "span_id": span_id,
        "parent_span_id": None,
        "name": name,
        "operation": "trace.start",
        "timestamp": now_iso(),
        "type": "root",
        "input": "",
        "output": "",
        "metadata": metadata or {},
        "usage": {},
        "duration_ms": 0,
        "success": True,
    }

    if user_id: root_span["metadata"]["user_id"] = user_id
    if session_id: root_span["metadata"]["session_id"] = session_id

    _ACTIVE_TRACE["trace_id"] = trace_id
    _ACTIVE_TRACE["spans"] = [root_span]
    _ACTIVE_TRACE["active_span_stack"] = [{
        "span_id": span_id,
        "start_time": time.time(),
    }]

    return trace_id


def start_span(name: str, metadata: Optional[Dict[str, Any]] = None) -> str:
    """
    Create a child span under the current active span.
    """
    if _ACTIVE_TRACE["trace_id"] is None:
        raise RuntimeError("start_span() called before start_trace()")

    span_id = new_id()
    stack = _ACTIVE_TRACE["active_span_stack"]
    parent_span_id = stack[-1]["span_id"] if stack else None

    span = {
        "span_id": span_id,
        "parent_span_id": parent_span_id,
        "name": name,
        "operation": "child",
        "timestamp": now_iso(),
        "type": "child",
        "input": "",
        "output": "",
        "metadata": metadata or {},
        "usage": {},
        "duration_ms": 0,
        "success": True,
    }

    _ACTIVE_TRACE["spans"].append(span)
    stack.append({"span_id": span_id, "start_time": time.time()})

    return span_id


def end_span(output: str = "", success: bool = True, error: str = ""):
    """
    Ends the most recent active span.
    """
    stack = _ACTIVE_TRACE["active_span_stack"]
    if not stack:
        return

    popped = stack.pop()
    span_id = popped["span_id"]
    duration = int((time.time() - popped["start_time"]) * 1000)

    for span in _ACTIVE_TRACE["spans"]:
        if span["span_id"] == span_id:
            span["output"] = output
            span["success"] = success
            if error:
                span["metadata"]["error_message"] = error
            span["duration_ms"] = duration
            return


def set_span_input(text: str):
    """
    Update input text of current span.
    """
    stack = _ACTIVE_TRACE["active_span_stack"]
    if not stack:
        return

    span_id = stack[-1]["span_id"]
    for span in _ACTIVE_TRACE["spans"]:
        if span["span_id"] == span_id:
            span["input"] = text
            return


def set_span_usage(usage_dict: Dict[str, Any]):
    """
    Add usage metrics to current span.
    """
    stack = _ACTIVE_TRACE["active_span_stack"]
    if not stack:
        return

    span_id = stack[-1]["span_id"]
    for span in _ACTIVE_TRACE["spans"]:
        if span["span_id"] == span_id:
            span["usage"].update(usage_dict)
            return


# =======================
# Finalize trace + send
# =======================

def end_trace():
    if _ACTIVE_TRACE["trace_id"] is None:
        return None

    # End ANY open spans
    while _ACTIVE_TRACE["active_span_stack"]:
        end_span()

    bundle = {
        "trace_id": _ACTIVE_TRACE["trace_id"],
        "spans": _ACTIVE_TRACE["spans"],
    }

    # Send to Langfuse
    if is_enabled():
        send_bundle(bundle)

    # Reset trace
    _ACTIVE_TRACE["trace_id"] = None
    _ACTIVE_TRACE["spans"] = []
    _ACTIVE_TRACE["active_span_stack"] = []

    return bundle
