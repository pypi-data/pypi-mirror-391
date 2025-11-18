"""
Core infrastructure modules for lfrppy.
"""
from __future__ import annotations

import sys

sys.modules.setdefault("lfrppy.core", sys.modules[__name__])

from .cli import main as cli_main
from .entrypoints import build_console_scripts, ensure_entry_function, list_entry_functions
from .registry import (
    CommandNotFoundError,
    CommandSpec,
    Dependency,
    InstallReport,
    MissingDependencyError,
    register_command,
    registry,
)

__all__ = [
    "cli_main",
    "build_console_scripts",
    "ensure_entry_function",
    "list_entry_functions",
    "CommandNotFoundError",
    "CommandSpec",
    "Dependency",
    "InstallReport",
    "MissingDependencyError",
    "register_command",
    "registry",
]
