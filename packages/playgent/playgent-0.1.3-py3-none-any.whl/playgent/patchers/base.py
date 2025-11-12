"""Base patcher class for library instrumentation."""

from abc import ABC, abstractmethod
from typing import Any, Optional


class Patcher(ABC):
    """Abstract base class for library patchers.

    Each patcher is responsible for patching a specific library (OpenAI, Anthropic, etc.)
    to automatically track LLM calls.
    """

    def __init__(self):
        self.is_patched = False
        self._original_methods = {}

    @abstractmethod
    def attempt_patch(self) -> bool:
        """Attempt to patch the target library.

        Returns:
            True if patching succeeded, False otherwise
        """
        pass

    @abstractmethod
    def undo_patch(self) -> bool:
        """Restore original library methods.

        Returns:
            True if restoration succeeded, False otherwise
        """
        pass

    def _store_original(self, key: str, original: Any):
        """Store original method/object for later restoration."""
        self._original_methods[key] = original

    def _get_original(self, key: str) -> Optional[Any]:
        """Retrieve stored original method/object."""
        return self._original_methods.get(key)

    def _clear_originals(self):
        """Clear all stored original methods."""
        self._original_methods.clear()