"""
Safe wrapper functions for instrumenting LLM clients.

This module provides explicit wrapper functions that instrument LLM clients
without any global state modifications or monkey-patching. Each wrapped client
maintains its own configuration and can use different API keys.

Features:
1. No global side effects (no sys.meta_path or GC scanning)
2. Per-client API keys and server URLs
3. Type-safe with IDE autocomplete preserved
4. Explicit and predictable behavior
5. Thread-safe and production-ready

Usage:
    from openai import OpenAI
    import playgent

    # Simple usage with API key
    client = playgent.wrap_openai(
        OpenAI(),
        api_key="your-playgent-api-key"
    )

    # Multiple clients with different keys
    client1 = playgent.wrap_openai(OpenAI(), api_key="project-1-key")
    client2 = playgent.wrap_openai(OpenAI(), api_key="project-2-key")

    # Auto-detect from environment variables
    client = playgent.wrap_openai(OpenAI())  # Uses PLAYGENT_API_KEY
"""

import functools
import logging
import os
from dataclasses import dataclass
from typing import TypeVar, overload, Any, Optional, Union, TYPE_CHECKING
from types import MethodType

from opentelemetry import trace

from .cost_calculator import calculate_cost
from . import state

if TYPE_CHECKING:
    import openai
    from openai import OpenAI, AsyncOpenAI
    import anthropic
    from anthropic import Anthropic, AsyncAnthropic

logger = logging.getLogger(__name__)

T = TypeVar('T')

# Marker attributes
WRAPPED_MARKER = '_playgent_wrapped'
CONFIG_ATTR = '_playgent_config'


class WrapperError(Exception):
    """Raised when there's an issue with wrapping a client."""
    pass


@dataclass
class ClientConfig:
    """Per-client Playgent configuration."""
    api_key: Optional[str]
    server_url: str
    tracer: trace.Tracer
    provider: str  # 'openai' or 'anthropic'


def _get_api_key(api_key: Optional[str] = None) -> Optional[str]:
    """Get API key from parameter or environment variable."""
    if api_key:
        return api_key

    env_key = os.environ.get("PLAYGENT_API_KEY")
    if env_key:
        logger.debug("Using PLAYGENT_API_KEY from environment")
        return env_key

    return None


def _get_server_url(server_url: Optional[str] = None) -> str:
    """Get server URL from parameter, environment, or default."""
    if server_url:
        return server_url

    env_url = os.environ.get("PLAYGENT_SERVER_URL")
    if env_url:
        logger.debug("Using PLAYGENT_SERVER_URL from environment")
        return env_url

    # Default production URL
    return "https://run.blaxel.ai/pharmie-agents/agents/playgent"


def _get_client_config(obj: Any) -> Optional[ClientConfig]:
    """
    Get the Playgent configuration from a client or its parent.

    This walks up the object hierarchy to find the root client object
    that contains the configuration.
    """
    # Check if config is directly on the object
    if hasattr(obj, CONFIG_ATTR):
        return getattr(obj, CONFIG_ATTR)

    # Try to walk up to find the client
    # For OpenAI: completions -> chat -> client
    # For Anthropic: messages -> client
    for attr in ['_client', 'client', '__wrapped__']:
        if hasattr(obj, attr):
            parent = getattr(obj, attr)
            if hasattr(parent, CONFIG_ATTR):
                return getattr(parent, CONFIG_ATTR)
            # Try one more level up
            if hasattr(parent, '_client'):
                grandparent = getattr(parent, '_client')
                if hasattr(grandparent, CONFIG_ATTR):
                    return getattr(grandparent, CONFIG_ATTR)

    return None


# ============================================================================
# OpenAI Wrappers
# ============================================================================

@overload
def wrap_openai(
    client: "OpenAI",
    api_key: Optional[str] = None,
    server_url: Optional[str] = None
) -> "OpenAI": ...

@overload
def wrap_openai(
    client: "AsyncOpenAI",
    api_key: Optional[str] = None,
    server_url: Optional[str] = None
) -> "AsyncOpenAI": ...

