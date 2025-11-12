"""Base plugin infrastructure for EverydayAI CLI.

This module defines the core plugin protocol and base class that all
CLI command plugins must implement.
"""

from abc import abstractmethod
from typing import Protocol, runtime_checkable

import click


@runtime_checkable
class CommandPlugin(Protocol):
    """Protocol that all command plugins must implement.

    This protocol defines the interface for command plugins, ensuring
    type safety and consistent behavior across all plugins.
    """

    @property
    def name(self) -> str:
        """The command name (used for CLI invocation).

        Returns:
            The command name (e.g., "vision", "transcribe")
        """
        ...

    @property
    def category(self) -> str:
        """The command category for grouping in help.

        Returns:
            Category name (e.g., "AI", "Audio", "Image")
        """
        ...

    @property
    def help_text(self) -> str:
        """Short help text shown in command list.

        Returns:
            Brief description of what the command does
        """
        ...

    def get_command(self) -> click.Command:
        """Get the Click command object.

        Returns:
            A Click Command object ready for registration
        """
        ...


class BaseCommandPlugin:
    """Base class for command plugins with common functionality.

    This class provides a convenient base implementation of the CommandPlugin
    protocol. Plugins can either inherit from this class or implement the
    protocol directly for more flexibility.

    Attributes:
        name: The command name
        category: The command category for help grouping
        help_text: Short description for help output
    """

    def __init__(self, name: str, category: str, help_text: str) -> None:
        """Initialize the base plugin.

        Args:
            name: The command name
            category: The command category
            help_text: Brief help description
        """
        self._name = name
        self._category = category
        self._help_text = help_text

    @property
    def name(self) -> str:
        """The command name."""
        return self._name

    @property
    def category(self) -> str:
        """The command category."""
        return self._category

    @property
    def help_text(self) -> str:
        """Short help text."""
        return self._help_text

    @abstractmethod
    def get_command(self) -> click.Command:
        """Get the Click command object.

        This method must be implemented by subclasses to return
        the actual Click command.

        Returns:
            A Click Command object
        """
        msg = "Plugins must implement get_command()"
        raise NotImplementedError(msg)
