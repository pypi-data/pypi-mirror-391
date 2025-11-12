"""
Standalone decorators for Playgent
"""
import functools
import inspect
import logging
from typing import Callable, Dict

from .types import parse_endpoint_event

logger = logging.getLogger(__name__)

# Global function registry for replay testing
_function_registry: Dict[str, Callable] = {}

# Track registered trace IDs to avoid duplicate backend calls
_registered_trace_ids: set = set()


def record(func):
    """
    Decorator to record function calls for replay testing.

    This decorator records function calls and their arguments, automatically
    managing traces and emitting events to the Playgent backend.

    Usage:
        from playgent import record

        @record
        def my_function(arg1, arg2):
            ...

    The decorator automatically:
    - Initializes Playgent from environment variables if needed
    - Creates traces as needed
    - Records function calls with their arguments
    - Manages LLM API event tracking

    Args:
        func: The function to decorate

    Returns:
        A wrapped version of the function that records calls
    """
    from . import core, state

    # Get function name and create registry key
    func_name = func.__name__
    function_key = f"{func.__module__}:{func_name}"

    if inspect.iscoroutinefunction(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                # Ensure Playgent is initialized
                core.ensure_initialized()

                # Convert args to kwargs using function signature
                sig = inspect.signature(func)
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()
                all_kwargs = dict(bound_args.arguments)

                # Filter out non-serializable objects like FastAPI Request
                serializable_kwargs = {}
                for k, v in all_kwargs.items():
                    # Skip Request objects from FastAPI/Starlette
                    if v.__class__.__name__ == 'Request':
                        serializable_kwargs[k] = f"<{v.__class__.__name__} object>"
                    else:
                        serializable_kwargs[k] = v

                # Get trace context
                context = state._trace_context.get()
                person_id = context.person_id if context else None
                session_id = context.session_id if context else None

                logger.debug(f"@record decorator: Retrieved context - person_id={person_id}, session_id={session_id}")

                # Enable patching
                with state._state_lock:
                    state.is_running = True  # Enable patching
                    logger.debug("@record decorator: Enabled patching")

                # Use OpenTelemetry spans
                from .spans import get_tracer, get_current_trace_id_as_uuid
                from .types import serialize_to_dict
                from opentelemetry.trace import StatusCode
                import json

                tracer = get_tracer()

                try:
                    with tracer.start_as_current_span(func_name) as span:
                        # Set span kind
                        span.set_attribute("span.kind", "endpoint")

                        # Extract OpenTelemetry trace_id and register with backend (once per trace)
                        otel_trace_id = get_current_trace_id_as_uuid()
                        if otel_trace_id and otel_trace_id not in _registered_trace_ids:
                            # create_trace now returns None on error instead of raising
                            trace_result = core.create_trace(person_id=person_id, trace_id=otel_trace_id)
                            if trace_result:
                                _registered_trace_ids.add(otel_trace_id)
                                logger.info(f"@record: Registered trace {otel_trace_id}")
                            else:
                                logger.debug(f"@record: Failed to register trace {otel_trace_id}, continuing anyway")

                    # Update context with trace_id (preserve existing session_id if set)
                    existing_context = state._trace_context.get()
                    state._trace_context.set(state.TraceContextData(
                        trace_id=otel_trace_id or "",
                        person_id=person_id or (existing_context.person_id if existing_context else None),
                        session_id=session_id or (existing_context.session_id if existing_context else None)
                    ))

                    # Set span attributes
                    span.set_attribute("function.name", func_name)
                    span.set_attribute("function.args", json.dumps(serialize_to_dict(serializable_kwargs)))
                    span.set_attribute("function.key", function_key)

                    # Add session_id and person_id from context
                    context = state._trace_context.get()
                    if context:
                        if context.session_id:
                            span.set_attribute("session_id", context.session_id)
                        if context.person_id:
                            span.set_attribute("person_id", context.person_id)

                    # Execute the wrapped function
                    response = await func(*args, **kwargs)

                    # Check if session_id was set inside the function via set_session()
                    final_context = state._trace_context.get()
                    if final_context:
                        if final_context.session_id and final_context.session_id != (context.session_id if context else None):
                            # Session ID was set during execution - add it to the span
                            span.set_attribute("session_id", final_context.session_id)
                        if final_context.person_id and final_context.person_id != (context.person_id if context else None):
                            # Person ID was updated during execution
                            span.set_attribute("person_id", final_context.person_id)

                    # Add result to span attributes (serialize to JSON string for OTel compatibility)
                    span.set_attribute("function.result", json.dumps(serialize_to_dict(response)))

                    # Mark span as successful
                    span.set_status(StatusCode.OK)

                    return response
                finally:
                    # Stop and flush (set is_running=False, stop threads, mark trace complete)
                    try:
                        core.stop()
                    except Exception as e:
                        logger.debug(f"@record: core.stop() failed (silently handled): {e}")
            except Exception as e:
                # If ANY Playgent operation fails, just call the original function
                logger.debug(f"@record decorator failed (silently handled): {e}")
                return await func(*args, **kwargs)

        # Register the WRAPPED function in global registry
        _function_registry[function_key] = async_wrapper

        # Mark the wrapper so middleware can detect it
        async_wrapper._playgent_decorated = True
        async_wrapper._playgent_func_name = func_name

        return async_wrapper
    else:
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                # Ensure Playgent is initialized
                core.ensure_initialized()

                # Convert args to kwargs using function signature
                sig = inspect.signature(func)
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()
                all_kwargs = dict(bound_args.arguments)

                # Filter out non-serializable objects like FastAPI Request
                serializable_kwargs = {}
                for k, v in all_kwargs.items():
                    # Skip Request objects from FastAPI/Starlette
                    if v.__class__.__name__ == 'Request':
                        serializable_kwargs[k] = f"<{v.__class__.__name__} object>"
                    else:
                        serializable_kwargs[k] = v

                # Get trace context
                context = state._trace_context.get()
                person_id = context.person_id if context else None
                session_id = context.session_id if context else None

                logger.debug(f"@record decorator: Retrieved context - person_id={person_id}, session_id={session_id}")

                # Enable patching
                with state._state_lock:
                    state.is_running = True  # Enable patching
                    logger.debug("@record decorator: Enabled patching")

                # Use OpenTelemetry spans
                from .spans import get_tracer, get_current_trace_id_as_uuid
                from .types import serialize_to_dict
                from opentelemetry.trace import StatusCode
                import json

                tracer = get_tracer()

                try:
                    with tracer.start_as_current_span(func_name) as span:
                        # Set span kind
                        span.set_attribute("span.kind", "endpoint")

                        # Extract OpenTelemetry trace_id and register with backend (once per trace)
                        otel_trace_id = get_current_trace_id_as_uuid()
                        if otel_trace_id and otel_trace_id not in _registered_trace_ids:
                            # create_trace now returns None on error instead of raising
                            trace_result = core.create_trace(person_id=person_id, trace_id=otel_trace_id)
                            if trace_result:
                                _registered_trace_ids.add(otel_trace_id)
                                logger.info(f"@record: Registered trace {otel_trace_id}")
                            else:
                                logger.debug(f"@record: Failed to register trace {otel_trace_id}, continuing anyway")

                    # Update context with trace_id (preserve existing session_id if set)
                    existing_context = state._trace_context.get()
                    state._trace_context.set(state.TraceContextData(
                        trace_id=otel_trace_id or "",
                        person_id=person_id or (existing_context.person_id if existing_context else None),
                        session_id=session_id or (existing_context.session_id if existing_context else None)
                    ))

                    # Set span attributes
                    span.set_attribute("function.name", func_name)
                    span.set_attribute("function.args", json.dumps(serialize_to_dict(serializable_kwargs)))
                    span.set_attribute("function.key", function_key)

                    # Add session_id and person_id from context
                    context = state._trace_context.get()
                    if context:
                        if context.session_id:
                            span.set_attribute("session_id", context.session_id)
                        if context.person_id:
                            span.set_attribute("person_id", context.person_id)

                    # Execute the wrapped function
                    response = func(*args, **kwargs)

                    # Check if session_id was set inside the function via set_session()
                    final_context = state._trace_context.get()
                    if final_context:
                        if final_context.session_id and final_context.session_id != (context.session_id if context else None):
                            # Session ID was set during execution - add it to the span
                            span.set_attribute("session_id", final_context.session_id)
                        if final_context.person_id and final_context.person_id != (context.person_id if context else None):
                            # Person ID was updated during execution
                            span.set_attribute("person_id", final_context.person_id)

                    # Add result to span attributes (serialize to JSON string for OTel compatibility)
                    span.set_attribute("function.result", json.dumps(serialize_to_dict(response)))

                    # Mark span as successful
                    span.set_status(StatusCode.OK)

                    return response
                finally:
                    # Stop and flush (set is_running=False, stop threads, mark trace complete)
                    try:
                        core.stop()
                    except Exception as e:
                        logger.debug(f"@record: core.stop() failed (silently handled): {e}")
            except Exception as e:
                # If ANY Playgent operation fails, just call the original function
                logger.debug(f"@record decorator failed (silently handled): {e}")
                return func(*args, **kwargs)

        # Register the WRAPPED function in global registry
        _function_registry[function_key] = sync_wrapper

        # Mark the wrapper so middleware can detect it
        sync_wrapper._playgent_decorated = True
        sync_wrapper._playgent_func_name = func_name

        return sync_wrapper


def get_function_registry():
    """Get the global function registry for debugging/testing"""
    return _function_registry