def wrap_openai(
    client: T,
    api_key: Optional[str] = None,
    server_url: Optional[str] = None
) -> T:
    """
    Wrap an OpenAI client to automatically track API calls with Playgent.

    Each wrapped client maintains its own configuration, allowing multiple
    clients to use different API keys and server URLs simultaneously.

    Args:
        client: An OpenAI or AsyncOpenAI client instance
        api_key: Optional Playgent API key. If not provided, uses PLAYGENT_API_KEY
                environment variable. If neither is set, tracking is disabled.
        server_url: Optional Playgent server URL. If not provided, uses
                   PLAYGENT_SERVER_URL environment variable or defaults to production.

    Returns:
        The same client instance with instrumentation applied

    Raises:
        TypeError: If the client is not an OpenAI or AsyncOpenAI instance
        WrapperError: If the client is already wrapped

    Example:
        >>> from openai import OpenAI
        >>> import playgent
        >>>
        >>> # With explicit API key
        >>> client = playgent.wrap_openai(
        ...     OpenAI(),
        ...     api_key="your-playgent-api-key"
        ... )
        >>>
        >>> # Auto-detect from environment
        >>> # export PLAYGENT_API_KEY=your-key
        >>> client = playgent.wrap_openai(OpenAI())
        >>>
        >>> # Multiple clients with different keys
        >>> client1 = playgent.wrap_openai(OpenAI(), api_key="key1")
        >>> client2 = playgent.wrap_openai(OpenAI(), api_key="key2")
    """
    try:
        import openai
        from openai import OpenAI, AsyncOpenAI
    except ImportError:
        raise ImportError(
            "OpenAI library is not installed. "
            "Install it with: pip install openai"
        )

    # Check if already wrapped
    if hasattr(client, WRAPPED_MARKER):
        raise WrapperError(
            f"Client is already wrapped by Playgent. "
            f"Check for {WRAPPED_MARKER} attribute to avoid double-wrapping."
        )

    # Get configuration
    effective_api_key = _get_api_key(api_key)
    effective_server_url = _get_server_url(server_url)

    # Initialize Playgent if needed (this ensures the global tracer is set up)
    if effective_api_key:
        from . import state
        from .core import init
        # Only initialize if not already done
        if not state.api_key:
            init(api_key=effective_api_key, server_url=effective_server_url, auto_patch=False)

    # Use the global Playgent tracer (not a client-specific one)
    from .spans import get_tracer
    tracer = get_tracer()

    # Store configuration on the client
    config = ClientConfig(
        api_key=effective_api_key,
        server_url=effective_server_url,
        tracer=tracer,
        provider='openai'
    )
    setattr(client, CONFIG_ATTR, config)

    # Log configuration status
    if not effective_api_key:
        logger.warning(
            "No Playgent API key provided. Tracking is disabled. "
            "Provide api_key parameter or set PLAYGENT_API_KEY environment variable."
        )
    else:
        logger.debug(f"OpenAI client wrapped with Playgent tracking to {effective_server_url}")

    # Determine client type and wrap accordingly
    if isinstance(client, AsyncOpenAI):
        _wrap_async_openai_client(client)
    elif isinstance(client, OpenAI):
        _wrap_sync_openai_client(client)
    else:
        raise TypeError(
            f"Expected OpenAI or AsyncOpenAI client, got {type(client).__name__}. "
            f"Make sure you're passing an initialized client instance."
        )

    # Mark as wrapped
    setattr(client, WRAPPED_MARKER, True)

    return client


def _wrap_sync_openai_client(client: "OpenAI") -> None:
    """
    Apply instrumentation to a synchronous OpenAI client.

    This wraps individual methods on the client instance, not the class.
    """
    # Store reference to client on nested objects for config lookup
    if hasattr(client, 'chat'):
        client.chat._client = client
        if hasattr(client.chat, 'completions'):
            client.chat.completions._client = client

    # Wrap chat completions
    if hasattr(client, 'chat') and hasattr(client.chat, 'completions'):
        original_create = client.chat.completions.create
        client.chat.completions.create = MethodType(
            _make_openai_chat_wrapper(original_create),
            client.chat.completions
        )

    # Wrap responses.create (the new unified API)
    if hasattr(client, 'responses'):
        client.responses._client = client
        original_create = client.responses.create
        client.responses.create = MethodType(
            _make_openai_chat_wrapper(original_create),  # Use same wrapper, it handles both
            client.responses
        )

    # Wrap embeddings
    if hasattr(client, 'embeddings'):
        client.embeddings._client = client
        original_create = client.embeddings.create
        client.embeddings.create = MethodType(
            _make_openai_embeddings_wrapper(original_create),
            client.embeddings
        )

    # Wrap images
    if hasattr(client, 'images'):
        client.images._client = client
        if hasattr(client.images, 'generate'):
            original_generate = client.images.generate
            client.images.generate = MethodType(
                _make_openai_images_wrapper(original_generate),
                client.images
            )


def _wrap_async_openai_client(client: "AsyncOpenAI") -> None:
    """
    Apply instrumentation to an asynchronous OpenAI client.

    This wraps individual methods on the client instance, not the class.
    """
    # Store reference to client on nested objects for config lookup
    if hasattr(client, 'chat'):
        client.chat._client = client
        if hasattr(client.chat, 'completions'):
            client.chat.completions._client = client

    # Wrap chat completions
    if hasattr(client, 'chat') and hasattr(client.chat, 'completions'):
        original_create = client.chat.completions.create
        client.chat.completions.create = MethodType(
            _make_openai_async_chat_wrapper(original_create),
            client.chat.completions
        )

    # Wrap responses.create (the new unified API)
    if hasattr(client, 'responses'):
        client.responses._client = client
        original_create = client.responses.create
        client.responses.create = MethodType(
            _make_openai_async_chat_wrapper(original_create),  # Use same wrapper, it handles both
            client.responses
        )

    # Wrap embeddings
    if hasattr(client, 'embeddings'):
        client.embeddings._client = client
        original_create = client.embeddings.create
        client.embeddings.create = MethodType(
            _make_openai_async_embeddings_wrapper(original_create),
            client.embeddings
        )

    # Wrap images
    if hasattr(client, 'images'):
        client.images._client = client
        if hasattr(client.images, 'generate'):
            original_generate = client.images.generate
            client.images.generate = MethodType(
                _make_openai_async_images_wrapper(original_generate),
                client.images
            )


