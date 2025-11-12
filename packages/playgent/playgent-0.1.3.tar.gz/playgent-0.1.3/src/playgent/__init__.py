"""Playgent SDK for tracking LLM API calls with automatic detection"""

__version__ = "0.1.3"

from .core import (
    create_trace,
    get_trace,
    get_trace_events,
    init,
    reset,
    trace,
    set_session,
    shutdown,
)
from .decorators import record
from .types import EndpointEvent, EvaluationResult, Judge, Trace, TestCase
from .patchers import patch_library, unpatch_library, unpatch_all
from .wrappers import (
    wrap_openai,
    wrap_anthropic,
    unwrap_openai,
    unwrap_anthropic,
    is_wrapped,
    WrapperError,
)

# Main exports
__all__ = [
    # Core functions
    "init",
    "record",
    "trace",
    "set_session",
    "create_trace",
    "reset",
    "shutdown",
    # Wrapper functions (recommended for production)
    "wrap_openai",
    "wrap_anthropic",
    "unwrap_openai",
    "unwrap_anthropic",
    "is_wrapped",
    "WrapperError",
    # Patching functions (legacy, use wrappers instead)
    "patch_library",
    "unpatch_library",
    "unpatch_all",
    # Testing functions
    "get_trace_events",
    "get_trace",
    # Data models
    "EndpointEvent",
    "Trace",
    "TestCase",
    "EvaluationResult",
    "Judge"
]