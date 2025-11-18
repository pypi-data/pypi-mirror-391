"""
Generate console_scripts entries dynamically for lfrppy commands.
"""
from __future__ import annotations

import sys
from typing import Dict, Iterable, List, Sequence, Tuple

sys.modules.setdefault("lfrppy.core.entrypoints", sys.modules[__name__])

from .registry import CommandNotFoundError, MissingDependencyError


def _command_to_func_name(command_name: str) -> str:
    sanitized = command_name.replace("-", "_")
    return f"command_entry_{sanitized}"


COMMAND_TO_FUNC: Dict[str, str] = {}
FUNC_TO_COMMAND: Dict[str, str] = {}


def _make_entry(command_name: str):
    def _entry() -> int:
        from .. import run_command

        try:
            result = run_command(command_name, sys.argv[1:])
        except MissingDependencyError as exc:
            print(exc)
            return 1
        except CommandNotFoundError:
            print(
                f"Unknown command '{command_name}'. Run `frpc help` or `frps help` to view available commands."
            )
            return 1
        return result or 0

    _entry.__name__ = _command_to_func_name(command_name)
    return _entry

def ensure_entry_function(command_name: str) -> str:
    existing = COMMAND_TO_FUNC.get(command_name)
    if existing:
        return existing

    func_name = _command_to_func_name(command_name)
    globals()[func_name] = _make_entry(command_name)
    COMMAND_TO_FUNC[command_name] = func_name
    FUNC_TO_COMMAND[func_name] = command_name
    return func_name


def list_entry_functions(skip: Iterable[str] = ()) -> Sequence[Tuple[str, str]]:
    from .. import list_commands

    skip_set = set(skip)
    entries: List[Tuple[str, str]] = []
    for spec in list_commands():
        if spec.name in skip_set:
            continue
        func_name = ensure_entry_function(spec.name)
        entries.append((spec.name, func_name))
    return entries


def build_console_scripts(skip: Iterable[str] = (), prefix: str = "") -> List[str]:
    scripts: List[str] = []
    for command_name, func_name in list_entry_functions(skip=skip):
        script_name = f"{prefix}{command_name}"
        scripts.append(f"{script_name}=lfrppy.core.entrypoints:{func_name}")
    return scripts
