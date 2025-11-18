from __future__ import annotations

import shutil
import subprocess
from typing import Tuple


def get_unit_state(unit: str) -> Tuple[str, str]:
    """
    Return the active and enabled state for a systemd unit in Chinese descriptions.
    """
    if shutil.which("systemctl") is None:
        unavailable = "systemctl 不可用"
        return unavailable, unavailable

    active = _query_active_state(unit)
    enabled = _query_enabled_state(unit)
    return active, enabled


def _query_active_state(unit: str) -> str:
    command = ["systemctl", "show", unit, "--property=ActiveState,SubState", "--no-page"]
    try:
        result = subprocess.run(
            command,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except FileNotFoundError:
        return "systemctl 不可用"

    if result.returncode != 0:
        return (result.stderr.strip() or f"错误 {result.returncode}") or "未知"

    state_map: dict[str, str] = {}
    for line in result.stdout.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            state_map[key.strip()] = value.strip()

    active = state_map.get("ActiveState", "").strip()
    sub = state_map.get("SubState", "").strip()
    return _translate_active_state(active, sub)


def _query_enabled_state(unit: str) -> str:
    command = ["systemctl", "is-enabled", unit]
    try:
        result = subprocess.run(
            command,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except FileNotFoundError:
        return "systemctl 不可用"

    output = (result.stdout.strip() or result.stderr.strip()).strip()
    if result.returncode == 0:
        return _translate_enabled_state(output or "unknown")
    return _translate_enabled_state(output or f"错误 {result.returncode}")


def _translate_active_state(active: str, sub: str) -> str:
    mapping = {
        "active": "运行中",
        "inactive": "已停止",
        "activating": "启动中",
        "deactivating": "停止中",
        "failed": "失败",
        "reloading": "重新加载中",
    }
    status = mapping.get(active, active or "未知")
    if sub and sub != active:
        return f"{status}（{sub}）"
    return status


def _translate_enabled_state(value: str) -> str:
    mapping = {
        "enabled": "已启用",
        "disabled": "未启用",
        "static": "静态（不可启用）",
        "indirect": "间接启用",
        "generated": "生成",
        "masked": "已屏蔽",
        "linked": "已链接",
        "unlinked": "未链接",
        "bad": "损坏",
    }
    return mapping.get(value, value or "未知")
