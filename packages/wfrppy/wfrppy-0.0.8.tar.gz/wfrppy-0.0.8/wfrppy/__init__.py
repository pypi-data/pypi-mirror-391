
"""
Public API for wfrppy command discovery and execution.
"""
from __future__ import annotations

from typing import Optional, Sequence
import sys


# Provide import alias without hyphen for Python modules.
sys.modules.setdefault("wfrppy", sys.modules[__name__])

from .core.registry import (
    CommandNotFoundError,
    CommandSpec,
    Dependency,
    InstallReport,
    MissingDependencyError,
    registry,
)

__all__ = [
    "CommandNotFoundError",
    "CommandSpec",
    "Dependency",
    "InstallReport",
    "MissingDependencyError",
    "discover",
    "get_command",
    "install_dependencies",
    "list_commands",
    "registry",
    "run_command",
]


def discover() -> None:
    """Import command modules and register their commands."""
    registry.discover()


def list_commands() -> Sequence[CommandSpec]:
    """Return all registered commands sorted by name."""
    discover()
    return registry.list_commands()


def get_command(name: str) -> CommandSpec:
    """Fetch a command by name, ensuring discovery has run."""
    discover()
    return registry.get(name)


def run_command(name: str, argv: Optional[Sequence[str]] = None, *, ensure_ready: bool = True):
    """Execute a command via the shared registry."""
    discover()
    return registry.run(name, argv, ensure_ready=ensure_ready)


def install_dependencies(name: str, *, upgrade: bool = False):
    """Install dependencies for the named command."""
    discover()
    return registry.install_dependencies(name, upgrade=upgrade)
