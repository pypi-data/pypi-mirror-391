"""
Middleware for capturing HTTP request details and managing trace context
"""
import contextvars
import json
import logging
from typing import Callable, Optional

try:
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.requests import Request
    from starlette.responses import Response
except ImportError:
    BaseHTTPMiddleware = None
    Request = None
    Response = None

from . import state

logger = logging.getLogger(__name__)

# Context variable to store HTTP request data thread-safely
_http_request_context: contextvars.ContextVar[Optional[dict]] = contextvars.ContextVar('playgent_http_request', default=None)


def get_http_request_data() -> Optional[dict]:
    """Get the current HTTP request data from context.

    Returns:
        The HTTP request data dict if available, None otherwise.
    """
    return _http_request_context.get()


class PlaygentMiddleware:
    """Middleware for capturing HTTP request details for Playgent-decorated endpoints

    This middleware automatically captures HTTP request details (method, URL, headers, body)
    for endpoints decorated with @record and adds them to the endpoint event.

    Usage with FastAPI:
        from fastapi import FastAPI
        from playgent.middleware import PlaygentMiddleware

        app = FastAPI()
        app.add_middleware(PlaygentMiddleware)

        @app.post("/endpoint")
        @record
        async def my_endpoint(request: Request):
            ...
    """

    def __init__(self, app):
        """Initialize the middleware

        Args:
            app: The ASGI application to wrap
        """
        if BaseHTTPMiddleware is None:
            raise ImportError(
                "Starlette is required to use PlaygentMiddleware. "
                "Install it with: pip install starlette"
            )
        self.app = app

    async def __call__(self, scope, receive, send):
        """ASGI middleware implementation"""
        if scope["type"] != "http":
            # Not an HTTP request, pass through
            return await self.app(scope, receive, send)

        # Extract headers early for trace/test case setup
        headers_dict = {}
        for name, value in scope.get("headers", []):
            headers_dict[name.decode().lower()] = value.decode()

        # Check for Playgent headers and set trace context
        # Support both new trace headers and legacy trace headers for backward compatibility
        trace_id = headers_dict.get("x-playgent-trace-id") or headers_dict.get("x-playgent-session-id")
        person_id = headers_dict.get("x-playgent-person-id")

        if trace_id or person_id:
            logger.debug(f"PlaygentMiddleware: Found headers - X-Playgent-Trace-Id={trace_id}, X-Playgent-Person-Id={person_id}")

        # If we have either header, set the trace context
        context_token = None
        if trace_id or person_id:
            # If trace_id not provided, create new trace with person_id
            if not trace_id:
                try:
                    # Create a new trace
                    from .core import create_trace
                    trace_id = create_trace(person_id=person_id)
                    if trace_id:
                        logger.info(f"PlaygentMiddleware: Created trace {trace_id} for person {person_id}")
                    else:
                        logger.debug(f"PlaygentMiddleware: Failed to create trace for person {person_id}")
                except Exception as e:
                    logger.debug(f"PlaygentMiddleware: Failed to create trace (silently handled): {e}")
                    trace_id = None

            if trace_id:
                try:
                    # Set the trace context
                    context_data = state.TraceContextData(
                        trace_id=trace_id,
                        person_id=person_id
                    )
                    context_token = state._trace_context.set(context_data)
                    logger.debug(f"PlaygentMiddleware: Set trace context - trace_id={trace_id}, person_id={person_id}")
                except Exception as e:
                    logger.debug(f"PlaygentMiddleware: Failed to set trace context (silently handled): {e}")
                    context_token = None

        # Try to get the route and endpoint
        route = scope.get("route")
        if not route:
            # No route matched, pass through
            try:
                return await self.app(scope, receive, send)
            finally:
                # Clean up context
                if context_token:
                    state._trace_context.reset(context_token)

        # Check if endpoint is decorated with @record
        handler = getattr(route, "endpoint", None)
        if not handler or not hasattr(handler, '_playgent_decorated'):
            # Not a Playgent-decorated endpoint, pass through
            try:
                return await self.app(scope, receive, send)
            finally:
                # Clean up context
                if context_token:
                    state._trace_context.reset(context_token)

        # This is a Playgent-decorated endpoint, capture request details
        logger.debug(f"Capturing HTTP request for Playgent endpoint: {scope['path']}")

        # Read the request body
        body_bytes = b""

        async def receive_wrapper():
            nonlocal body_bytes
            message = await receive()
            if message["type"] == "http.request":
                body = message.get("body", b"")
                body_bytes += body
                # Store the body so we can re-inject it
                if not message.get("more_body", False):
                    # Body is complete, store it for re-injection
                    scope["_playgent_body"] = body_bytes
            return message

        # Create a new receive that will replay the body
        body_consumed = False

        async def receive_replay():
            nonlocal body_consumed
            if not body_consumed and scope.get("_playgent_body"):
                body_consumed = True
                return {
                    "type": "http.request",
                    "body": scope["_playgent_body"],
                    "more_body": False
                }
            return await receive()

        # Capture response and add HTTP data to endpoint event
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                # Response is starting, add HTTP request data to the endpoint event
                if state.endpoint_id:
                    # Update the endpoint event with HTTP request data
                    try:
                        # Get request details
                        method = scope["method"]
                        path = scope["path"]
                        query_string = scope.get("query_string", b"")
                        if query_string:
                            url = f"{path}?{query_string.decode()}"
                        else:
                            url = path

                        # Get body
                        body = None
                        if scope.get("_playgent_body"):
                            try:
                                body = scope["_playgent_body"].decode('utf-8')
                            except UnicodeDecodeError:
                                body = f"<binary data: {len(scope['_playgent_body'])} bytes>"

                        # Create HTTP request data
                        http_request_data = {
                            "method": method,
                            "url": url,
                            "headers": headers_dict,
                            "body": body
                        }

                        # Store in state for potential use
                        state.last_http_request = http_request_data

                        logger.debug(f"Captured HTTP request: {method} {url}")

                    except Exception as e:
                        logger.error(f"Error capturing HTTP request: {e}")

            await send(message)

        # Call the app with wrapped receive
        try:
            await self.app(scope, receive_wrapper if not scope.get("_playgent_body") else receive_replay, send_wrapper)
        finally:
            # Clean up context
            if context_token:
                state._trace_context.reset(context_token)
                logger.debug(f"PlaygentMiddleware: Cleaned up trace context after request to {scope['path']}")


