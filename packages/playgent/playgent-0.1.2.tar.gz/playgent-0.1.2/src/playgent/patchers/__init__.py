"""Patchers for automatic LLM library instrumentation."""

from typing import Dict, Optional
from .base import Patcher
from .openai_patcher import OpenAIPatcher
from .anthropic_patcher import AnthropicPatcher


# Registry of available patchers
_patchers: Dict[str, Patcher] = {}


def get_patcher(library_name: str) -> Optional[Patcher]:
    """Get or create a patcher for the specified library."""
    if library_name not in _patchers:
        if library_name == "openai":
            _patchers[library_name] = OpenAIPatcher()
        elif library_name == "anthropic":
            _patchers[library_name] = AnthropicPatcher()
        else:
            return None

    return _patchers[library_name]


def patch_library(library_name: str) -> bool:
    """Patch a specific library for automatic tracking.

    Args:
        library_name: Name of the library to patch ('openai', 'anthropic', etc.)

    Returns:
        True if patching succeeded, False otherwise
    """
    patcher = get_patcher(library_name)
    if patcher and not patcher.is_patched:
        return patcher.attempt_patch()
    return False


def unpatch_library(library_name: str) -> bool:
    """Remove patches from a specific library.

    Args:
        library_name: Name of the library to unpatch

    Returns:
        True if unpatching succeeded, False otherwise
    """
    patcher = get_patcher(library_name)
    if patcher and patcher.is_patched:
        return patcher.undo_patch()
    return False


def unpatch_all() -> None:
    """Remove all active patches."""
    for library_name in list(_patchers.keys()):
        unpatch_library(library_name)
    _patchers.clear()


# List of libraries to auto-patch
SUPPORTED_LIBRARIES = ["openai", "anthropic"]


__all__ = [
    "Patcher",
    "OpenAIPatcher",
    "AnthropicPatcher",
    "get_patcher",
    "patch_library",
    "unpatch_library",
    "unpatch_all",
    "SUPPORTED_LIBRARIES",
]