def _make_openai_chat_wrapper(original_method):
    """Create a wrapper for OpenAI chat.completions.create method."""
    @functools.wraps(original_method)
    def wrapper(self, *args, **kwargs):
        # Debug logging
        logger.debug(f"OpenAI wrapper called for {original_method.__name__}")

        # Get client configuration
        config = _get_client_config(self)

        # Skip instrumentation if no config or no API key
        if not config or not config.api_key:
            logger.debug("No config or API key, skipping instrumentation")
            return original_method(*args, **kwargs)

        # Get tracer from client config
        tracer = config.tracer

        # Import json for serialization
        import json

        logger.debug("Starting generation span...")
        # Start span using OpenTelemetry
        with tracer.start_as_current_span("generation") as span:
            # Set span attributes
            span.set_attribute("span.kind", "generation")
            span.set_attribute("provider", "openai")

            # Add session_id and person_id from context
            context = state._trace_context.get()
            if context:
                if context.session_id:
                    span.set_attribute("session_id", context.session_id)
                if context.person_id:
                    span.set_attribute("person_id", context.person_id)

            # Extract model and inputs/messages from kwargs
            model = kwargs.get('model', 'gpt-4')

            # Handle both messages (chat.completions) and input (responses.create)
            input_data = kwargs.get('input') or kwargs.get('messages', [])

            # Set model attribute
            span.set_attribute("model", model)

            # Set inputs - convert Pydantic models to dicts for proper serialization
            try:
                if isinstance(input_data, list):
                    # Convert any Pydantic models in the list
                    serializable_input = []
                    for item in input_data:
                        if hasattr(item, 'model_dump'):
                            serializable_input.append(item.model_dump())
                        elif isinstance(item, dict):
                            serializable_input.append(item)
                        else:
                            serializable_input.append(str(item))
                    span.set_attribute("inputs", json.dumps(serializable_input))
                else:
                    span.set_attribute("inputs", json.dumps(input_data))
            except (TypeError, ValueError):
                # If still not JSON serializable, just use string representation
                span.set_attribute("inputs", str(input_data))

            try:
                # Call original method
                response = original_method(*args, **kwargs)

                # Calculate cost and set token usage attributes
                if hasattr(response, 'usage') and response.usage:
                    model = kwargs.get('model', 'unknown')

                    # Handle different usage formats
                    if hasattr(response.usage, 'prompt_tokens'):
                        # Chat completion format
                        input_tokens = response.usage.prompt_tokens
                        output_tokens = response.usage.completion_tokens
                        total_tokens = response.usage.total_tokens
                    elif hasattr(response.usage, 'input_tokens'):
                        # Responses API format
                        input_tokens = response.usage.input_tokens
                        output_tokens = response.usage.output_tokens
                        total_tokens = getattr(response.usage, 'total_tokens', input_tokens + output_tokens)
                    else:
                        # Unknown format, skip
                        input_tokens = output_tokens = total_tokens = None

                    if input_tokens is not None:
                        span.set_attribute("token_usage.input", input_tokens)
                        span.set_attribute("token_usage.output", output_tokens)
                        span.set_attribute("token_usage.total", total_tokens)

                        # Create token_usage dict for calculate_cost
                        token_usage = {
                            "input": input_tokens,
                            "output": output_tokens,
                            "total": total_tokens
                        }

                        cost = calculate_cost(
                            provider='openai',
                            model=model,
                            token_usage=token_usage
                        )
                        if cost is not None:
                            span.set_attribute("cost_usd", cost)

                # Set outputs as list of {type, content} objects for frontend
                outputs = []

                # Handle different response types
                if hasattr(response, 'choices') and response.choices:
                    # Chat completion response
                    for choice in response.choices:
                        if hasattr(choice, 'message') and choice.message:
                            message = choice.message

                            # Add message content
                            if message.content:
                                outputs.append({
                                    "type": "message",
                                    "content": message.content
                                })

                            # Add function calls if present
                            if hasattr(message, 'tool_calls') and message.tool_calls:
                                for tool_call in message.tool_calls:
                                    if hasattr(tool_call, 'function'):
                                        outputs.append({
                                            "type": "function_call",
                                            "name": tool_call.function.name,
                                            "content": tool_call.function.arguments
                                        })

                elif hasattr(response, 'output'):
                    # Responses API format - handle output array of ResponseOutputMessage objects
                    if isinstance(response.output, list):
                        for item in response.output:
                            # item is a ResponseOutputMessage with type and content
                            if hasattr(item, 'type'):
                                # Get the type (e.g., "message", "function_call", "reasoning", etc.)
                                item_type = str(item.type) if not isinstance(item.type, str) else item.type

                                # Extract the actual content
                                if hasattr(item, 'content') and isinstance(item.content, list):
                                    # Content is a list of ResponseOutputText objects
                                    # Concatenate all text parts
                                    text_parts = []
                                    for content_item in item.content:
                                        if hasattr(content_item, 'text'):
                                            text_parts.append(content_item.text)
                                    content = ' '.join(text_parts) if text_parts else str(item.content)
                                elif hasattr(item, 'content'):
                                    content = str(item.content)
                                else:
                                    content = str(item)

                                output_obj = {
                                    "type": item_type,
                                    "content": content
                                }

                                # Add name for function calls
                                if hasattr(item, 'name'):
                                    output_obj["name"] = str(item.name)

                                outputs.append(output_obj)
                            else:
                                # Fallback - shouldn't happen with proper response structure
                                outputs.append({
                                    "type": "message",
                                    "content": str(item)
                                })
                    else:
                        # Single output, treat as message
                        outputs.append({
                            "type": "message",
                            "content": str(response.output)
                        })

                elif hasattr(response, 'output_text'):
                    # Simple text output
                    outputs.append({
                        "type": "message",
                        "content": response.output_text
                    })

                # Fallback if no recognized format
                if not outputs:
                    outputs.append({
                        "type": "message",
                        "content": str(response)
                    })

                span.set_attribute("outputs", json.dumps(outputs))

                return response

            except Exception as e:
                # Record exception and set error attributes
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                span.set_attribute("error", True)
                span.set_attribute("error.type", type(e).__name__)
                span.set_attribute("error.message", str(e))
                raise

    return wrapper