# For backward compatibility with BaseHTTPMiddleware pattern
if BaseHTTPMiddleware:
    class PlaygentHTTPMiddleware(BaseHTTPMiddleware):
        """Alternative middleware using Starlette's BaseHTTPMiddleware

        This middleware captures HTTP request details and manages trace context
        based on X-Playgent-Trace-Id and X-Playgent-Test-Id headers.
        """

        async def dispatch(self, request: Request, call_next: Callable) -> Response:
            """Process the request and response"""
            logger.debug(f"=== PlaygentHTTPMiddleware.dispatch called for {request.url.path} ===")

            # Extract Playgent headers
            # Support both new trace headers and legacy trace headers
            trace_id = request.headers.get("X-Playgent-Trace-Id") or request.headers.get("X-Playgent-Session-Id")
            person_id = request.headers.get("X-Playgent-Person-Id")

            if trace_id or person_id:
                logger.debug(f"PlaygentHTTPMiddleware: Found headers - X-Playgent-Trace-Id={trace_id}, X-Playgent-Person-Id={person_id}")

            # Set trace context if headers present
            context_token = None
            if trace_id or person_id:
                # If only person_id provided, create a new trace
                if not trace_id:
                    try:
                        from .core import create_trace
                        trace_id = create_trace(person_id=person_id)
                        if trace_id:
                            logger.info(f"PlaygentHTTPMiddleware: Created trace {trace_id} for person {person_id}")
                        else:
                            logger.debug(f"PlaygentHTTPMiddleware: Failed to create trace for person {person_id}")
                    except Exception as e:
                        logger.debug(f"PlaygentHTTPMiddleware: Failed to create trace (silently handled): {e}")
                        trace_id = None

                if trace_id:
                    try:
                        context_data = state.TraceContextData(
                            trace_id=trace_id,
                            person_id=person_id
                        )
                        context_token = state._trace_context.set(context_data)
                        logger.debug(f"PlaygentHTTPMiddleware: Set trace context - trace_id={trace_id}, person_id={person_id}")
                    except Exception as e:
                        logger.debug(f"PlaygentHTTPMiddleware: Failed to set trace context (silently handled): {e}")
                        context_token = None

            # Capture request details for all requests
            http_request_data = None
            http_request_token = None

            try:
                # Read body (this consumes it)
                body_bytes = await request.body()
                logger.debug(f"Read {len(body_bytes)} bytes from request body")

                # Create HTTP request data - ensure headers are JSON-serializable
                http_request_data = {
                    "method": request.method,
                    "url": str(request.url),
                    "headers": {k: str(v) for k, v in request.headers.items()},
                    "body": body_bytes.decode('utf-8') if body_bytes else None
                }

                logger.debug(f"Captured HTTP request data: method={request.method}, url={request.url}")

                # Re-inject body so the endpoint can read it
                async def receive():
                    return {"type": "http.request", "body": body_bytes}

                # Create new request with the receive function
                request = Request(request.scope, receive)

                # Store HTTP data in context variable
                http_request_token = _http_request_context.set(http_request_data)

            except Exception as e:
                logger.error(f"Error capturing HTTP request: {e}")

            try:
                # Call the endpoint
                response = await call_next(request)
                return response
            finally:
                # Clean up context variables
                if http_request_token:
                    _http_request_context.reset(http_request_token)
                if context_token:
                    state._trace_context.reset(context_token)
                    logger.debug(f"PlaygentHTTPMiddleware: Cleaned up trace context after request")