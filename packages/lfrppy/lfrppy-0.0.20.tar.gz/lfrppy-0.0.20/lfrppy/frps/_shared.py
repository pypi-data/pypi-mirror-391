from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Sequence, Set

FRP_VERSION = "0.65.0"
DEFAULT_INSTALL_DIR = "~/frp/frps"
DEFAULT_SYSTEMD_DIR = "/etc/systemd/system"
STATE_FILE = Path.home() / ".frppy" / "frps_state.json"
SERVICE_ACTIONS = ("start", "stop", "restart", "status", "enable", "disable")
FILE_ACTIONS = {"vim", "cat"}
ELEVATION_ENV = "LFRPPY_FRPS_ELEVATED"
DEFAULT_CONFIG_NAME = "main"
RESOURCE_DIR = Path(__file__).resolve().parent.parent / "resources" / "frps"

__all__ = [
    "FRP_VERSION",
    "DEFAULT_INSTALL_DIR",
    "DEFAULT_SYSTEMD_DIR",
    "STATE_FILE",
    "SERVICE_ACTIONS",
    "FILE_ACTIONS",
    "ELEVATION_ENV",
    "DEFAULT_CONFIG_NAME",
    "RESOURCE_DIR",
    "_ensure_executable",
    "_write_text",
    "_save_state",
    "_run_command",
    "_run_systemctl",
    "_systemctl_daemon_reload",
    "_systemctl_collect_units",
    "_discover_frps_units",
    "_needs_privileged_write",
    "_maybe_reexec_with_sudo",
    "_load_state",
    "_load_state_optional",
    "_mark_not_deployed",
    "_resolve_install_dir",
    "_config_path",
]


def _ensure_executable(path: Path) -> None:
    current_mode = path.stat().st_mode
    path.chmod(current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def _write_text(path: Path, content: str, *, mode: Optional[int] = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    if mode is not None:
        try:
            path.chmod(mode)
        except PermissionError:
            print(f"Permission denied when setting mode {oct(mode)} on {path}.")


def _save_state(data: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _load_state() -> dict:
    if not STATE_FILE.exists():
        raise FileNotFoundError("No frps deployment record found; run frps deploy first.")
    return json.loads(STATE_FILE.read_text(encoding="utf-8"))


def _load_state_optional() -> Optional[dict]:
    if not STATE_FILE.exists():
        return None
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _mark_not_deployed() -> None:
    STATE_FILE.unlink(missing_ok=True)


def _run_command(command: Sequence[str]) -> None:
    try:
        result = subprocess.run(command, check=False)
        if result.returncode != 0:
            print(f"Command {' '.join(command)} failed (exit {result.returncode}).")
    except FileNotFoundError:
        print(f"Command '{command[0]}' not found. Skipping.")


def _run_systemctl(args: Sequence[str], *, require_sudo: bool = False) -> None:
    command: List[str] = ["systemctl", *args]
    if require_sudo and os.name != "nt":
        geteuid = getattr(os, "geteuid", None)
        if geteuid is None or geteuid() != 0:
            command = ["sudo", "-E", *command]
    _run_command(command)


def _systemctl_daemon_reload() -> None:
    if shutil.which("systemctl"):
        _run_systemctl(["daemon-reload"], require_sudo=True)


def _systemctl_collect_units(pattern: str) -> Set[str]:
    if shutil.which("systemctl") is None:
        return set()
    command = [
        "systemctl",
        "--no-legend",
        "--no-pager",
        *pattern.split(),
    ]
    try:
        result = subprocess.run(
            command,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except FileNotFoundError:
        return set()
    units: Set[str] = set()
    for line in result.stdout.splitlines():
        columns = line.split()
        if not columns:
            continue
        name = columns[0]
        if name.endswith(".service"):
            units.add(name[:-8])
    return units




def _discover_frps_units(systemd_dir: Path) -> Set[str]:
    units: Set[str] = set()
    if systemd_dir.exists():
        for path in systemd_dir.glob("frps@*.service"):
            if path.name == "frps@.service":
                continue
            units.add(path.stem)
    units.update(_systemctl_collect_units("list-units frps@*.service --type=service --all"))
    units.update(_systemctl_collect_units("list-unit-files frps@*.service"))
    return units


def _needs_privileged_write(path: Path) -> bool:
    resolved = Path(path).expanduser()
    candidate = resolved if resolved.exists() else resolved.parent
    if candidate.exists() and os.access(candidate, os.W_OK):
        return False
    if os.name == "nt":
        return True
    try:
        return resolved.resolve().is_relative_to(Path("/etc"))
    except AttributeError:
        return str(resolved.resolve()).startswith("/etc/")


def _maybe_reexec_with_sudo(systemd_dir: str, extra_paths: Sequence[Path] = ()) -> None:
    if os.name == "nt":
        return
    if os.environ.get(ELEVATION_ENV) == "1":
        return

    geteuid = getattr(os, "geteuid", None)
    if geteuid is None or geteuid() == 0:
        return

    paths_to_check: List[Path] = []
    if systemd_dir:
        paths_to_check.append(Path(systemd_dir))
    paths_to_check.extend(extra_paths)

    if not paths_to_check:
        return
    if not any(_needs_privileged_write(path) for path in paths_to_check):
        return

    env = os.environ.copy()
    env[ELEVATION_ENV] = "1"
    sudo_cmd = ["sudo", "-E", sys.argv[0], *sys.argv[1:]]
    print("Elevating permissions via sudo...")
    os.execvpe("sudo", sudo_cmd, env)


def _resolve_install_dir(state: Optional[dict]) -> Optional[Path]:
    if not state:
        return None
    install = state.get("install_dir")
    if not install:
        return None
    return Path(install).expanduser()


def _config_path(install_dir: Path, name: str) -> Path:
    return install_dir / f"{name}.toml"
