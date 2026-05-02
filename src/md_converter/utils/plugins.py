"""Plugin system for extensible parsers and renderers."""

import logging
import importlib
import inspect
from typing import Dict, Type, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
from enum import Enum


logger = logging.getLogger(__name__)


class PluginType(Enum):
    """Types of plugins supported."""

    PARSER = "parser"       # Markdown parsers
    RENDERER = "renderer"   # Output renderers (PDF, DOCX, HTML, etc.)
    EXTENSION = "extension" # Markdown extensions


@dataclass
class PluginMetadata:
    """Metadata about a loaded plugin."""

    name: str
    plugin_type: PluginType
    version: str
    description: str
    author: str
    cls: Type


class PluginRegistry:
    """Registry for plugins.

    Usage:
        from md_converter.utils.plugins import PluginRegistry, PluginType

        registry = PluginRegistry()

        # Discover built-in plugins
        registry.discover_builtins()

        # Load a plugin
        registry.load_plugin(MyCustomParser, PluginType.PARSER)

        # Get a plugin
        parser_cls = registry.get_plugin("my_parser", PluginType.PARSER)

        # List all plugins of a type
        for name in registry.list_plugins(PluginType.PARSER):
            print(name)
    """

    def __init__(self):
        self._plugins: Dict[PluginType, Dict[str, PluginMetadata]] = {
            pt: {} for pt in PluginType
        }

    def register(
        self,
        cls: Type,
        plugin_type: PluginType,
        name: str = None,
        description: str = "",
        version: str = "1.0.0",
        author: str = "unknown",
    ) -> None:
        """Register a plugin class.

        Args:
            cls: The plugin class
            plugin_type: Type of plugin
            name: Optional name (defaults to class name)
            description: Plugin description
            version: Plugin version
            author: Plugin author
        """
        plugin_name = name or cls.__name__

        metadata = PluginMetadata(
            name=plugin_name,
            plugin_type=plugin_type,
            version=version,
            description=description,
            author=author,
            cls=cls,
        )
        self._plugins[plugin_type][plugin_name] = metadata
        logger.debug(f"Registered plugin: {plugin_name} ({plugin_type.value})")

    def unregister(self, name: str, plugin_type: PluginType) -> bool:
        """Unregister a plugin.

        Args:
            name: Plugin name
            plugin_type: Plugin type

        Returns:
            True if removed, False if not found
        """
        if name in self._plugins[plugin_type]:
            del self._plugins[plugin_type][name]
            return True
        return False

    def get_plugin(self, name: str, plugin_type: PluginType) -> Optional[Type]:
        """Get a plugin class by name.

        Args:
            name: Plugin name
            plugin_type: Plugin type

        Returns:
            Plugin class or None if not found
        """
        metadata = self._plugins[plugin_type].get(name)
        return metadata.cls if metadata else None

    def list_plugins(self, plugin_type: PluginType = None) -> List[str]:
        """List all plugins or plugins of a specific type.

        Args:
            plugin_type: Optional filter by type

        Returns:
            List of plugin names
        """
        if plugin_type:
            return list(self._plugins[plugin_type].keys())
        all_names = []
        for plugins in self._plugins.values():
            all_names.extend(plugins.keys())
        return all_names

    def get_metadata(self, name: str, plugin_type: PluginType) -> Optional[PluginMetadata]:
        """Get plugin metadata.

        Args:
            name: Plugin name
            plugin_type: Plugin type

        Returns:
            PluginMetadata or None if not found
        """
        return self._plugins[plugin_type].get(name)

    def discover_builtins(self) -> None:
        """Discover and register all built-in plugins."""
        from md_converter.parsers.markdown import MarkdownParser
        from md_converter.parsers.mermaid import MermaidParser, KrokiRenderer
        from md_converter.parsers.math import MathParser
        from md_converter.parsers.frontmatter import FrontmatterParser
        from md_converter.renderers.pdf import PDFRenderer
        from md_converter.renderers.docx import DOCXRenderer
        from md_converter.renderers.html import HTMLRenderer

        # Built-in parsers
        self.register(MarkdownParser, PluginType.PARSER, "markdown", "Default Markdown parser")
        self.register(MermaidParser, PluginType.PARSER, "mermaid", "Mermaid diagram parser")
        self.register(MathParser, PluginType.PARSER, "math", "Math/LaTeX parser")
        self.register(FrontmatterParser, PluginType.PARSER, "frontmatter", "YAML frontmatter parser")
        self.register(KrokiRenderer, PluginType.PARSER, "kroki", "Kroki diagram renderer")

        # Built-in renderers
        self.register(PDFRenderer, PluginType.RENDERER, "pdf", "WeasyPrint PDF renderer")
        self.register(DOCXRenderer, PluginType.RENDERER, "docx", "python-docx renderer")
        self.register(HTMLRenderer, PluginType.RENDERER, "html", "HTML renderer")

    def load_from_entry_points(self) -> int:
        """Load plugins from package entry points.

        Looks for 'md_convert.plugins' entry point group.

        Returns:
            Number of plugins loaded
        """
        loaded = 0
        try:
            from importlib.metadata import entry_points

            eps = entry_points()
            md_convert_eps = eps.get("md_convert.plugins", [])

            for ep in md_convert_eps:
                try:
                    module = importlib.import_module(ep.module)
                    cls = getattr(module, ep.attr, None)
                    if cls is None:
                        logger.warning(f"Entry point {ep} has no attribute {ep.attr}")
                        continue

                    # Determine plugin type from class name
                    if "Parser" in cls.__name__:
                        pt = PluginType.PARSER
                    elif "Renderer" in cls.__name__:
                        pt = PluginType.RENDERER
                    else:
                        pt = PluginType.EXTENSION

                    self.register(cls, pt, name=ep.name)
                    loaded += 1
                except Exception as e:
                    logger.warning(f"Failed to load plugin from {ep}: {e}")
        except Exception as e:
            logger.debug(f"Could not load entry points: {e}")

        return loaded

    def clear(self) -> None:
        """Clear all registered plugins."""
        for plugins in self._plugins.values():
            plugins.clear()


# Global registry instance
_registry = PluginRegistry()


def get_registry() -> PluginRegistry:
    """Get the global plugin registry."""
    return _registry


def register_plugin(
    cls: Type,
    plugin_type: PluginType,
    name: str = None,
    **kwargs,
) -> None:
    """Register a plugin with the global registry."""
    _registry.register(cls, plugin_type, name, **kwargs)


def list_parser_plugins() -> List[str]:
    """List all available parser plugins."""
    return _registry.list_plugins(PluginType.PARSER)


def list_renderer_plugins() -> List[str]:
    """List all available renderer plugins."""
    return _registry.list_plugins(PluginType.RENDERER)
