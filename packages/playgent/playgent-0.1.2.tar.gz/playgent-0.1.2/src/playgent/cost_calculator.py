"""Cost calculation for LLM token usage.

Pricing data based on public pricing as of January 2025.
These should ideally be configurable via environment or config file.
"""

from typing import Dict, Optional

# Pricing per 1000 tokens in USD
# Sources:
# - OpenAI: https://openai.com/pricing
# - Anthropic: https://www.anthropic.com/pricing
PRICING = {
    "openai": {
        # GPT-4 models
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-4-turbo-preview": {"input": 0.01, "output": 0.03},
        "gpt-4o": {"input": 0.005, "output": 0.015},
        "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},

        # GPT-3.5 models
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
        "gpt-3.5-turbo-16k": {"input": 0.003, "output": 0.004},

        # O1 models (reasoning models)
        "o1-preview": {"input": 0.015, "output": 0.06},
        "o1-mini": {"input": 0.003, "output": 0.012},

        # GPT-5 placeholder (update when available)
        "gpt-5": {"input": 0.01, "output": 0.03},  # Assuming similar to gpt-4-turbo
    },
    "anthropic": {
        # Claude 3 models
        "claude-3-opus-20240229": {"input": 0.015, "output": 0.075},
        "claude-3-sonnet-20240229": {"input": 0.003, "output": 0.015},
        "claude-3-haiku-20240307": {"input": 0.00025, "output": 0.00125},

        # Claude 3.5 models
        "claude-3-5-sonnet-20241022": {"input": 0.003, "output": 0.015},
        "claude-3-5-haiku-20241022": {"input": 0.001, "output": 0.005},

        # Simplified names (map to specific versions)
        "claude-3-opus": {"input": 0.015, "output": 0.075},
        "claude-3-sonnet": {"input": 0.003, "output": 0.015},
        "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
        "claude-3.5-sonnet": {"input": 0.003, "output": 0.015},
        "claude-3.5-haiku": {"input": 0.001, "output": 0.005},

        # Legacy models
        "claude-2.1": {"input": 0.008, "output": 0.024},
        "claude-2": {"input": 0.008, "output": 0.024},
        "claude-instant-1.2": {"input": 0.0008, "output": 0.0024},
    },
    "cohere": {
        # Command models
        "command": {"input": 0.001, "output": 0.002},
        "command-light": {"input": 0.00015, "output": 0.0006},
        "command-r": {"input": 0.0005, "output": 0.0015},
        "command-r-plus": {"input": 0.003, "output": 0.015},
    },
    "google": {
        # Gemini models
        "gemini-pro": {"input": 0.00025, "output": 0.0005},
        "gemini-pro-vision": {"input": 0.00025, "output": 0.0005},
        "gemini-1.5-pro": {"input": 0.0035, "output": 0.0105},
        "gemini-1.5-flash": {"input": 0.000075, "output": 0.0003},
    }
}


def calculate_cost(
    provider: str,
    model: str,
    token_usage: Optional[Dict[str, int]]
) -> Optional[float]:
    """Calculate cost in USD based on token usage.

    Args:
        provider: LLM provider (e.g., "openai", "anthropic")
        model: Model name (e.g., "gpt-4", "claude-3-opus")
        token_usage: Dictionary with "input" and "output" token counts

    Returns:
        Cost in USD rounded to 6 decimal places, or None if cannot calculate
    """
    if not token_usage:
        return None

    # Normalize provider name
    provider = provider.lower()

    # Get pricing for provider and model
    if provider not in PRICING:
        return None

    provider_pricing = PRICING[provider]

    # Try exact model match first
    model_pricing = None
    if model in provider_pricing:
        model_pricing = provider_pricing[model]
    else:
        # Try to find a partial match (e.g., "gpt-4-0125-preview" → "gpt-4-turbo-preview")
        for key in provider_pricing:
            if key in model or model in key:
                model_pricing = provider_pricing[key]
                break

    if not model_pricing:
        return None

    # Calculate cost
    input_tokens = token_usage.get("input", 0)
    output_tokens = token_usage.get("output", 0)

    # Pricing is per 1000 tokens
    input_cost = (input_tokens / 1000.0) * model_pricing["input"]
    output_cost = (output_tokens / 1000.0) * model_pricing["output"]

    total_cost = input_cost + output_cost

    # Round to 6 decimal places (smallest unit is typically $0.000001)
    return round(total_cost, 6)


def extract_token_usage(response: any, provider: str) -> Optional[Dict[str, int]]:
    """Extract token usage from LLM response object.

    Args:
        response: Response object from LLM provider
        provider: Provider name (e.g., "openai", "anthropic")

    Returns:
        Dictionary with "input", "output", and "total" token counts, or None

    Note:
        This function will never raise exceptions. If extraction fails, it returns None.
    """
    try:
        token_usage = None

        if provider == "openai":
            # OpenAI responses have usage attribute
            if hasattr(response, 'usage'):
                usage = response.usage
                if usage:
                    token_usage = {
                        "input": getattr(usage, 'prompt_tokens', 0) or getattr(usage, 'input_tokens', 0),
                        "output": getattr(usage, 'completion_tokens', 0) or getattr(usage, 'output_tokens', 0),
                        "total": getattr(usage, 'total_tokens', 0)
                    }
                    # Calculate total if not provided
                    if not token_usage["total"]:
                        token_usage["total"] = token_usage["input"] + token_usage["output"]

        elif provider == "anthropic":
            # Anthropic responses have usage attribute
            if hasattr(response, 'usage'):
                usage = response.usage
                if usage:
                    token_usage = {
                        "input": getattr(usage, 'input_tokens', 0),
                        "output": getattr(usage, 'output_tokens', 0),
                        "total": 0
                    }
                    token_usage["total"] = token_usage["input"] + token_usage["output"]

        elif provider == "cohere":
            # Cohere responses may have meta.tokens attribute
            if hasattr(response, 'meta') and hasattr(response.meta, 'tokens'):
                tokens = response.meta.tokens
                if tokens:
                    token_usage = {
                        "input": getattr(tokens, 'input_tokens', 0),
                        "output": getattr(tokens, 'output_tokens', 0),
                        "total": getattr(tokens, 'total_tokens', 0)
                    }

        return token_usage
    except Exception:
        # Silent failure - return None if extraction fails for any reason
        return None