def _make_openai_async_chat_wrapper(original_method):
    """Create a wrapper for async OpenAI chat.completions.create method."""
    @functools.wraps(original_method)
    async def wrapper(self, *args, **kwargs):
        # Get client configuration
        config = _get_client_config(self)

        # Skip instrumentation if no config or no API key
        if not config or not config.api_key:
            return await original_method(*args, **kwargs)

        # Get tracer from client config
        tracer = config.tracer

        # Start span using OpenTelemetry
        with tracer.start_as_current_span("generation") as span:
            # Import json for serialization
            import json

            # Set span attributes
            span.set_attribute("span.kind", "generation")
            span.set_attribute("provider", "openai")

            # Add session_id and person_id from context
            context = state._trace_context.get()
            if context:
                if context.session_id:
                    span.set_attribute("session_id", context.session_id)
                if context.person_id:
                    span.set_attribute("person_id", context.person_id)

            # Extract model and inputs/messages from kwargs
            model = kwargs.get('model', 'gpt-4')

            # Handle both messages (chat.completions) and input (responses.create)
            input_data = kwargs.get('input') or kwargs.get('messages', [])

            # Set model attribute
            span.set_attribute("model", model)

            # Set inputs - convert Pydantic models to dicts for proper serialization
            try:
                if isinstance(input_data, list):
                    # Convert any Pydantic models in the list
                    serializable_input = []
                    for item in input_data:
                        if hasattr(item, 'model_dump'):
                            serializable_input.append(item.model_dump())
                        elif isinstance(item, dict):
                            serializable_input.append(item)
                        else:
                            serializable_input.append(str(item))
                    span.set_attribute("inputs", json.dumps(serializable_input))
                else:
                    span.set_attribute("inputs", json.dumps(input_data))
            except (TypeError, ValueError):
                # If still not JSON serializable, just use string representation
                span.set_attribute("inputs", str(input_data))

            try:
                # Call original method
                response = await original_method(*args, **kwargs)

                # Calculate cost and set token usage attributes
                if hasattr(response, 'usage') and response.usage:
                    model = kwargs.get('model', 'unknown')

                    # Handle different usage formats
                    if hasattr(response.usage, 'prompt_tokens'):
                        # Chat completion format
                        input_tokens = response.usage.prompt_tokens
                        output_tokens = response.usage.completion_tokens
                        total_tokens = response.usage.total_tokens
                    elif hasattr(response.usage, 'input_tokens'):
                        # Responses API format
                        input_tokens = response.usage.input_tokens
                        output_tokens = response.usage.output_tokens
                        total_tokens = getattr(response.usage, 'total_tokens', input_tokens + output_tokens)
                    else:
                        # Unknown format, skip
                        input_tokens = output_tokens = total_tokens = None

                    if input_tokens is not None:
                        span.set_attribute("token_usage.input", input_tokens)
                        span.set_attribute("token_usage.output", output_tokens)
                        span.set_attribute("token_usage.total", total_tokens)

                        # Create token_usage dict for calculate_cost
                        token_usage = {
                            "input": input_tokens,
                            "output": output_tokens,
                            "total": total_tokens
                        }

                        cost = calculate_cost(
                            provider='openai',
                            model=model,
                            token_usage=token_usage
                        )
                        if cost is not None:
                            span.set_attribute("cost_usd", cost)

                # Set outputs as list of {type, content} objects for frontend
                outputs = []

                # Handle different response types
                if hasattr(response, 'choices') and response.choices:
                    # Chat completion response
                    for choice in response.choices:
                        if hasattr(choice, 'message') and choice.message:
                            message = choice.message

                            # Add message content
                            if message.content:
                                outputs.append({
                                    "type": "message",
                                    "content": message.content
                                })

                            # Add function calls if present
                            if hasattr(message, 'tool_calls') and message.tool_calls:
                                for tool_call in message.tool_calls:
                                    if hasattr(tool_call, 'function'):
                                        outputs.append({
                                            "type": "function_call",
                                            "name": tool_call.function.name,
                                            "content": tool_call.function.arguments
                                        })

                elif hasattr(response, 'output'):
                    # Responses API format - handle output array of ResponseOutputMessage objects
                    if isinstance(response.output, list):
                        for item in response.output:
                            # item is a ResponseOutputMessage with type and content
                            if hasattr(item, 'type'):
                                # Get the type (e.g., "message", "function_call", "reasoning", etc.)
                                item_type = str(item.type) if not isinstance(item.type, str) else item.type

                                # Extract the actual content
                                if hasattr(item, 'content') and isinstance(item.content, list):
                                    # Content is a list of ResponseOutputText objects
                                    # Concatenate all text parts
                                    text_parts = []
                                    for content_item in item.content:
                                        if hasattr(content_item, 'text'):
                                            text_parts.append(content_item.text)
                                    content = ' '.join(text_parts) if text_parts else str(item.content)
                                elif hasattr(item, 'content'):
                                    content = str(item.content)
                                else:
                                    content = str(item)

                                output_obj = {
                                    "type": item_type,
                                    "content": content
                                }

                                # Add name for function calls
                                if hasattr(item, 'name'):
                                    output_obj["name"] = str(item.name)

                                outputs.append(output_obj)
                            else:
                                # Fallback - shouldn't happen with proper response structure
                                outputs.append({
                                    "type": "message",
                                    "content": str(item)
                                })
                    else:
                        # Single output, treat as message
                        outputs.append({
                            "type": "message",
                            "content": str(response.output)
                        })

                elif hasattr(response, 'output_text'):
                    # Simple text output
                    outputs.append({
                        "type": "message",
                        "content": response.output_text
                    })

                # Fallback if no recognized format
                if not outputs:
                    outputs.append({
                        "type": "message",
                        "content": str(response)
                    })

                span.set_attribute("outputs", json.dumps(outputs))

                return response

            except Exception as e:
                # Record exception and set error attributes
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                span.set_attribute("error", True)
                span.set_attribute("error.type", type(e).__name__)
                span.set_attribute("error.message", str(e))
                raise

    return wrapper


