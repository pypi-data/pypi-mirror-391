from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Sequence, Callable, Optional


CommandRunner = Callable[[Sequence[str]], None]


def edit_with_vim(config_path: Path, run_command: CommandRunner, *, require_sudo: bool) -> None:
    """
    Prepare a config file and open it with vim.

    Parameters
    ----------
    config_path:
        Target configuration file.
    run_command:
        Helper that executes shell commands while handling errors.
    require_sudo:
        When True on POSIX systems, all filesystem preparation and the vim invocation
        are performed through sudo to satisfy permission requirements.
    """
    if os.name == "nt":
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.touch(exist_ok=True)
        run_command(["vim", str(config_path)])
        return

    if require_sudo:
        run_command(["sudo", "mkdir", "-p", str(config_path.parent)])
        run_command(["sudo", "touch", str(config_path)])
        run_command(["sudo", "vim", str(config_path)])
        return

    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.touch(exist_ok=True)
    run_command(["vim", str(config_path)])


def cat_config(config_path: Path, *, use_sudo_on_posix: bool) -> int:
    """
    Output the contents of a config file, optionally elevating on POSIX platforms.

    Parameters
    ----------
    config_path:
        Target configuration file.
    use_sudo_on_posix:
        When True, execute `sudo cat` on non-Windows systems to read files owned by root.

    Returns
    -------
    int
        Zero on success, otherwise the exit code from the underlying command.
    """
    if os.name == "nt" or not use_sudo_on_posix:
        try:
            print(config_path.read_text(encoding="utf-8"), end="")
        except OSError as exc:
            print(f"Unable to read {config_path}: {exc}")
            return 1
        return 0

    result = subprocess.run(["sudo", "cat", str(config_path)], check=False)
    if result.returncode != 0:
        print(f"`sudo cat {config_path}` failed (exit {result.returncode}).")
    return result.returncode


def resolve_config_name(command_label: str, provided: Optional[str], *, default: str) -> str:
    """
    Determine the configuration name for a command, notifying the user when falling back.
    """
    if provided:
        return provided
    print(f"{command_label}: 未指定配置名称，默认使用 '{default}'。")
    return default
