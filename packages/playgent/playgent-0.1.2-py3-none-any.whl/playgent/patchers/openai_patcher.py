"""OpenAI library patcher with event-style span emission."""

import functools
import logging
import sys
import gc
import uuid
import json
from typing import Any, Dict, Optional
from .base import Patcher
from .. import state, core
from ..types import serialize_to_dict
from ..cost_calculator import extract_token_usage, calculate_cost

logger = logging.getLogger(__name__)


class OpenAIPatcher(Patcher):
    """Improved patcher for OpenAI that handles existing instances."""

    def attempt_patch(self) -> bool:
        """Patch OpenAI at multiple levels to handle all scenarios."""
        try:
            import openai

            # Strategy 1: Patch the class __init__ for new instances
            if hasattr(openai, 'OpenAI'):
                self._patch_client_class(openai.OpenAI)

            if hasattr(openai, 'AsyncOpenAI'):
                self._patch_async_client_class(openai.AsyncOpenAI)

            # Strategy 2: Patch at the module/class method level
            # This ensures even existing instances use patched methods
            self._patch_at_class_level()

            # Strategy 3: Find and patch existing instances in memory
            self._patch_existing_instances()

            self.is_patched = True
            return True

        except Exception as e:
            print(f"Failed to patch OpenAI: {e}")
            return False

    def _patch_at_class_level(self):
        """Patch methods at the class level so all instances (new and existing) are affected."""
        import openai

        # Patch the Completions class methods directly
        try:
            from openai.resources.chat.completions import Completions
            if hasattr(Completions, 'create'):
                original = Completions.create
                Completions.create = self._wrap_chat_completions_create_universal(original)
                self._store_original('Completions.create', original)
        except ImportError:
            pass

        # Patch async completions
        try:
            from openai.resources.chat.completions import AsyncCompletions
            if hasattr(AsyncCompletions, 'create'):
                original = AsyncCompletions.create
                AsyncCompletions.create = self._wrap_async_chat_completions_create_universal(original)
                self._store_original('AsyncCompletions.create', original)
        except ImportError:
            pass

        # Patch regular completions (older API)
        try:
            from openai.resources.completions import Completions as RegularCompletions
            if hasattr(RegularCompletions, 'create'):
                original = RegularCompletions.create
                RegularCompletions.create = self._wrap_completions_create_universal(original)
                self._store_original('RegularCompletions.create', original)
        except ImportError:
            pass

        # Patch responses API if it exists
        try:
            from openai.resources.responses import Responses
            if hasattr(Responses, 'create'):
                original = Responses.create
                Responses.create = self._wrap_responses_create_universal(original)
                self._store_original('Responses.create', original)
        except (ImportError, AttributeError):
            pass

    def _patch_existing_instances(self):
        """Find and patch any existing OpenAI client instances in memory."""
        import openai

        # Use garbage collector to find all instances
        for obj in gc.get_objects():
            try:
                # Check if it's an OpenAI client instance
                if isinstance(obj, openai.OpenAI) or (hasattr(openai, 'AsyncOpenAI') and isinstance(obj, openai.AsyncOpenAI)):
                    # The methods are already patched at class level,
                    # but we can do additional instance-specific patching if needed
                    pass
            except:
                # Some objects might not be accessible
                continue

    def _wrap_chat_completions_create_universal(self, original_method):
        """Universal wrapper that works for both bound and unbound methods."""
        @functools.wraps(original_method)
        def wrapper(*args, **kwargs):
            # Only track if Playgent is running
            if not state.is_running:
                return original_method(*args, **kwargs)

            # Wrap ALL tracking code in try-except to ensure user's API calls never fail due to observability
            try:
                from ..spans import get_tracer
                from opentelemetry.trace import StatusCode

                messages = kwargs.get("messages", [])
                model = kwargs.get("model", "")

                # Get OpenTelemetry tracer
                tracer = get_tracer()

                # Create single generation span for entire API call
                with tracer.start_as_current_span("generation") as span:
                    # Mark as Playgent-created span (for filtering)

                    # Set span kind
                    span.set_attribute("span.kind", "generation")

                    # Set input attributes (serialize to JSON string for OTel compatibility)
                    import json
                    span.set_attribute("inputs", json.dumps(serialize_to_dict(messages)))
                    span.set_attribute("model", model)

                    if kwargs.get("temperature") is not None:
                        span.set_attribute("temperature", kwargs.get("temperature"))
                    if kwargs.get("max_tokens") is not None:
                        span.set_attribute("max_tokens", kwargs.get("max_tokens"))

                    # Set session_id and person_id if available from context
                    context = state._trace_context.get()
                    if context:
                        if context.session_id:
                            span.set_attribute("session_id", context.session_id)
                        if context.person_id:
                            span.set_attribute("person_id", context.person_id)
                    elif state.person_id:
                        span.set_attribute("person_id", state.person_id)

                    # Call original method
                    response = original_method(*args, **kwargs)

                    # Extract token usage and calculate cost
                    token_usage = extract_token_usage(response, "openai")
                    if token_usage:
                        span.set_attribute("token_usage.input", token_usage.get("input", 0))
                        span.set_attribute("token_usage.output", token_usage.get("output", 0))
                        span.set_attribute("token_usage.total", token_usage.get("total", 0))

                        cost = calculate_cost("openai", model, token_usage)
                        if cost is not None:
                            span.set_attribute("cost_usd", cost)

                    # Collect all outputs into an array
                    outputs = []
                    if hasattr(response, 'choices'):
                        for choice in response.choices:
                            if hasattr(choice, 'message'):
                                # Add message output
                                message_output = {
                                    "type": "message",
                                    "content": choice.message.content if choice.message.content else "",
                                    "role": choice.message.role if hasattr(choice.message, 'role') else "assistant"
                                }
                                outputs.append(message_output)

                                # Check for tool calls
                                if hasattr(choice.message, 'tool_calls') and choice.message.tool_calls:
                                    for tool_call in choice.message.tool_calls:
                                        function_call_output = {
                                            "type": "function_call",
                                            "name": tool_call.function.name if hasattr(tool_call.function, 'name') else "",
                                            "arguments": tool_call.function.arguments if hasattr(tool_call.function, 'arguments') else "",
                                            "call_id": tool_call.id if hasattr(tool_call, 'id') else ""
                                        }
                                        outputs.append(function_call_output)

                    # Set outputs array as attribute (serialize to JSON string for OTel compatibility)
                    span.set_attribute("outputs", json.dumps(serialize_to_dict(outputs)))

                    # Mark span as successful
                    span.set_status(StatusCode.OK)

                    return response

            except Exception as e:
                # If tracking fails, log and return response if we got it, otherwise call original method
                logger.error(f"Playgent tracking failed in OpenAI chat completions: {e}")
                if 'response' in locals():
                    return response
                else:
                    return original_method(*args, **kwargs)

        return wrapper

    def _wrap_async_chat_completions_create_universal(self, original_method):
        """Universal async wrapper that works for both bound and unbound methods."""
        @functools.wraps(original_method)
        async def wrapper(*args, **kwargs):
            # Only track if Playgent is running
            if not state.is_running:
                return await original_method(*args, **kwargs)

            # Wrap ALL tracking code in try-except to ensure user's API calls never fail due to observability
            try:
                from ..spans import get_tracer
                from opentelemetry.trace import StatusCode

                messages = kwargs.get("messages", [])
                model = kwargs.get("model", "")

                # Get OpenTelemetry tracer
                tracer = get_tracer()

                # Create single generation span for entire API call
                with tracer.start_as_current_span("generation") as span:
                    # Mark as Playgent-created span (for filtering)

                    # Set span kind
                    span.set_attribute("span.kind", "generation")

                    # Set input attributes (serialize to JSON string for OTel compatibility)
                    import json
                    span.set_attribute("inputs", json.dumps(serialize_to_dict(messages)))
                    span.set_attribute("model", model)

                    if kwargs.get("temperature") is not None:
                        span.set_attribute("temperature", kwargs.get("temperature"))
                    if kwargs.get("max_tokens") is not None:
                        span.set_attribute("max_tokens", kwargs.get("max_tokens"))

                    # Set session_id and person_id if available from context
                    context = state._trace_context.get()
                    if context:
                        if context.session_id:
                            span.set_attribute("session_id", context.session_id)
                        if context.person_id:
                            span.set_attribute("person_id", context.person_id)
                    elif state.person_id:
                        span.set_attribute("person_id", state.person_id)

                    # Call original method
                    response = await original_method(*args, **kwargs)

                    # Extract token usage and calculate cost
                    token_usage = extract_token_usage(response, "openai")
                    if token_usage:
                        span.set_attribute("token_usage.input", token_usage.get("input", 0))
                        span.set_attribute("token_usage.output", token_usage.get("output", 0))
                        span.set_attribute("token_usage.total", token_usage.get("total", 0))

                        cost = calculate_cost("openai", model, token_usage)
                        if cost is not None:
                            span.set_attribute("cost_usd", cost)

                    # Collect all outputs into an array
                    outputs = []
                    if hasattr(response, 'choices'):
                        for choice in response.choices:
                            if hasattr(choice, 'message'):
                                # Add message output
                                message_output = {
                                    "type": "message",
                                    "content": choice.message.content if choice.message.content else "",
                                    "role": choice.message.role if hasattr(choice.message, 'role') else "assistant"
                                }
                                outputs.append(message_output)

                                # Check for tool calls
                                if hasattr(choice.message, 'tool_calls') and choice.message.tool_calls:
                                    for tool_call in choice.message.tool_calls:
                                        function_call_output = {
                                            "type": "function_call",
                                            "name": tool_call.function.name if hasattr(tool_call.function, 'name') else "",
                                            "arguments": tool_call.function.arguments if hasattr(tool_call.function, 'arguments') else "",
                                            "call_id": tool_call.id if hasattr(tool_call, 'id') else ""
                                        }
                                        outputs.append(function_call_output)

                    # Set outputs array as attribute (serialize to JSON string for OTel compatibility)
                    span.set_attribute("outputs", json.dumps(serialize_to_dict(outputs)))

                    # Mark span as successful
                    span.set_status(StatusCode.OK)

                    return response

            except Exception as e:
                # If tracking fails, log and return response if we got it, otherwise call original method
                logger.error(f"Playgent tracking failed in OpenAI async chat completions: {e}")
                if 'response' in locals():
                    return response
                else:
                    return await original_method(*args, **kwargs)

        return wrapper

    def _wrap_completions_create_universal(self, original_method):
        """Universal wrapper for regular completions."""
        @functools.wraps(original_method)
        def wrapper(*args, **kwargs):
            # Only track if Playgent is running
            if not state.is_running:
                return original_method(*args, **kwargs)

            # Wrap ALL tracking code in try-except to ensure user's API calls never fail due to observability
            try:
                from ..spans import get_tracer
                from opentelemetry.trace import StatusCode

                prompt = kwargs.get("prompt", "")
                model = kwargs.get("model", "")

                # Get OpenTelemetry tracer
                tracer = get_tracer()

                # Create single generation span for entire API call
                with tracer.start_as_current_span("generation") as span:
                    # Mark as Playgent-created span (for filtering)

                    # Set span kind
                    span.set_attribute("span.kind", "generation")

                    # Set input attributes
                    span.set_attribute("inputs", prompt)
                    span.set_attribute("model", model)

                    if kwargs.get("temperature") is not None:
                        span.set_attribute("temperature", kwargs.get("temperature"))
                    if kwargs.get("max_tokens") is not None:
                        span.set_attribute("max_tokens", kwargs.get("max_tokens"))

                    # Set session_id and person_id if available from context
                    context = state._trace_context.get()
                    if context:
                        if context.session_id:
                            span.set_attribute("session_id", context.session_id)
                        if context.person_id:
                            span.set_attribute("person_id", context.person_id)
                    elif state.person_id:
                        span.set_attribute("person_id", state.person_id)

                    # Call original method
                    response = original_method(*args, **kwargs)

                    # Extract token usage and calculate cost
                    token_usage = extract_token_usage(response, "openai")
                    if token_usage:
                        span.set_attribute("token_usage.input", token_usage.get("input", 0))
                        span.set_attribute("token_usage.output", token_usage.get("output", 0))
                        span.set_attribute("token_usage.total", token_usage.get("total", 0))

                        cost = calculate_cost("openai", model, token_usage)
                        if cost is not None:
                            span.set_attribute("cost_usd", cost)

                    # Collect all outputs into an array
                    outputs = []
                    if hasattr(response, 'choices'):
                        for choice in response.choices:
                            message_output = {
                                "type": "message",
                                "content": choice.text if hasattr(choice, 'text') else "",
                                "role": "assistant"
                            }
                            outputs.append(message_output)

                    # Set outputs array as attribute (serialize to JSON string for OTel compatibility)
                    span.set_attribute("outputs", json.dumps(serialize_to_dict(outputs)))

                    # Mark span as successful
                    span.set_status(StatusCode.OK)

                    return response

            except Exception as e:
                # If tracking fails, log and return response if we got it, otherwise call original method
                logger.error(f"Playgent tracking failed in OpenAI completions: {e}")
                if 'response' in locals():
                    return response
                else:
                    return original_method(*args, **kwargs)

        return wrapper

    def _wrap_responses_create_universal(self, original_method):
        """Universal wrapper for responses API."""
        @functools.wraps(original_method)
        def wrapper(*args, **kwargs):
            # Only track if Playgent is running
            if not state.is_running:
                return original_method(*args, **kwargs)

            # Wrap ALL tracking code in try-except to ensure user's API calls never fail due to observability
            try:
                from ..spans import get_tracer
                from opentelemetry.trace import StatusCode

                input_data = kwargs.get("input", "")
                instructions = kwargs.get("instructions", "")
                model = kwargs.get("model", "")

                # Get OpenTelemetry tracer
                tracer = get_tracer()

                # Create single generation span for entire API call
                with tracer.start_as_current_span("generation") as span:
                    # Mark as Playgent-created span (for filtering)

                    # Set span kind
                    span.set_attribute("span.kind", "generation")

                    # Set input attributes (serialize to JSON string for OTel compatibility)
                    import json
                    span.set_attribute("inputs", json.dumps(serialize_to_dict(input_data)))
                    span.set_attribute("instructions", instructions)
                    if model:
                        span.set_attribute("model", model)

                    # Set session_id and person_id if available from context
                    context = state._trace_context.get()
                    if context:
                        if context.session_id:
                            span.set_attribute("session_id", context.session_id)
                        if context.person_id:
                            span.set_attribute("person_id", context.person_id)
                    elif state.person_id:
                        span.set_attribute("person_id", state.person_id)

                    # Call original method
                    response = original_method(*args, **kwargs)

                    # Extract token usage and calculate cost
                    token_usage = extract_token_usage(response, "openai")
                    if token_usage:
                        span.set_attribute("token_usage.input", token_usage.get("input", 0))
                        span.set_attribute("token_usage.output", token_usage.get("output", 0))
                        span.set_attribute("token_usage.total", token_usage.get("total", 0))

                        cost = calculate_cost("openai", model, token_usage)
                        if cost is not None:
                            span.set_attribute("cost_usd", cost)

                    # Collect all outputs into an array
                    outputs = []
                    if hasattr(response, 'output') and response.output:
                        # Process each item in the output directly
                        for item in response.output:
                            # Each item in response.output has a type field
                            if hasattr(item, 'type'):
                                if item.type == 'message':
                                    # For message items, check if they have content
                                    if hasattr(item, 'content') and item.content:
                                        # Process each content block within the message
                                        for content_item in item.content:
                                            if hasattr(content_item, 'type') and content_item.type == 'output_text':
                                                message_output = {
                                                    "type": "message",
                                                    "content": content_item.text if hasattr(content_item, 'text') else "",
                                                    "role": "assistant"
                                                }
                                                outputs.append(message_output)

                                elif item.type == 'function_call':
                                    function_call_output = {
                                        "type": "function_call",
                                        "name": item.name if hasattr(item, 'name') else "",
                                        "arguments": item.arguments if hasattr(item, 'arguments') else "",
                                        "call_id": item.call_id if hasattr(item, 'call_id') else ""
                                    }
                                    outputs.append(function_call_output)

                                elif item.type == 'custom_tool_call':
                                    function_call_output = {
                                        "type": "function_call",
                                        "name": item.name if hasattr(item, 'name') else "",
                                        "arguments": item.arguments if hasattr(item, 'arguments') else "",
                                        "call_id": item.id if hasattr(item, 'id') else ""
                                    }
                                    outputs.append(function_call_output)

                                elif item.type == 'mcp_call':
                                    function_call_output = {
                                        "type": "function_call",
                                        "name": f"mcp_{item.name if hasattr(item, 'name') else ''}",
                                        "arguments": item.arguments if hasattr(item, 'arguments') else "",
                                        "call_id": item.id if hasattr(item, 'id') else ""
                                    }
                                    outputs.append(function_call_output)

                                elif item.type == 'web_search_call':
                                    function_call_output = {
                                        "type": "function_call",
                                        "name": "web_search",
                                        "arguments": json.dumps({"query": item.query if hasattr(item, 'query') else ""}),
                                        "call_id": item.id if hasattr(item, 'id') else ""
                                    }
                                    outputs.append(function_call_output)

                                elif item.type == 'reasoning':
                                    reasoning_output = {
                                        "type": "reasoning",
                                        "content": item.content if hasattr(item, 'content') else ""
                                    }
                                    outputs.append(reasoning_output)

                                elif item.type == 'output_text':
                                    message_output = {
                                        "type": "message",
                                        "content": item.content if hasattr(item, 'content') else "",
                                        "role": "assistant"
                                    }
                                    outputs.append(message_output)

                    # Set outputs array as attribute (serialize to JSON string for OTel compatibility)
                    span.set_attribute("outputs", json.dumps(serialize_to_dict(outputs)))

                    # Mark span as successful
                    span.set_status(StatusCode.OK)

                    return response

            except Exception as e:
                # If tracking fails, log and return response if we got it, otherwise call original method
                logger.error(f"Playgent tracking failed in OpenAI responses: {e}")
                if 'response' in locals():
                    return response
                else:
                    return original_method(*args, **kwargs)

        return wrapper

    def _patch_client_class(self, client_class):
        """Still patch __init__ for additional instance-level setup if needed."""
        # Store original if not already stored
        if not self._get_original('OpenAI.__init__'):
            self._store_original('OpenAI.__init__', client_class.__init__)

    def _patch_async_client_class(self, client_class):
        """Still patch __init__ for additional instance-level setup if needed."""
        # Store original if not already stored
        if not self._get_original('AsyncOpenAI.__init__'):
            self._store_original('AsyncOpenAI.__init__', client_class.__init__)

    def undo_patch(self) -> bool:
        """Restore original OpenAI methods."""
        try:
            import openai

            # Restore class-level methods
            try:
                from openai.resources.chat.completions import Completions
                original = self._get_original('Completions.create')
                if original:
                    Completions.create = original
            except ImportError:
                pass

            try:
                from openai.resources.chat.completions import AsyncCompletions
                original = self._get_original('AsyncCompletions.create')
                if original:
                    AsyncCompletions.create = original
            except ImportError:
                pass

            try:
                from openai.resources.completions import Completions as RegularCompletions
                original = self._get_original('RegularCompletions.create')
                if original:
                    RegularCompletions.create = original
            except ImportError:
                pass

            try:
                from openai.resources.responses import Responses
                original = self._get_original('Responses.create')
                if original:
                    Responses.create = original
            except (ImportError, AttributeError):
                pass

            self._clear_originals()
            self.is_patched = False
            return True

        except Exception as e:
            print(f"Failed to undo OpenAI patch: {e}")
            return False