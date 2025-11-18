from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Optional

import lfrppy.bin as bin_pkg

from ._shared import (
    RESOURCE_DIR,
    _mark_not_deployed,
    _save_state,
    _systemctl_daemon_reload,
    _write_text,
    _load_state_optional,
)


def frps_deploy(
    install_dir: str,
    *,
    service_user: Optional[str],
    systemd_dir: str,
    overwrite: bool,
    install_service: bool,
) -> int:
    target_dir = Path(install_dir).expanduser().resolve()
    systemd_path = Path(systemd_dir).expanduser().resolve()
    existing_state = _load_state_optional()

    stored_dir: Optional[Path] = None
    if existing_state:
        raw_dir = existing_state.get("install_dir")
        if raw_dir:
            stored_dir = Path(raw_dir).expanduser().resolve()

    if existing_state:
        if stored_dir and stored_dir != target_dir:
            print(f"Deployment already exists at {stored_dir}. Run `frps cleanup` before switching directories.")
            return 1
        if not overwrite:
            print("Deployment already exists. Run `frps cleanup` or use --overwrite to redeploy in the same directory.")
            return 1
    else:
        if target_dir.exists() and not overwrite:
            print(f"Install directory {target_dir} already exists. Run `frps cleanup` or add --overwrite.")
            return 1

    if target_dir.exists():
        try:
            shutil.rmtree(target_dir)
        except PermissionError:
            print(f"Unable to remove existing directory {target_dir} (permission denied). Try using sudo.")
            return 1
        except OSError as exc:
            print(f"Unable to remove existing directory {target_dir}: {exc}")
            return 1

    if existing_state and overwrite:
        _mark_not_deployed()

    target_dir.mkdir(parents=True, exist_ok=True)
    logs_dir = target_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    package_binary_dir = Path(getattr(bin_pkg, "__file__", __file__)).resolve().parent
    package_binary = package_binary_dir / "frps"
    if not package_binary.exists():
        print("Embedded frps binary not found.")
        return 1
    try:
        package_binary.chmod(0o555)
    except PermissionError:
        print(f"Permission denied when setting mode 0o555 on {package_binary}.")

    _write_text(
        target_dir / "main.toml",
        (RESOURCE_DIR / "main.toml").read_text(encoding="utf-8"),
        mode=0o666,
    )
    _write_text(
        target_dir / "frps_full_example.toml",
        (RESOURCE_DIR / "frps_full_example.toml").read_text(encoding="utf-8"),
        mode=0o666,
    )

    service_template = (RESOURCE_DIR / "systemd" / "frps@.service").read_text(encoding="utf-8")
    replacer = {
        "<user>": service_user or os.getenv("USER", "frp"),
        "<dir>": str(target_dir),
        "<bin_dir>": str(package_binary_dir),
    }
    for key, value in replacer.items():
        service_template = service_template.replace(key, value)

    template_hint = (
        f"systemd template installed to: {systemd_path / 'frps@.service'}"
        if install_service
        else "systemd template not installed (--no-service)."
    )
    readme = (
        "frps deployment completed\n\n"
        f"Install directory: {target_dir}\n\n"
        "Contents:\n"
        "  - main.toml (mode 0666; copy and edit)\n"
        "  - frps_full_example.toml (mode 0666; full options)\n"
        "  - logs/ (empty directory for log files)\n\n"
        "Quick start:\n"
        "  1. Copy a template to <name>.toml (for example example.toml).\n"
        "  2. Edit the config, then use `cd $(frps pwd)` to inspect the directory.\n"
        "  3. Start service: sudo systemctl start frps@<name>\n"
        "  4. Enable at boot: sudo systemctl enable frps@<name>\n"
        "  5. Check status: sudo systemctl status frps@<name>\n"
        "  6. Stop service: sudo systemctl stop frps@<name>\n"
        "  7. Disable service: sudo systemctl disable frps@<name>\n\n"
        "Maintenance:\n"
        "  - Run sudo systemctl daemon-reload after editing templates.\n"
        "  - Use `frps cleanup` to remove installs and templates (sudo may be required).\n"
        "  - Re-deploy with --overwrite to replace existing files.\n\n"
        f"{template_hint}\n"
    )
    _write_text(target_dir / "readme.txt", readme)

    if install_service:
        service_destination = systemd_path / "frps@.service"
        try:
            _write_text(service_destination, service_template)
            print(f"systemd template written to {service_destination}")
        except PermissionError:
            print(
                f"Permission denied when writing {service_destination}. "
                "Run again with sudo or copy the file manually."
            )
        _systemctl_daemon_reload()

    print("frps deployment completed.")
    print(f"Binary (package): {package_binary}")
    print(f"Example config: {target_dir / 'main.toml'}")
    if install_service:
        print(f"Systemd template: {service_destination}")
    else:
        print("Systemd template installation skipped (--no-service).")

    _save_state(
        {
            "install_dir": str(target_dir),
            "systemd_dir": str(systemd_path),
            "service_user": service_user or os.getenv("USER", "frp"),
            "bin_dir": str(package_binary_dir),
        }
    )
    return 0
