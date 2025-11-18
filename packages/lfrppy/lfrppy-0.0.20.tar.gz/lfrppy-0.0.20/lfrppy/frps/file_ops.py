from __future__ import annotations

from ..core.config_ops import cat_config, edit_with_vim
from ._shared import (
    _config_path,
    _load_state_optional,
    _resolve_install_dir,
    _run_command,
)


def frps_vim(name: str) -> int:
    state = _load_state_optional()
    install_dir = _resolve_install_dir(state)
    if install_dir is None:
        print("No frps deployment found; nothing to edit.")
        return 1

    config_path = _config_path(install_dir, name)
    edit_with_vim(config_path, _run_command, require_sudo=True)
    return 0


def frps_cat(name: str) -> int:
    state = _load_state_optional()
    install_dir = _resolve_install_dir(state)
    if install_dir is None:
        print("No frps deployment found; nothing to display.")
        return 1

    config_path = _config_path(install_dir, name)
    if not config_path.exists():
        print(f"Configuration file {config_path} not found.")
        return 1

    return cat_config(config_path, use_sudo_on_posix=False)
