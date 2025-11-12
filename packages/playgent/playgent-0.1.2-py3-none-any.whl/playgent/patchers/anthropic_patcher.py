"""Improved Anthropic library patcher that handles existing instances."""

import functools
import logging
import gc
import uuid
from typing import Any, Dict, Optional
from .base import Patcher
from .. import state, core
from ..types import serialize_to_dict
from ..cost_calculator import extract_token_usage, calculate_cost

logger = logging.getLogger(__name__)


class AnthropicPatcher(Patcher):
    """Improved patcher for Anthropic that handles existing instances."""

    def attempt_patch(self) -> bool:
        """Patch Anthropic at multiple levels to handle all scenarios."""
        try:
            import anthropic

            # Strategy 1: Patch at the class/module level for all instances
            self._patch_at_class_level()

            # Strategy 2: Find and note existing instances (already affected by class-level patch)
            self._patch_existing_instances()

            self.is_patched = True
            return True

        except Exception as e:
            print(f"Failed to patch Anthropic: {e}")
            return False

    def _patch_at_class_level(self):
        """Patch methods at the class level so all instances (new and existing) are affected."""
        import anthropic

        # Patch Messages class methods directly
        try:
            from anthropic.resources import Messages
            if hasattr(Messages, 'create'):
                original = Messages.create
                Messages.create = self._wrap_messages_create_universal(original)
                self._store_original('Messages.create', original)
        except ImportError:
            pass

        # Patch AsyncMessages if it exists
        try:
            from anthropic.resources import AsyncMessages
            if hasattr(AsyncMessages, 'create'):
                original = AsyncMessages.create
                AsyncMessages.create = self._wrap_async_messages_create_universal(original)
                self._store_original('AsyncMessages.create', original)
        except ImportError:
            pass

        # Patch Completions for older API
        try:
            from anthropic.resources import Completions
            if hasattr(Completions, 'create'):
                original = Completions.create
                Completions.create = self._wrap_completions_create_universal(original)
                self._store_original('Completions.create', original)
        except ImportError:
            pass

        # Patch AsyncCompletions if it exists
        try:
            from anthropic.resources import AsyncCompletions
            if hasattr(AsyncCompletions, 'create'):
                original = AsyncCompletions.create
                AsyncCompletions.create = self._wrap_async_completions_create_universal(original)
                self._store_original('AsyncCompletions.create', original)
        except ImportError:
            pass

    def _patch_existing_instances(self):
        """Find and note any existing Anthropic client instances in memory."""
        import anthropic

        # Use garbage collector to find all instances
        for obj in gc.get_objects():
            try:
                # Check if it's an Anthropic client instance
                if isinstance(obj, anthropic.Anthropic) or (hasattr(anthropic, 'AsyncAnthropic') and isinstance(obj, anthropic.AsyncAnthropic)):
                    # The methods are already patched at class level
                    pass
            except:
                # Some objects might not be accessible
                continue

    def _wrap_messages_create_universal(self, original_method):
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
                system = kwargs.get("system", "")

                # Get OpenTelemetry tracer
                tracer = get_tracer()

                # Create single generation span for entire API call
                with tracer.start_as_current_span("generation") as span:

                    # Set span kind
                    span.set_attribute("span.kind", "generation")

                    # Set input attributes (serialize to JSON string for OTel compatibility)
                    import json
                    span.set_attribute("inputs", json.dumps(serialize_to_dict(messages)))
                    span.set_attribute("model", model)

                    if system:
                        span.set_attribute("system", system)
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
                    token_usage = extract_token_usage(response, "anthropic")
                    if token_usage:
                        span.set_attribute("token_usage.input", token_usage.get("input", 0))
                        span.set_attribute("token_usage.output", token_usage.get("output", 0))
                        span.set_attribute("token_usage.total", token_usage.get("total", 0))

                        cost = calculate_cost("anthropic", model, token_usage)
                        if cost is not None:
                            span.set_attribute("cost_usd", cost)

                    # Collect all outputs into an array
                    outputs = []
                    if hasattr(response, 'content'):
                        # Anthropic returns content blocks
                        for block in response.content:
                            if hasattr(block, 'text'):
                                # Text content block
                                message_output = {
                                    "type": "message",
                                    "content": block.text,
                                    "role": "assistant"
                                }
                                outputs.append(message_output)
                            elif hasattr(block, 'type'):
                                if block.type == 'tool_use':
                                    # Tool use block
                                    function_call_output = {
                                        "type": "function_call",
                                        "name": block.name if hasattr(block, 'name') else "",
                                        "arguments": str(block.input) if hasattr(block, 'input') else "",
                                        "call_id": block.id if hasattr(block, 'id') else ""
                                    }
                                    outputs.append(function_call_output)
                                elif block.type == 'thinking':
                                    # Thinking block (Claude extended thinking)
                                    thinking_output = {
                                        "type": "thinking",
                                        "content": block.thinking if hasattr(block, 'thinking') else ""
                                    }
                                    outputs.append(thinking_output)

                    # Set outputs array as attribute (serialize to JSON string for OTel compatibility)
                    span.set_attribute("outputs", json.dumps(serialize_to_dict(outputs)))

                    # Mark span as successful
                    span.set_status(StatusCode.OK)

                    return response

            except Exception as e:
                # If tracking fails, log and return response if we got it, otherwise call original method
                logger.error(f"Playgent tracking failed in Anthropic messages: {e}")
                if 'response' in locals():
                    return response
                else:
                    return original_method(*args, **kwargs)

        return wrapper

    def _wrap_async_messages_create_universal(self, original_method):
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
                system = kwargs.get("system", "")

                # Get OpenTelemetry tracer
                tracer = get_tracer()

                # Create single generation span for entire API call
                with tracer.start_as_current_span("generation") as span:

                    # Set span kind
                    span.set_attribute("span.kind", "generation")

                    # Set input attributes (serialize to JSON string for OTel compatibility)
                    import json
                    span.set_attribute("inputs", json.dumps(serialize_to_dict(messages)))
                    span.set_attribute("model", model)

                    if system:
                        span.set_attribute("system", system)
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
                    token_usage = extract_token_usage(response, "anthropic")
                    if token_usage:
                        span.set_attribute("token_usage.input", token_usage.get("input", 0))
                        span.set_attribute("token_usage.output", token_usage.get("output", 0))
                        span.set_attribute("token_usage.total", token_usage.get("total", 0))

                        cost = calculate_cost("anthropic", model, token_usage)
                        if cost is not None:
                            span.set_attribute("cost_usd", cost)

                    # Collect all outputs into an array
                    outputs = []
                    if hasattr(response, 'content'):
                        # Anthropic returns content blocks
                        for block in response.content:
                            if hasattr(block, 'text'):
                                # Text content block
                                message_output = {
                                    "type": "message",
                                    "content": block.text,
                                    "role": "assistant"
                                }
                                outputs.append(message_output)
                            elif hasattr(block, 'type'):
                                if block.type == 'tool_use':
                                    # Tool use block
                                    function_call_output = {
                                        "type": "function_call",
                                        "name": block.name if hasattr(block, 'name') else "",
                                        "arguments": str(block.input) if hasattr(block, 'input') else "",
                                        "call_id": block.id if hasattr(block, 'id') else ""
                                    }
                                    outputs.append(function_call_output)
                                elif block.type == 'thinking':
                                    # Thinking block (Claude extended thinking)
                                    thinking_output = {
                                        "type": "thinking",
                                        "content": block.thinking if hasattr(block, 'thinking') else ""
                                    }
                                    outputs.append(thinking_output)

                    # Set outputs array as attribute (serialize to JSON string for OTel compatibility)
                    span.set_attribute("outputs", json.dumps(serialize_to_dict(outputs)))

                    # Mark span as successful
                    span.set_status(StatusCode.OK)

                    return response

            except Exception as e:
                # If tracking fails, log and return response if we got it, otherwise call original method
                logger.error(f"Playgent tracking failed in Anthropic async messages: {e}")
                if 'response' in locals():
                    return response
                else:
                    return await original_method(*args, **kwargs)

        return wrapper

    def _wrap_completions_create_universal(self, original_method):
        """Universal wrapper for completions."""
        @functools.wraps(original_method)
        def wrapper(*args, **kwargs):
            # Only track if Playgent is running
            if not state.is_running:
                return original_method(*args, **kwargs)

            # Wrap ALL tracking code in try-except to ensure user's API calls never fail due to observability
            try:
                prompt = kwargs.get("prompt", "")
                model = kwargs.get("model", "")

                # Create input span
                from ..spans import create_span

                input_attributes = {
                    "inputs": prompt,
                    "model": model,
                    "temperature": kwargs.get("temperature"),
                    "max_tokens_to_sample": kwargs.get("max_tokens_to_sample"),
                    "instructions": f"Model: {model}"
                }

                with create_span(
                    name="completions.create",
                    kind="input",
                    attributes=input_attributes
                ) as input_span:
                    # Store the input span ID for child spans
                    actual_input_span_id = input_span.id

                    # Call original method
                    response = original_method(*args, **kwargs)

                    # Extract token usage and calculate cost
                    token_usage = extract_token_usage(response, "anthropic")
                    if token_usage:
                        input_span.token_usage = token_usage
                        cost = calculate_cost("anthropic", model, token_usage)
                        if cost is not None:
                            input_span.cost_usd = cost

                    # Process response
                    if hasattr(response, 'completion'):
                        # Create message span for text output
                        message_span = Span(
                            trace_id=input_span.trace_id,
                            id=str(uuid.uuid4()),
                            parent_span_id=actual_input_span_id,
                            name="message",
                            kind="message"
                        )

                        message_span.attributes = {
                            "content": response.completion,
                            "type": "output_text"
                        }

                        message_span.end(status="ok")
                        core.emit_span(message_span)

                    return response

            except Exception as e:
                # If tracking fails, log and return response if we got it, otherwise call original method
                logger.error(f"Playgent tracking failed in Anthropic completions: {e}")
                if 'response' in locals():
                    return response
                else:
                    return original_method(*args, **kwargs)

        return wrapper

    def _wrap_async_completions_create_universal(self, original_method):
        """Universal async wrapper for completions."""
        @functools.wraps(original_method)
        async def wrapper(*args, **kwargs):
            # Only track if Playgent is running
            if not state.is_running:
                return await original_method(*args, **kwargs)

            # Wrap ALL tracking code in try-except to ensure user's API calls never fail due to observability
            try:
                prompt = kwargs.get("prompt", "")
                model = kwargs.get("model", "")

                # Create input span
                from ..spans import create_span_async

                input_attributes = {
                    "inputs": prompt,
                    "model": model,
                    "temperature": kwargs.get("temperature"),
                    "max_tokens_to_sample": kwargs.get("max_tokens_to_sample"),
                    "instructions": f"Model: {model}"
                }

                async with create_span_async(
                    name="completions.create",
                    kind="input",
                    attributes=input_attributes
                ) as input_span:
                    # Store the input span ID for child spans
                    actual_input_span_id = input_span.id

                    # Call original method
                    response = await original_method(*args, **kwargs)

                    # Extract token usage and calculate cost
                    token_usage = extract_token_usage(response, "anthropic")
                    if token_usage:
                        input_span.token_usage = token_usage
                        cost = calculate_cost("anthropic", model, token_usage)
                        if cost is not None:
                            input_span.cost_usd = cost

                    # Process response
                    if hasattr(response, 'completion'):
                        # Create message span for text output
                        message_span = Span(
                            trace_id=input_span.trace_id,
                            id=str(uuid.uuid4()),
                            parent_span_id=actual_input_span_id,
                            name="message",
                            kind="message"
                        )

                        message_span.attributes = {
                            "content": response.completion,
                            "type": "output_text"
                        }

                        message_span.end(status="ok")
                        core.emit_span(message_span)

                    return response

            except Exception as e:
                # If tracking fails, log and return response if we got it, otherwise call original method
                logger.error(f"Playgent tracking failed in Anthropic async completions: {e}")
                if 'response' in locals():
                    return response
                else:
                    return await original_method(*args, **kwargs)

        return wrapper


    def undo_patch(self) -> bool:
        """Restore original Anthropic methods."""
        try:
            import anthropic

            # Restore Messages class
            try:
                from anthropic.resources import Messages
                original = self._get_original('Messages.create')
                if original:
                    Messages.create = original
            except ImportError:
                pass

            # Restore AsyncMessages
            try:
                from anthropic.resources import AsyncMessages
                original = self._get_original('AsyncMessages.create')
                if original:
                    AsyncMessages.create = original
            except ImportError:
                pass

            # Restore Completions
            try:
                from anthropic.resources import Completions
                original = self._get_original('Completions.create')
                if original:
                    Completions.create = original
            except ImportError:
                pass

            # Restore AsyncCompletions
            try:
                from anthropic.resources import AsyncCompletions
                original = self._get_original('AsyncCompletions.create')
                if original:
                    AsyncCompletions.create = original
            except ImportError:
                pass

            self._clear_originals()
            self.is_patched = False
            return True

        except Exception as e:
            print(f"Failed to undo Anthropic patch: {e}")
            return False