def _make_openai_embeddings_wrapper(original_method):
    """Create a wrapper for OpenAI embeddings.create method."""
    @functools.wraps(original_method)
    def wrapper(self, *args, **kwargs):
        config = _get_client_config(self)
        if not config or not config.api_key:
            return original_method(*args, **kwargs)

        tracer = config.tracer

        with tracer.start_as_current_span("embeddings") as span:
            span.set_attribute("span.kind", "embeddings")
            span.set_attribute("provider", "openai")
            span.set_attribute("inputs", str(kwargs))

            # Add session_id and person_id from context
            context = state._trace_context.get()
            if context:
                if context.session_id:
                    span.set_attribute("session_id", context.session_id)
                if context.person_id:
                    span.set_attribute("person_id", context.person_id)

            try:
                response = original_method(*args, **kwargs)
                span.set_attribute("outputs", str(response))
                return response
            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                raise

    return wrapper


def _make_openai_async_embeddings_wrapper(original_method):
    """Create a wrapper for async OpenAI embeddings.create method."""
    @functools.wraps(original_method)
    async def wrapper(self, *args, **kwargs):
        config = _get_client_config(self)
        if not config or not config.api_key:
            return await original_method(*args, **kwargs)

        tracer = config.tracer

        with tracer.start_as_current_span("embeddings") as span:
            span.set_attribute("span.kind", "embeddings")
            span.set_attribute("provider", "openai")
            span.set_attribute("inputs", str(kwargs))

            # Add session_id and person_id from context
            context = state._trace_context.get()
            if context:
                if context.session_id:
                    span.set_attribute("session_id", context.session_id)
                if context.person_id:
                    span.set_attribute("person_id", context.person_id)

            try:
                response = await original_method(*args, **kwargs)
                span.set_attribute("outputs", str(response))
                return response
            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                raise

    return wrapper


