"""Hook system for pre/post conversion callbacks."""

from typing import Callable, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum


class HookPhase(Enum):
    """Phases where hooks can be executed."""

    PRE_CONVERT = "pre_convert"      # Before conversion starts
    POST_CONVERT = "post_convert"    # After conversion completes
    PRE_RENDER = "pre_render"        # Before rendering starts
    POST_RENDER = "post_render"     # After rendering completes
    ON_ERROR = "on_error"           # When an error occurs


@dataclass
class Hook:
    """A callable hook with metadata."""

    name: str
    callback: Callable[[Dict[str, Any]], None]
    phase: HookPhase
    description: str = ""
    enabled: bool = True


class HookManager:
    """Manage conversion hooks.

    Usage:
        from md_converter.utils.hooks import HookManager, HookPhase

        hooks = HookManager()

        def my_pre_convert(context):
            print(f"Converting {context['input_path']}")

        hooks.register("my_hook", HookPhase.PRE_CONVERT, my_pre_convert)
        hooks.trigger(HookPhase.PRE_CONVERT, {"input_path": "doc.md"})

        # With Converter
        converter = Converter()
        converter.hooks.register("log", HookPhase.POST_CONVERT, lambda ctx: print("Done!"))
        converter.convert("doc.md", "out.pdf")
    """

    def __init__(self):
        self._hooks: Dict[HookPhase, List[Hook]] = {phase: [] for phase in HookPhase}

    def register(
        self,
        name: str,
        phase: HookPhase,
        callback: Callable[[Dict[str, Any]], None],
        description: str = "",
    ) -> None:
        """Register a hook.

        Args:
            name: Unique name for the hook
            phase: When to execute (PRE_CONVERT, POST_CONVERT, etc.)
            callback: Function that takes context dict
            description: Optional description
        """
        # Check if hook with same name already exists
        for existing in self._hooks[phase]:
            if existing.name == name:
                existing.callback = callback  # Update existing
                existing.enabled = True
                return

        hook = Hook(
            name=name,
            callback=callback,
            phase=phase,
            description=description,
        )
        self._hooks[phase].append(hook)

    def unregister(self, name: str, phase: HookPhase = None) -> None:
        """Unregister a hook by name.

        Args:
            name: Name of the hook to remove
            phase: Optional phase filter (if None, removes from all phases)
        """
        if phase:
            self._hooks[phase] = [h for h in self._hooks[phase] if h.name != name]
        else:
            for p in HookPhase:
                self._hooks[p] = [h for h in self._hooks[p] if h.name != name]

    def trigger(self, phase: HookPhase, context: Dict[str, Any]) -> None:
        """Trigger all hooks for a given phase.

        Args:
            phase: The hook phase to trigger
            context: Context dictionary passed to each hook
        """
        for hook in self._hooks[phase]:
            if hook.enabled:
                try:
                    hook.callback(context)
                except Exception as e:
                    # Hook errors should not break conversion
                    # Log but continue
                    import warnings
                    warnings.warn(f"Hook '{hook.name}' failed: {e}")

    def list_hooks(self, phase: HookPhase = None) -> List[Hook]:
        """List all registered hooks.

        Args:
            phase: Optional filter by phase

        Returns:
            List of Hook objects
        """
        if phase:
            return list(self._hooks[phase])
        all_hooks = []
        for hooks in self._hooks.values():
            all_hooks.extend(hooks)
        return all_hooks

    def disable(self, name: str) -> None:
        """Disable a hook by name."""
        for hooks in self._hooks.values():
            for hook in hooks:
                if hook.name == name:
                    hook.enabled = False

    def enable(self, name: str) -> None:
        """Enable a hook by name."""
        for hooks in self._hooks.values():
            for hook in hooks:
                if hook.name == name:
                    hook.enabled = True


# Global hook manager
_global_hooks = HookManager()


def get_hooks() -> HookManager:
    """Get the global hook manager instance."""
    return _global_hooks


def register_global_hook(
    name: str,
    phase: HookPhase,
    callback: Callable[[Dict[str, Any]], None],
    description: str = "",
) -> None:
    """Register a global hook across all Converter instances.

    Note: Per-instance hooks are checked first, then global hooks.
    """
    _global_hooks.register(name, phase, callback, description)


def clear_global_hooks() -> None:
    """Clear all global hooks. Use with caution."""
    global _global_hooks
    _global_hooks = HookManager()
