"""Plugin loader for dynamic command discovery and registration.

This module handles discovering, loading, and registering command plugins
from both the built-in plugins directory and external sources via entry points.
"""

import importlib.metadata
import importlib.util
import logging
from pathlib import Path
from typing import TYPE_CHECKING

import click

from ei_cli.plugins.base import CommandPlugin

if TYPE_CHECKING:
    from collections.abc import Iterator

logger = logging.getLogger(__name__)


class PluginLoader:
    """Discovers and loads command plugins dynamically.

    The loader finds plugins from two sources:
    1. Built-in plugins from the plugins directory
    2. External plugins registered via entry points

    Attributes:
        plugins: Dictionary mapping command names to plugin instances
    """

    ENTRY_POINT_GROUP = "eai.plugins"

    def __init__(self) -> None:
        """Initialize the plugin loader."""
        self.plugins: dict[str, CommandPlugin] = {}

    def discover_plugins(self) -> None:
        """Discover all available plugins from built-in and external sources."""
        self._discover_builtin_plugins()
        self._discover_entry_point_plugins()
        logger.info("Discovered %d plugins", len(self.plugins))

    def _discover_builtin_plugins(self) -> None:
        """Discover plugins from the built-in plugins directory."""
        plugins_dir = Path(__file__).parent
        logger.debug("Scanning for built-in plugins in: %s", plugins_dir)

        for plugin_file in plugins_dir.glob("*.py"):
            # Skip special files
            if plugin_file.stem in {"__init__", "base", "loader"}:
                continue

            try:
                self._load_plugin_module(plugin_file)
            except Exception:
                logger.exception("Failed to load plugin from %s", plugin_file)

    def _load_plugin_module(self, plugin_file: Path) -> None:
        """Load a plugin from a Python file.

        Args:
            plugin_file: Path to the plugin module file
        """
        module_name = f"ei_cli.plugins.{plugin_file.stem}"
        spec = importlib.util.spec_from_file_location(module_name, plugin_file)

        if spec is None or spec.loader is None:
            logger.warning("Could not load spec for %s", plugin_file)
            return

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Look for plugin instance named 'plugin' in module
        if hasattr(module, "plugin"):
            plugin = module.plugin
            if isinstance(plugin, CommandPlugin):
                self._register_plugin(plugin)
            else:
                logger.warning(
                    "Found 'plugin' in %s but not a CommandPlugin",
                    plugin_file,
                )
        else:
            logger.debug("No 'plugin' instance found in %s", plugin_file)

    def _discover_entry_point_plugins(self) -> None:
        """Discover plugins registered via setuptools entry points."""
        try:
            entry_points = importlib.metadata.entry_points()
            if hasattr(entry_points, "select"):
                # Python 3.10+
                plugin_eps = entry_points.select(group=self.ENTRY_POINT_GROUP)
            else:
                # Python 3.9
                plugin_eps = entry_points.get(self.ENTRY_POINT_GROUP, [])

            for ep in plugin_eps:
                try:
                    plugin_class = ep.load()
                    plugin = plugin_class()
                    self._register_plugin(plugin)
                except Exception:
                    logger.exception("Failed to load plugin from entry point: %s", ep.name)

        except Exception:
            logger.exception("Failed to discover entry point plugins")

    def _register_plugin(self, plugin: CommandPlugin) -> None:
        """Register a plugin instance.

        Args:
            plugin: The plugin instance to register
        """
        if plugin.name in self.plugins:
            logger.warning("Plugin '%s' is already registered, skipping", plugin.name)
            return

        self.plugins[plugin.name] = plugin
        logger.debug("Registered plugin: %s (category: %s)", plugin.name, plugin.category)

    def register_commands(self, cli_group: click.Group) -> None:
        """Register all discovered plugins as Click commands.

        Args:
            cli_group: The Click group to register commands with
        """
        for plugin in self.plugins.values():
            try:
                command = plugin.get_command()
                cli_group.add_command(command, name=plugin.name)
                logger.debug("Registered command: %s", plugin.name)
            except Exception:
                logger.exception("Failed to register command: %s", plugin.name)

    def get_plugins_by_category(self) -> dict[str, list[CommandPlugin]]:
        """Group plugins by category for organized help display.

        Returns:
            Dictionary mapping category names to lists of plugins
        """
        categories: dict[str, list[CommandPlugin]] = {}

        for plugin in self.plugins.values():
            category = plugin.category
            if category not in categories:
                categories[category] = []
            categories[category].append(plugin)

        # Sort plugins within each category by name
        for plugins in categories.values():
            plugins.sort(key=lambda p: p.name)

        return categories

    def get_plugin(self, name: str) -> CommandPlugin | None:
        """Get a plugin by name.

        Args:
            name: The command name

        Returns:
            The plugin instance, or None if not found
        """
        return self.plugins.get(name)

    def iter_plugins(self) -> "Iterator[CommandPlugin]":
        """Iterate over all registered plugins.

        Yields:
            Plugin instances
        """
        yield from self.plugins.values()