def _make_openai_images_wrapper(original_method):
    """Create a wrapper for OpenAI images.generate method."""
    @functools.wraps(original_method)
    def wrapper(self, *args, **kwargs):
        config = _get_client_config(self)
        if not config or not config.api_key:
            return original_method(*args, **kwargs)

        tracer = config.tracer

        with tracer.start_as_current_span("images") as span:
            span.set_attribute("span.kind", "images")
            span.set_attribute("provider", "openai")
            span.set_attribute("inputs", str(kwargs))

            # Add session_id and person_id from context
            context = state._trace_context.get()
            if context:
                if context.session_id:
                    span.set_attribute("session_id", context.session_id)
                if context.person_id:
                    span.set_attribute("person_id", context.person_id)

            try:
                response = original_method(*args, **kwargs)
                span.set_attribute("outputs", str(response))
                return response
            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                raise

    return wrapper


def _make_openai_async_images_wrapper(original_method):
    """Create a wrapper for async OpenAI images.generate method."""
    @functools.wraps(original_method)
    async def wrapper(self, *args, **kwargs):
        config = _get_client_config(self)
        if not config or not config.api_key:
            return await original_method(*args, **kwargs)

        tracer = config.tracer

        with tracer.start_as_current_span("images") as span:
            span.set_attribute("span.kind", "images")
            span.set_attribute("provider", "openai")
            span.set_attribute("inputs", str(kwargs))

            # Add session_id and person_id from context
            context = state._trace_context.get()
            if context:
                if context.session_id:
                    span.set_attribute("session_id", context.session_id)
                if context.person_id:
                    span.set_attribute("person_id", context.person_id)

            try:
                response = await original_method(*args, **kwargs)
                span.set_attribute("outputs", str(response))
                return response
            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                raise

    return wrapper


# ============================================================================
# Anthropic Wrappers
# ============================================================================

@overload
def wrap_anthropic(
    client: "Anthropic",
    api_key: Optional[str] = None,
    server_url: Optional[str] = None
) -> "Anthropic": ...

@overload
def wrap_anthropic(
    client: "AsyncAnthropic",
    api_key: Optional[str] = None,
    server_url: Optional[str] = None
) -> "AsyncAnthropic": ...

def wrap_anthropic(
    client: T,
    api_key: Optional[str] = None,
    server_url: Optional[str] = None
) -> T:
    """
    Wrap an Anthropic client to automatically track API calls with Playgent.

    Each wrapped client maintains its own configuration, allowing multiple
    clients to use different API keys and server URLs simultaneously.

    Args:
        client: An Anthropic or AsyncAnthropic client instance
        api_key: Optional Playgent API key. If not provided, uses PLAYGENT_API_KEY
                environment variable. If neither is set, tracking is disabled.
        server_url: Optional Playgent server URL. If not provided, uses
                   PLAYGENT_SERVER_URL environment variable or defaults to production.

    Returns:
        The same client instance with instrumentation applied

    Raises:
        TypeError: If the client is not an Anthropic or AsyncAnthropic instance
        WrapperError: If the client is already wrapped

    Example:
        >>> from anthropic import Anthropic
        >>> import playgent
        >>>
        >>> # With explicit API key
        >>> client = playgent.wrap_anthropic(
        ...     Anthropic(),
        ...     api_key="your-playgent-api-key"
        ... )
        >>>
        >>> # Auto-detect from environment
        >>> # export PLAYGENT_API_KEY=your-key
        >>> client = playgent.wrap_anthropic(Anthropic())
        >>>
        >>> # Multiple clients with different keys
        >>> client1 = playgent.wrap_anthropic(Anthropic(), api_key="key1")
        >>> client2 = playgent.wrap_anthropic(Anthropic(), api_key="key2")
    """
    try:
        import anthropic
        from anthropic import Anthropic, AsyncAnthropic
    except ImportError:
        raise ImportError(
            "Anthropic library is not installed. "
            "Install it with: pip install anthropic"
        )

    # Check if already wrapped
    if hasattr(client, WRAPPED_MARKER):
        raise WrapperError(
            f"Client is already wrapped by Playgent. "
            f"Check for {WRAPPED_MARKER} attribute to avoid double-wrapping."
        )

    # Get configuration
    effective_api_key = _get_api_key(api_key)
    effective_server_url = _get_server_url(server_url)

    # Initialize Playgent if needed (this ensures the global tracer is set up)
    if effective_api_key:
        from . import state
        from .core import init
        # Only initialize if not already done
        if not state.api_key:
            init(api_key=effective_api_key, server_url=effective_server_url, auto_patch=False)

    # Use the global Playgent tracer (not a client-specific one)
    from .spans import get_tracer
    tracer = get_tracer()

    # Store configuration on the client
    config = ClientConfig(
        api_key=effective_api_key,
        server_url=effective_server_url,
        tracer=tracer,
        provider='anthropic'
    )
    setattr(client, CONFIG_ATTR, config)

    # Log configuration status
    if not effective_api_key:
        logger.warning(
            "No Playgent API key provided. Tracking is disabled. "
            "Provide api_key parameter or set PLAYGENT_API_KEY environment variable."
        )
    else:
        logger.debug(f"Anthropic client wrapped with Playgent tracking to {effective_server_url}")

    # Determine client type and wrap accordingly
    if isinstance(client, AsyncAnthropic):
        _wrap_async_anthropic_client(client)
    elif isinstance(client, Anthropic):
        _wrap_sync_anthropic_client(client)
    else:
        raise TypeError(
            f"Expected Anthropic or AsyncAnthropic client, got {type(client).__name__}. "
            f"Make sure you're passing an initialized client instance."
        )

    # Mark as wrapped
    setattr(client, WRAPPED_MARKER, True)

    return client


