"""
Core functionality for Playgent SDK

This module provides all the functions that were previously methods on PlaygentClient.
"""

import atexit
import contextvars
import logging
import os
import threading
import time
import uuid
from queue import Empty, Queue
from typing import Any, Dict, List, Optional, Tuple, Union

from . import state
from .types import EndpointEvent, Judge, Trace
from .import_hooks import register_post_import_hook
from .patchers import patch_library, SUPPORTED_LIBRARIES

logger = logging.getLogger(__name__)


def _setup_auto_patching():
    """Set up automatic patching for supported LLM libraries."""
    import sys

    for library_name in SUPPORTED_LIBRARIES:
        # Check if library is already imported
        if library_name in sys.modules:
            # Patch immediately
            logger.debug(f"Library {library_name} already imported, patching now")
            patch_library(library_name)
        else:
            # Register hook for when it gets imported
            logger.debug(f"Registering import hook for {library_name}")

            def create_patch_hook(lib_name):
                """Create a closure to capture library name."""
                def patch_hook(module):
                    logger.debug(f"Import hook fired for {lib_name}, patching now")
                    patch_library(lib_name)
                return patch_hook

            register_post_import_hook(create_patch_hook(library_name), library_name)


class TraceContext:
    """Context manager for setting trace context"""

    def __init__(self, trace_id: Optional[str], person_id: Optional[str] = None,
                 endpoint_events: Optional[List[EndpointEvent]] = None,
                 judge: Optional[Judge] = None):
        self.trace_id = trace_id  # Can be None now
        self.person_id = person_id
        self.endpoint_events = endpoint_events or []
        self.judge = judge
        self.token = None

    def __enter__(self) -> Union[Optional[str], Tuple[List[EndpointEvent], Optional[Judge]]]:
        """Set the trace context when entering"""
        try:
            # Only set context if we have a valid trace_id
            if self.trace_id:
                context_data = state.TraceContextData(
                    trace_id=self.trace_id,
                    person_id=self.person_id
                )
                self.token = state._trace_context.set(context_data)
                logger.debug(f"TraceContext.__enter__: Set context with trace_id={self.trace_id}, person_id={self.person_id}")
            else:
                logger.debug("TraceContext.__enter__: No trace_id, skipping context set")

            # For test cases, return inputs and judge
            if self.endpoint_events and self.judge:
                logger.debug(f"TraceContext.__enter__: Returning {len(self.endpoint_events)} events and judge for test mode")
                return self.endpoint_events, self.judge
            # For regular traces, return trace_id (which may be None)
            logger.debug(f"TraceContext.__enter__: Returning trace_id={self.trace_id} for regular mode")
            return self.trace_id
        except Exception as e:
            logger.debug(f"TraceContext.__enter__ failed (silently handled): {e}")
            # Return safe defaults
            if self.endpoint_events is not None:
                return self.endpoint_events, self.judge
            return None

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Reset the trace context when exiting"""
        if self.token is not None:
            state._trace_context.reset(self.token)
            logger.debug(f"TraceContext.__exit__: Reset context for trace_id={self.trace_id}")


def init(api_key: Optional[str] = None, server_url: Optional[str] = None, auto_patch: bool = True) -> bool:
    """[DEPRECATED] Initialize Playgent with configuration

    This function is deprecated. Use the wrapper approach instead:

        from openai import OpenAI
        import playgent

        # New approach (recommended)
        client = playgent.wrap_openai(OpenAI(), api_key="your-key")

    The wrapper approach is safer, cleaner, and supports per-client configuration.

    Args:
        api_key: API key for authentication. If not provided, reads from PLAYGENT_API_KEY env var
        server_url: Backend server URL. If not provided, uses default or PLAYGENT_SERVER_URL env var
        auto_patch: If True, automatically patch supported LLM libraries for tracking

    Returns:
        bool: True if initialization succeeded, False if it failed (tracking will be disabled)

    Note:
        This function will never raise exceptions. If initialization fails, it logs a warning
        and disables tracking, allowing your application to continue running normally.
    """
    import warnings
    warnings.warn(
        "playgent.init() is deprecated. Use the wrapper approach instead:\n"
        "    client = playgent.wrap_openai(OpenAI(), api_key='your-key')\n"
        "See documentation for migration guide.",
        DeprecationWarning,
        stacklevel=2
    )
    try:
        # Set API key with thread safety
        with state._state_lock:
            state.api_key = api_key or os.getenv("PLAYGENT_API_KEY")
            if not state.api_key:
                logger.warning(
                    "Playgent API key not provided. Tracking disabled. To enable tracking:\n"
                    "1. Set PLAYGENT_API_KEY environment variable, or\n"
                    "2. Call playgent.init(api_key='your-key')"
                )
                state.is_running = False
                return False

            # Set server URL
            if server_url:
                state.server_url = server_url
            else:
                env_server_url = os.getenv("PLAYGENT_SERVER_URL")
                if env_server_url:
                    state.server_url = env_server_url

        logger.info(f"Playgent initialized with server URL: {state.server_url}")

        # Initialize OpenTelemetry tracer
        from .spans import initialize_tracer
        initialize_tracer()

        # Set up automatic patching if enabled
        if auto_patch:
            _setup_auto_patching()

        return True

    except Exception as e:
        logger.error(f"Playgent initialization failed: {e}. Tracking disabled.")
        state.is_running = False
        return False


def ensure_initialized():
    """Ensure Playgent is initialized, auto-initialize if possible"""
    if state.api_key is None:
        init()  # Will not raise - returns False if no env var is set


def create_trace(person_id: Optional[str] = None, trace_id: Optional[str] = None) -> Optional[str]:
    """Create a new trace via the backend API

    Args:
        person_id: Optional person ID to associate with the trace
        trace_id: Optional trace ID to use (if provided, backend will register this specific ID)

    Returns:
        The newly created trace ID, or None if creation fails

    Note:
        This function will never raise exceptions - it returns None on any error
    """
    try:
        ensure_initialized()

        import httpx
        headers = {
            "Authorization": f"Bearer {state.api_key}",
            "Content-Type": "application/json"
        }

        payload = {}
        if person_id:
            payload["person_id"] = person_id
        if trace_id:
            payload["trace_id"] = trace_id

        response = httpx.post(
            f"{state.server_url}/traces",
            json=payload,
            headers=headers,
            timeout=5.0
        )

        if response.status_code == 201:
            data = response.json()
            trace_id: str = data.get("trace_id", "")  # Backend now returns trace_id
            if not trace_id:
                logger.debug("Server returned empty trace_id")
                return None
            # Basic validation: trace_id should be alphanumeric with hyphens
            import re
            if not re.match(r'^[a-zA-Z0-9\-_]+$', trace_id):
                logger.debug("Invalid trace_id format received from server")
                return None
            logger.info(f"Created new trace: {trace_id}")
            return trace_id
        else:
            logger.debug(f"Failed to create trace (status {response.status_code})")
            return None
    except Exception as e:
        # Never expose API key in errors
        error_msg = str(e).replace(state.api_key, "***") if state.api_key and state.api_key in str(e) else str(e)
        logger.debug(f"Failed to create trace (silently handled): {error_msg}")
        return None




def set_session(session_id: str, person_id: Optional[str] = None):
    """Set the session context for the current execution

    This allows you to associate a session/conversation ID with the current trace.
    The session_id will be included in all spans created within this context.
    The context is stored in a contextvar, making it thread-safe and async-safe.

    This function also creates/updates the trace in the backend.

    Args:
        session_id: The session/conversation ID to associate with this trace
        person_id: Optional person ID to associate with the session
    """
    ensure_initialized()

    # Get the current OpenTelemetry trace_id (this is the source of truth)
    from .spans import get_current_trace_id_as_uuid
    otel_trace_id = get_current_trace_id_as_uuid()

    # Get existing context
    context = state._trace_context.get()

    # Create/update the trace in the backend with session_id
    try:
        import httpx
        headers = {
            "Authorization": f"Bearer {state.api_key}",
            "Content-Type": "application/json"
        }

        payload = {"session_id": session_id}
        if otel_trace_id:
            payload["trace_id"] = otel_trace_id
        if person_id:
            payload["person_id"] = person_id
        response = httpx.post(
            f"{state.server_url}/traces",
            json=payload,
            headers=headers,
            timeout=5.0
        )

        if response.status_code in [200, 201]:
            logger.info(f"Created/updated trace in backend with session_id={session_id}")
        elif response.status_code == 409:
            logger.debug(f"Session {session_id} already exists in backend")
        else:
            logger.warning(f"Failed to create/update trace in backend (status {response.status_code})")
    except Exception as e:
        # Sanitize error to avoid exposing API key
        error_msg = str(e).replace(state.api_key, "***") if state.api_key and state.api_key in str(e) else str(e)
        logger.warning(f"Failed to create/update trace in backend: {error_msg}")

    # Update the context with session_id and OTel trace_id
    context_data = state.TraceContextData(
        trace_id=otel_trace_id or "",  # Use OTel trace_id or empty string
        session_id=session_id,
        person_id=person_id
    )
    state._trace_context.set(context_data)
    logger.info(f"[SET_SESSION] Set session_id={session_id}, person_id={person_id}, trace_id={otel_trace_id}")




def trace(trace_id: Optional[str] = None, test_case_name: Optional[str] = None):
    """Unified context manager for traces and test replay

    Usage for regular traces:
        with trace() as trace_id:
            # All calls within this block use the trace_id
            my_function("Hello")

    Usage for test replay:
        with trace(test_case_name="my-test") as (inputs, judge):
            for inp in inputs:
                my_function(**inp.arguments)
            result = judge.evaluate()

    Args:
        trace_id: Optional trace ID to use. If None, creates a new trace.
        test_case_name: Optional test case name for replay testing.

    Returns:
        For regular traces: Returns the trace_id (or None if trace creation fails)
        For test traces: Returns (endpoint_events, judge) tuple (or empty list and None on failure)

    Note:
        This function will never raise exceptions - it provides defaults on any error
    """
    # Test replay mode
    if test_case_name:
        logger.debug(f"trace: Starting test replay mode for test_case_name={test_case_name}")

        try:
            ensure_initialized()

            import httpx
            client = httpx.Client(timeout=10.0)
            headers = {
                "Authorization": f"Bearer {state.api_key}"
            }

            # Search for test case by name
            logger.debug(f"trace: Searching for test case with name={test_case_name}")
            search_response = client.get(
                f"{state.server_url}/tests",
                params={"name": test_case_name},
                headers=headers
            )

            if search_response.status_code != 200:
                logger.debug(f"Failed to search test cases (status {search_response.status_code})")
                client.close()
                # Return empty context that won't fail
                return TraceContext(None, person_id=None, endpoint_events=[], judge=None)

            search_results = search_response.json()
            test_cases = search_results.get("test_cases", [])

            if not test_cases:
                logger.debug(f"No test case found with name: {test_case_name}")
                client.close()
                return TraceContext(None, person_id=None, endpoint_events=[], judge=None)

            if len(test_cases) > 1:
                logger.debug(f"Multiple test cases found with name: {test_case_name}. Please use a more specific name.")
                client.close()
                return TraceContext(None, person_id=None, endpoint_events=[], judge=None)

            # Get the test case ID
            test_case_id = test_cases[0]["id"]
            logger.debug(f"trace: Found test case with id={test_case_id}")

            # Fetch the full test case details
            response = client.get(
                f"{state.server_url}/tests/{test_case_id}",
                headers=headers
            )

            if response.status_code != 200:
                logger.debug(f"Failed to fetch test case (status {response.status_code})")
                client.close()
                return TraceContext(None, person_id=None, endpoint_events=[], judge=None)

            test_case = response.json()
            annotated_trace_id = test_case.get("annotated_trace")

            if not annotated_trace_id:
                logger.debug(f"Test case {test_case_name} (ID: {test_case_id}) has no annotated_trace configured")
                client.close()
                return TraceContext(None, person_id=None, endpoint_events=[], judge=None)

            logger.info(f"Using annotated_trace {annotated_trace_id} from test case {test_case_name}")

            # Create new trace for this test run
            new_trace_id = create_trace()
            if not new_trace_id:
                logger.debug("Failed to create new trace for test run")
                client.close()
                return TraceContext(None, person_id=None, endpoint_events=[], judge=None)

            # Update trace status to "running"
            try:
                client.patch(
                    f"{state.server_url}/traces/{new_trace_id}",
                    json={"status": "running"},
                    headers=headers
                )
            except Exception as e:
                logger.debug(f"Failed to update trace status: {e}")
                # Continue anyway - not critical

            # Get endpoint events from the annotated trace
            endpoint_events = get_trace_events(annotated_trace_id)

            # Create Judge instance
            judge = Judge(
                test_case_id=test_case_id,
                trace_id=new_trace_id,
                client=client,
                headers=headers
            )

            return TraceContext(new_trace_id, person_id=None, endpoint_events=endpoint_events, judge=judge)

        except Exception as e:
            logger.debug(f"trace test mode failed (silently handled): {e}")
            try:
                client.close()
            except:
                pass
            # Return empty context that won't fail
            return TraceContext(None, person_id=None, endpoint_events=[], judge=None)

    # Regular trace mode
    try:
        if trace_id is None:
            trace_id = create_trace()
            if trace_id:
                logger.debug(f"trace: Created new regular trace with id={trace_id}")
            else:
                logger.debug("trace: Failed to create new trace, using None")
        else:
            logger.debug(f"trace: Using provided trace_id={trace_id}")

        return TraceContext(trace_id)
    except Exception as e:
        logger.debug(f"trace regular mode failed (silently handled): {e}")
        return TraceContext(None)




# Span emission is now handled by OpenTelemetry's BatchSpanProcessor
# No need for custom emit_span, flush_buffered_spans, start_span_sender_if_needed, or span_sender_worker


def event_sender_worker():
    """Background thread worker to send events in batches"""
    import httpx

    client = httpx.Client(timeout=2.0)
    max_batch_size = min(state.batch_size, 100)  # Cap at 100 events per batch

    while not state.stop_sender.is_set():
        batch = []

        # Try to collect up to max_batch_size events
        for _ in range(max_batch_size):
            try:
                # Wait up to 0.5 seconds for each event
                event = state.event_queue.get(timeout=0.5)
                batch.append(event)
            except Empty:
                # No more events available, send what we have
                break

        # Send batch if we collected any events
        if batch:
            try:
                headers = {
                    "Authorization": f"Bearer {state.api_key}"
                }

                client.post(
                    f"{state.server_url}/events",
                    json={"events": batch},
                    headers=headers,
                    timeout=1.0
                )
            except Exception as e:
                # Sanitize error to avoid exposing API key
                error_msg = str(e).replace(state.api_key, "***") if state.api_key and state.api_key in str(e) else str(e)
                logger.error(f"Failed to send events: {error_msg}")

    # Send any remaining events before shutting down
    remaining = []
    while not state.event_queue.empty():
        try:
            remaining.append(state.event_queue.get_nowait())
        except Empty:
            break

    if remaining:
        try:
            headers = {
                "Authorization": f"Bearer {state.api_key}"
            }

            client.post(
                f"{state.server_url}/events",
                json={"events": remaining},
                headers=headers,
                timeout=1.0
            )
        except Exception as e:
            # Sanitize error to avoid exposing API key
            error_msg = str(e).replace(state.api_key, "***") if state.api_key and state.api_key in str(e) else str(e)
            logger.error(f"Failed to send remaining events: {error_msg}")

    client.close()


def start(trace_id: Optional[str] = None, person_id: Optional[str] = None):
    """Start a Playgent tracking trace"""
    ensure_initialized()

    if state.is_running:
        logger.warning("Playgent is already running")
        return

    # Handle trace_id
    if not trace_id:
        # Get from context or create new
        context = state._trace_context.get()
        if context:
            trace_id = context.trace_id
        else:
            trace_id = state.trace_id

        if not trace_id:
            try:
                import httpx
                headers = {
                    "Authorization": f"Bearer {state.api_key}",
                    "Content-Type": "application/json"
                }

                payload = {}
                if person_id:
                    payload["person_id"] = person_id

                response = httpx.post(
                    f"{state.server_url}/traces",
                    json=payload,
                    headers=headers,
                    timeout=5.0
                )

                if response.status_code == 201:
                    data = response.json()
                    trace_id = data.get("trace_id")  # Backend now returns trace_id
                    logger.info(f"Created new trace via API: {trace_id}")
                else:
                    # Fallback to UUID if API call fails
                    logger.warning(f"Failed to create trace via API (status {response.status_code}), falling back to UUID")
                    trace_id = str(uuid.uuid4())
            except Exception as e:
                # Sanitize error to avoid exposing API key
                error_msg = str(e).replace(state.api_key, "***") if state.api_key and state.api_key in str(e) else str(e)
                logger.warning(f"Failed to create trace via API: {error_msg}, falling back to UUID")
                trace_id = str(uuid.uuid4())

    # Use lock for thread-safe state modification
    with state._state_lock:
        state.trace_id = trace_id
        state.person_id = person_id  # Can be None

        # Start sender threads
        state.stop_sender.clear()

        # Start span sender thread
        state.span_sender_thread = threading.Thread(target=span_sender_worker, daemon=True)
        state.span_sender_thread.start()

    logger.info(f"Span emission enabled - sending to {state.server_url}/spans")
    logger.info(f"Trace ID: {state.trace_id}")
    if state.person_id:
        logger.info(f"Person ID: {state.person_id}")

    # Register shutdown handler to ensure cleanup
    atexit.register(shutdown)


    state.is_running = True
    logger.info("🎯 Playgent SDK started - All LLM API calls will be tracked")


def stop():
    """End the current Playgent tracking trace and flush spans"""
    if not state.is_running:
        logger.warning("Playgent is not running")
        return

    if state.trace_id:
        try:
            import httpx
            headers = {
                "Authorization": f"Bearer {state.api_key}",
                "Content-Type": "application/json"
            }

            response = httpx.patch(
                f"{state.server_url}/traces/{state.trace_id}",
                json={"status": "completed"},
                headers=headers,
                timeout=5.0
            )

            if response.status_code == 200:
                logger.info(f"Trace {state.trace_id} marked as completed")
            else:
                logger.warning(f"Failed to update trace status (status {response.status_code})")
        except Exception as e:
            logger.warning(f"Failed to update trace status: {e}")

    # Flush spans but don't shutdown the tracer (we want to reuse it for next call)
    flush_spans()

    state.is_running = False
    logger.info("🚫 Playgent SDK stopped")



def flush_spans():
    """Flush any pending spans to the backend without shutting down the tracer"""
    try:
        from .spans import flush_tracer
        flush_tracer()
        logger.info("✅ Playgent spans flushed successfully")
    except Exception as e:
        logger.warning(f"Failed to flush spans: {e}")


def shutdown():
    """Gracefully shutdown OpenTelemetry tracer and flush remaining spans"""
    try:
        from .spans import shutdown_tracer
        shutdown_tracer()
        logger.info("✅ Playgent tracer shut down successfully")
    except Exception as e:
        logger.warning(f"Failed to shutdown tracer: {e}")


def get_trace_events(trace_id: str) -> List[EndpointEvent]:
    """Get all events for a trace, properly typed

    Args:
        trace_id: The trace ID to fetch events from

    Returns:
        List of EndpointEvent objects with 'arguments' attribute, or empty list on error

    Note:
        This function will never raise exceptions - it returns empty list on any error
    """
    try:
        ensure_initialized()

        import httpx
        client = httpx.Client(timeout=10.0)

        headers = {
            "Authorization": f"Bearer {state.api_key}"
        }

        # Fetch all endpoint events for this trace
        response = client.get(
            f"{state.server_url}/events",
            params={
                "trace_id": trace_id,
                "event_type": "endpoint",
                "limit": 1000
            },
            headers=headers
        )

        if response.status_code != 200:
            logger.debug(f"Failed to fetch events (status {response.status_code})")
            client.close()
            return []

        result = response.json()
        events = result.get("events", [])

        # Sort by timestamp to ensure correct order
        events.sort(key=lambda e: e.get("timestamp", ""))

        # Transform to EndpointEvent objects
        endpoint_events = []
        for event in events:
            data = event.get("data", {})

            # Parse data if it's a JSON string
            if isinstance(data, str):
                import json
                try:
                    data = json.loads(data)
                except (json.JSONDecodeError, ValueError) as e:
                    logger.debug(f"Failed to parse event data as JSON: {e}")
                    data = {}  # Use empty dict as fallback

            endpoint_event = EndpointEvent(
                name=data.get("name", ""),
                arguments=data.get("kwargs", {}),
                function_key=data.get("function_key", ""),
                timestamp=event.get("timestamp", ""),
                id=event.get("id", "")
            )
            endpoint_events.append(endpoint_event)

        logger.info(f"Retrieved {len(endpoint_events)} endpoint events from trace {trace_id}")
        client.close()
        return endpoint_events
    except Exception as e:
        logger.debug(f"get_trace_events failed (silently handled): {e}")
        try:
            client.close()
        except:
            pass
        return []


def get_trace(trace_id: str) -> Optional[Trace]:
    """Get trace details from backend

    Args:
        trace_id: The trace ID to fetch

    Returns:
        Trace object with all details including eval_output, or None on error

    Note:
        This function will never raise exceptions - it returns None on any error
    """
    try:
        ensure_initialized()

        import httpx
        client = httpx.Client(timeout=10.0)

        headers = {
            "Authorization": f"Bearer {state.api_key}"
        }

        response = client.get(
            f"{state.server_url}/traces/{trace_id}/status",
            headers=headers
        )

        if response.status_code == 404:
            logger.debug(f"Trace {trace_id} not found")
            client.close()
            return None
        elif response.status_code != 200:
            logger.debug(f"Failed to fetch trace (status {response.status_code})")
            client.close()
            return None

        trace_data = response.json()
        result = Trace.from_dict(trace_data)
        client.close()
        return result

    except Exception as e:
        logger.debug(f"get_trace failed (silently handled): {e}")
        try:
            client.close()
        except:
            pass
        return None


def reset():
    """Reset all global state (useful for testing)"""
    with state._state_lock:
        state.api_key = None
        state.server_url = "http://localhost:1338"
        state.batch_size = 10
        state.trace_id = None
        state.person_id = None
        state.endpoint = None
        state.is_running = False
        state.events = []
        state.event_queue = Queue()
        state.sender_thread = None
        state.stop_sender.clear()
        # Reset context var
        state._trace_context = contextvars.ContextVar('playgent_trace', default=None)