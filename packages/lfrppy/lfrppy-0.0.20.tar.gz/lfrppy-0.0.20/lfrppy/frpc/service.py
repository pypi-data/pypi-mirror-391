from __future__ import annotations

import shutil
from pathlib import Path

from ._shared import (
    DEFAULT_INSTALL_DIR,
    _load_state_optional,
    _run_systemctl,
)


def frpc_service_action(action: str, name: str) -> int:
    state = _load_state_optional()
    if not state:
        print("No frpc deployment found; service commands are unavailable.")
        return 1
    install_dir = Path(state.get("install_dir", DEFAULT_INSTALL_DIR)).expanduser()

    if action in {"start", "enable", "restart"}:
        config_path = install_dir / f"{name}.toml"
        if not config_path.exists():
            print(f"Configuration file {config_path} not found. Create it before running `frpc {action} {name}`.")
            return 1

    if shutil.which("systemctl") is None:
        print("systemctl was not found; service management commands are unavailable.")
        return 1
    unit = f"frpc@{name}"
    _run_systemctl([action, unit], require_sudo=True)
    return 0