def _wrap_sync_anthropic_client(client: "Anthropic") -> None:
    """
    Apply instrumentation to a synchronous Anthropic client.

    This wraps individual methods on the client instance, not the class.
    """
    # Store reference to client on nested objects for config lookup
    if hasattr(client, 'messages'):
        client.messages._client = client

    # Wrap messages.create
    if hasattr(client, 'messages'):
        original_create = client.messages.create
        client.messages.create = MethodType(
            _make_anthropic_messages_wrapper(original_create),
            client.messages
        )

    # Wrap completions if they exist (for older API versions)
    if hasattr(client, 'completions'):
        client.completions._client = client
        original_create = client.completions.create
        client.completions.create = MethodType(
            _make_anthropic_completions_wrapper(original_create),
            client.completions
        )


def _wrap_async_anthropic_client(client: "AsyncAnthropic") -> None:
    """
    Apply instrumentation to an asynchronous Anthropic client.

    This wraps individual methods on the client instance, not the class.
    """
    # Store reference to client on nested objects for config lookup
    if hasattr(client, 'messages'):
        client.messages._client = client

    # Wrap messages.create
    if hasattr(client, 'messages'):
        original_create = client.messages.create
        client.messages.create = MethodType(
            _make_anthropic_async_messages_wrapper(original_create),
            client.messages
        )

    # Wrap completions if they exist (for older API versions)
    if hasattr(client, 'completions'):
        client.completions._client = client
        original_create = client.completions.create
        client.completions.create = MethodType(
            _make_anthropic_async_completions_wrapper(original_create),
            client.completions
        )


def _make_anthropic_messages_wrapper(original_method):
    """Create a wrapper for Anthropic messages.create method."""
    @functools.wraps(original_method)
    def wrapper(self, *args, **kwargs):
        config = _get_client_config(self)
        if not config or not config.api_key:
            return original_method(*args, **kwargs)

        tracer = config.tracer

        with tracer.start_as_current_span("generation") as span:
            span.set_attribute("span.kind", "generation")
            span.set_attribute("provider", "anthropic")
            span.set_attribute("model", kwargs.get('model', 'unknown'))
            span.set_attribute("inputs", str(kwargs))

            # Add session_id and person_id from context
            context = state._trace_context.get()
            if context:
                if context.session_id:
                    span.set_attribute("session_id", context.session_id)
                if context.person_id:
                    span.set_attribute("person_id", context.person_id)

            try:
                response = original_method(*args, **kwargs)

                # Set token usage and cost attributes
                if hasattr(response, 'usage'):
                    model = kwargs.get('model', 'unknown')
                    span.set_attribute("token_usage.input", response.usage.input_tokens)
                    span.set_attribute("token_usage.output", response.usage.output_tokens)

                    cost = calculate_cost(
                        provider='anthropic',
                        model=model,
                        input_tokens=response.usage.input_tokens,
                        output_tokens=response.usage.output_tokens
                    )
                    if cost is not None:
                        span.set_attribute("cost_usd", cost)

                span.set_attribute("outputs", str(response))
                return response

            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                raise

    return wrapper


def _make_anthropic_async_messages_wrapper(original_method):
    """Create a wrapper for async Anthropic messages.create method."""
    @functools.wraps(original_method)
    async def wrapper(self, *args, **kwargs):
        config = _get_client_config(self)
        if not config or not config.api_key:
            return await original_method(*args, **kwargs)

        tracer = config.tracer

        with tracer.start_as_current_span("generation") as span:
            span.set_attribute("span.kind", "generation")
            span.set_attribute("provider", "anthropic")
            span.set_attribute("model", kwargs.get('model', 'unknown'))
            span.set_attribute("inputs", str(kwargs))

            # Add session_id and person_id from context
            context = state._trace_context.get()
            if context:
                if context.session_id:
                    span.set_attribute("session_id", context.session_id)
                if context.person_id:
                    span.set_attribute("person_id", context.person_id)

            try:
                response = await original_method(*args, **kwargs)

                # Set token usage and cost attributes
                if hasattr(response, 'usage'):
                    model = kwargs.get('model', 'unknown')
                    span.set_attribute("token_usage.input", response.usage.input_tokens)
                    span.set_attribute("token_usage.output", response.usage.output_tokens)

                    cost = calculate_cost(
                        provider='anthropic',
                        model=model,
                        input_tokens=response.usage.input_tokens,
                        output_tokens=response.usage.output_tokens
                    )
                    if cost is not None:
                        span.set_attribute("cost_usd", cost)

                span.set_attribute("outputs", str(response))
                return response

            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                raise

    return wrapper


