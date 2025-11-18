from __future__ import annotations

from pathlib import Path
from typing import Callable, Iterable, Optional, Sequence, Tuple

from .systemd import get_unit_state


LoadStateFn = Callable[[], Optional[dict]]
ResolveInstallDirFn = Callable[[Optional[dict]], Optional[Path]]


def _collect_configs(install_dir: Path, *, extension: str = ".toml") -> list[str]:
    return sorted(
        path.stem
        for path in install_dir.glob(f"*{extension}")
        if path.is_file()
    )


def _format_table(rows: Sequence[Tuple[str, str, str, str]]) -> list[str]:
    headers = ("名称", "默认", "运行状态", "开机自启")
    columns = list(zip(*([headers] + list(rows))))
    widths = [max(len(str(cell)) for cell in column) for column in columns]

    def _format_row(row: Sequence[str]) -> str:
        return " | ".join(str(value).ljust(width) for value, width in zip(row, widths))

    separator = "-+-".join("-" * width for width in widths)
    return [
        _format_row(headers),
        separator,
        *(_format_row(row) for row in rows),
    ]


def list_config_profiles(
    *,
    program_name: str,
    load_state_optional: LoadStateFn,
    resolve_install_dir: ResolveInstallDirFn,
    unit_prefix: str,
    default_config: str,
) -> int:
    state = load_state_optional()
    install_dir = resolve_install_dir(state)
    if install_dir is None:
        print(f"No {program_name} deployment found; nothing to list.")
        return 0

    if not install_dir.exists():
        print(f"Configuration directory {install_dir} does not exist; please redeploy.")
        return 0

    configs = _collect_configs(install_dir)
    if not configs:
        print(f"No configuration files (*.toml) found under {install_dir}.")
        return 0

    rows: list[Tuple[str, str, str, str]] = []
    for name in configs:
        status, enabled = get_unit_state(f"{unit_prefix}{name}")
        marker = "是" if name == default_config else ""
        rows.append((name, marker, status, enabled))

    print(f"配置目录：{install_dir}")
    for line in _format_table(rows):
        print(line)
    return 0
