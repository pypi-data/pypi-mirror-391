"""EverydayAI CLI Plugin System.

This module provides the plugin infrastructure for dynamically loading
and registering CLI commands.
"""

from ei_cli.plugins.base import BaseCommandPlugin, CommandPlugin
from ei_cli.plugins.loader import PluginLoader

__all__ = [
    "BaseCommandPlugin",
    "CommandPlugin",
    "PluginLoader",
]