def _make_anthropic_completions_wrapper(original_method):
    """Create a wrapper for Anthropic completions.create method (legacy)."""
    @functools.wraps(original_method)
    def wrapper(self, *args, **kwargs):
        config = _get_client_config(self)
        if not config or not config.api_key:
            return original_method(*args, **kwargs)

        tracer = config.tracer

        with tracer.start_as_current_span("completions") as span:
            span.set_attribute("span.kind", "completions")
            span.set_attribute("provider", "anthropic")
            span.set_attribute("inputs", str(kwargs))

            # Add session_id and person_id from context
            context = state._trace_context.get()
            if context:
                if context.session_id:
                    span.set_attribute("session_id", context.session_id)
                if context.person_id:
                    span.set_attribute("person_id", context.person_id)

            try:
                response = original_method(*args, **kwargs)
                span.set_attribute("outputs", str(response))
                return response
            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                raise

    return wrapper


def _make_anthropic_async_completions_wrapper(original_method):
    """Create a wrapper for async Anthropic completions.create method (legacy)."""
    @functools.wraps(original_method)
    async def wrapper(self, *args, **kwargs):
        config = _get_client_config(self)
        if not config or not config.api_key:
            return await original_method(*args, **kwargs)

        tracer = config.tracer

        with tracer.start_as_current_span("completions") as span:
            span.set_attribute("span.kind", "completions")
            span.set_attribute("provider", "anthropic")
            span.set_attribute("inputs", str(kwargs))

            # Add session_id and person_id from context
            context = state._trace_context.get()
            if context:
                if context.session_id:
                    span.set_attribute("session_id", context.session_id)
                if context.person_id:
                    span.set_attribute("person_id", context.person_id)

            try:
                response = await original_method(*args, **kwargs)
                span.set_attribute("outputs", str(response))
                return response
            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                raise

    return wrapper


# ============================================================================
# Utility Functions
# ============================================================================

def unwrap_openai(client: T) -> T:
    """
    Remove Playgent instrumentation from an OpenAI client.

    Args:
        client: A wrapped OpenAI or AsyncOpenAI client

    Returns:
        The same client with instrumentation removed

    Raises:
        WrapperError: If the client is not wrapped

    Example:
        >>> client = playgent.wrap_openai(OpenAI())
        >>> # ... use wrapped client ...
        >>> client = playgent.unwrap_openai(client)
        >>> # Client is now back to original state
    """
    if not hasattr(client, WRAPPED_MARKER):
        raise WrapperError("Client is not wrapped by Playgent")

    # Remove markers and config
    delattr(client, WRAPPED_MARKER)
    if hasattr(client, CONFIG_ATTR):
        delattr(client, CONFIG_ATTR)

    logger.warning(
        "Unwrapping removes markers but doesn't restore original methods. "
        "Consider creating a new client instance for a completely clean client."
    )

    return client


def unwrap_anthropic(client: T) -> T:
    """
    Remove Playgent instrumentation from an Anthropic client.

    Args:
        client: A wrapped Anthropic or AsyncAnthropic client

    Returns:
        The same client with instrumentation removed

    Raises:
        WrapperError: If the client is not wrapped

    Example:
        >>> client = playgent.wrap_anthropic(Anthropic())
        >>> # ... use wrapped client ...
        >>> client = playgent.unwrap_anthropic(client)
        >>> # Client is now back to original state
    """
    if not hasattr(client, WRAPPED_MARKER):
        raise WrapperError("Client is not wrapped by Playgent")

    # Remove markers and config
    delattr(client, WRAPPED_MARKER)
    if hasattr(client, CONFIG_ATTR):
        delattr(client, CONFIG_ATTR)

    logger.warning(
        "Unwrapping removes markers but doesn't restore original methods. "
        "Consider creating a new client instance for a completely clean client."
    )

    return client


def is_wrapped(client: Any) -> bool:
    """
    Check if a client is wrapped by Playgent.

    Args:
        client: Any client instance

    Returns:
        True if the client is wrapped, False otherwise

    Example:
        >>> client = OpenAI()
        >>> playgent.is_wrapped(client)
        False
        >>> client = playgent.wrap_openai(client)
        >>> playgent.is_wrapped(client)
        True
    """
    return hasattr(client, WRAPPED_MARKER)