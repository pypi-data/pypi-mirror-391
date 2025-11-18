from __future__ import annotations

from ..core.listing import list_config_profiles
from ._shared import (
    DEFAULT_CONFIG_NAME,
    _load_state_optional,
    _resolve_install_dir,
)


def frpc_list() -> int:
    return list_config_profiles(
        program_name="frpc",
        load_state_optional=_load_state_optional,
        resolve_install_dir=_resolve_install_dir,
        unit_prefix="frpc@",
        default_config=DEFAULT_CONFIG_NAME,
    )
