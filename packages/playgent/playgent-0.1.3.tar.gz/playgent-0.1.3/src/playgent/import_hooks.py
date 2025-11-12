"""Import hook system for automatic library patching.

This module provides infrastructure to intercept module imports and apply
patches after modules are loaded, similar to how Weave handles automatic
LLM tracking.
"""

import sys
import threading
from typing import Dict, List, Callable, Optional, Any
from importlib.abc import MetaPathFinder, Loader
from importlib.machinery import ModuleSpec
import importlib.util


# Global registry of post-import hooks
_post_import_hooks: Dict[str, List[Callable]] = {}
_post_import_hooks_lock = threading.Lock()
_import_hook_finder_installed = False


class ImportHookChainedLoader(Loader):
    """Wrapper for module loaders that executes post-import hooks."""

    def __init__(self, loader: Loader, module_name: str):
        self.loader = loader
        self.module_name = module_name

    def create_module(self, spec):
        """Delegate to original loader."""
        if hasattr(self.loader, 'create_module'):
            return self.loader.create_module(spec)
        return None

    def exec_module(self, module):
        """Execute module and then run post-import hooks."""
        # Execute the original module
        self.loader.exec_module(module)

        # Run post-import hooks
        notify_module_loaded(module)

    def load_module(self, fullname):
        """Legacy load_module support."""
        module = self.loader.load_module(fullname)
        notify_module_loaded(module)
        return module


class ImportHookFinder(MetaPathFinder):
    """Custom meta path finder that intercepts imports for registered modules."""

    def find_spec(self, fullname: str, path: Optional[List[str]], target: Optional[Any] = None) -> Optional[ModuleSpec]:
        """Find module spec and wrap loader if hooks are registered."""
        # Check if we have hooks for this module
        with _post_import_hooks_lock:
            if fullname not in _post_import_hooks:
                return None

            # Don't process if hooks have already been executed
            hooks = _post_import_hooks.get(fullname, [])
            if not hooks:
                return None

        # Find the actual spec using the rest of sys.meta_path
        for finder in sys.meta_path:
            if finder is self:
                continue

            if hasattr(finder, 'find_spec'):
                spec = finder.find_spec(fullname, path, target)
                if spec is not None:
                    # Wrap the loader to execute hooks after import
                    if spec.loader is not None:
                        spec.loader = ImportHookChainedLoader(spec.loader, fullname)
                    return spec

        return None

    def find_module(self, fullname: str, path: Optional[List[str]] = None):
        """Legacy find_module support for older Python versions."""
        spec = self.find_spec(fullname, path)
        if spec is not None:
            return spec.loader
        return None


def install_import_hook_finder():
    """Install the ImportHookFinder into sys.meta_path if not already installed."""
    global _import_hook_finder_installed

    with _post_import_hooks_lock:
        if _import_hook_finder_installed:
            return

        # Check if already in meta_path
        for finder in sys.meta_path:
            if isinstance(finder, ImportHookFinder):
                _import_hook_finder_installed = True
                return

        # Insert at the beginning to intercept imports early
        sys.meta_path.insert(0, ImportHookFinder())
        _import_hook_finder_installed = True


def notify_module_loaded(module):
    """Execute all registered hooks for a module."""
    module_name = module.__name__

    # Get hooks to execute (outside lock to prevent deadlock)
    hooks_to_execute = []
    with _post_import_hooks_lock:
        if module_name in _post_import_hooks:
            hooks_to_execute = _post_import_hooks[module_name].copy()
            # Clear hooks after getting them (but keep key to mark as processed)
            _post_import_hooks[module_name] = []

    # Execute hooks outside the lock
    for hook in hooks_to_execute:
        try:
            hook(module)
        except Exception as e:
            # Log error but continue with other hooks
            print(f"Error executing import hook for {module_name}: {e}")


def register_post_import_hook(hook: Callable, module_name: str):
    """Register a hook to be called after a module is imported.

    Args:
        hook: Callable that takes the module as argument
        module_name: Name of the module to hook (e.g., 'openai')
    """
    # Install the finder if needed
    install_import_hook_finder()

    # Check if module is already imported
    if module_name in sys.modules:
        # Module already imported, execute hook immediately
        try:
            hook(sys.modules[module_name])
        except Exception as e:
            print(f"Error executing immediate hook for {module_name}: {e}")
        return

    # Register hook for future import
    with _post_import_hooks_lock:
        if module_name not in _post_import_hooks:
            _post_import_hooks[module_name] = []
        _post_import_hooks[module_name].append(hook)


def unregister_hooks(module_name: str):
    """Remove all hooks for a specific module."""
    with _post_import_hooks_lock:
        if module_name in _post_import_hooks:
            del _post_import_hooks[module_name]


def clear_all_hooks():
    """Clear all registered hooks."""
    with _post_import_hooks_lock:
        _post_import_hooks.clear()