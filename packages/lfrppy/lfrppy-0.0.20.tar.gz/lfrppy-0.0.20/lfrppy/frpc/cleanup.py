from __future__ import annotations

import shutil
from pathlib import Path

from ._shared import (
    DEFAULT_INSTALL_DIR,
    DEFAULT_SYSTEMD_DIR,
    _discover_frpc_units,
    _load_state_optional,
    _mark_not_deployed,
    _run_systemctl,
    _systemctl_daemon_reload,
)


def frpc_cleanup(*, keep_dir: bool) -> int:
    state = _load_state_optional()
    if not state:
        print("No frpc deployment found; nothing to clean.")
        return 0
    install_path = Path(state.get("install_dir", DEFAULT_INSTALL_DIR)).expanduser().resolve()
    systemd_path = Path(state.get("systemd_dir", DEFAULT_SYSTEMD_DIR)).expanduser().resolve()

    exit_code = 0

    service_units = _discover_frpc_units(systemd_path)

    _run_systemctl(["stop", "frpc"], require_sudo=True)
    _run_systemctl(["disable", "frpc"], require_sudo=True)

    for svc in sorted(service_units):
        _run_systemctl(["stop", svc], require_sudo=True)
        _run_systemctl(["disable", svc], require_sudo=True)

    for svc in sorted(service_units):
        unit_file = systemd_path / f"{svc}.service"
        if unit_file.exists():
            try:
                unit_file.unlink()
                print(f"Removed {unit_file}")
            except PermissionError:
                print(f"Permission denied when removing {unit_file}.")
                exit_code = 1

    template_file = systemd_path / "frpc@.service"
    if template_file.exists():
        try:
            template_file.unlink()
            print(f"Removed {template_file}")
        except PermissionError:
            print(f"Permission denied when removing {template_file}.")
            exit_code = 1

    base_service = systemd_path / "frpc.service"
    if base_service.exists():
        try:
            base_service.unlink()
            print(f"Removed {base_service}")
        except PermissionError:
            print(f"Permission denied when removing {base_service}.")
            exit_code = 1

    _systemctl_daemon_reload()

    if not keep_dir and install_path.exists():
        try:
            shutil.rmtree(install_path)
            print(f"Removed directory {install_path}")
        except PermissionError:
            print(f"Permission denied when removing directory {install_path}.")
            exit_code = 1
        except OSError as exc:
            print(f"Failed removing directory {install_path}: {exc}")
            exit_code = 1

    if exit_code == 0:
        _mark_not_deployed()

    return exit_code
