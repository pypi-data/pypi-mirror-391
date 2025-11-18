"""
Command suite for managing the FRP server (frps).
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional, Sequence

import lfrppy.bin as bin_pkg

from ..core.config_ops import resolve_config_name
from ..core.registry import register_command
from ._shared import (
    DEFAULT_CONFIG_NAME,
    DEFAULT_INSTALL_DIR,
    DEFAULT_SYSTEMD_DIR,
    FRP_VERSION,
    SERVICE_ACTIONS,
    _load_state_optional,
    _maybe_reexec_with_sudo,
)
from .cleanup import frps_cleanup
from .deploy import frps_deploy
from .file_ops import frps_cat, frps_vim
from .listing import frps_list
from .pwd import frps_pwd
from .service import frps_service_action


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="frps",
        description="FRP server management helpers.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    deploy = subparsers.add_parser("deploy", help="Install frps and supporting files.")
    deploy.add_argument(
        "install_dir",
        nargs="?",
        default=DEFAULT_INSTALL_DIR,
        help=f"Target installation directory (default {DEFAULT_INSTALL_DIR}).",
    )
    deploy.add_argument(
        "--service-user",
        default=None,
        help="User account used by the systemd unit (defaults to current user).",
    )
    deploy.add_argument(
        "--systemd-dir",
        default=DEFAULT_SYSTEMD_DIR,
        help=f"Location to install systemd template (default {DEFAULT_SYSTEMD_DIR}).",
    )
    deploy.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing files in the install directory.",
    )
    deploy.add_argument(
        "--no-service",
        dest="install_service",
        action="store_false",
        help="Skip copying the systemd template into systemd-dir.",
    )
    deploy.set_defaults(install_service=True)

    cleanup = subparsers.add_parser("cleanup", help="Clean frps deployment artifacts.")
    cleanup.add_argument(
        "--keep-dir",
        action="store_true",
        help="Keep the install directory (removed by default).",
    )

    subparsers.add_parser("list", help="List available configuration profiles and their statuses.")
    subparsers.add_parser("pwd", help="Print the deployment directory for shell usage.")
    vim_parser = subparsers.add_parser("vim", help="Edit a configuration file using vim.")
    vim_parser.add_argument("name", nargs="?", default=None, help="Configuration name (without .toml).")

    cat_parser = subparsers.add_parser("cat", help="Print a configuration file.")
    cat_parser.add_argument("name", nargs="?", default=None, help="Configuration name (without .toml).")

    for action in SERVICE_ACTIONS:
        srv = subparsers.add_parser(action, help=f"{action} frps<name> via systemctl.")
        srv.add_argument(
            "name",
            nargs="?",
            default=None,
            help="Configuration name (maps to frps@name.service).",
        )

    return parser


def frps_main(argv: Optional[Sequence[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "deploy":
        package_binary_dir = Path(getattr(bin_pkg, "__file__", __file__)).resolve().parent
        package_binary = package_binary_dir / "frps"
        target_systemd_dir = args.systemd_dir if args.install_service else ""
        _maybe_reexec_with_sudo(target_systemd_dir, extra_paths=(package_binary,))
        return frps_deploy(
            args.install_dir,
            service_user=args.service_user,
            systemd_dir=args.systemd_dir,
            overwrite=args.overwrite,
            install_service=args.install_service,
        )

    if args.command == "cleanup":
        state = _load_state_optional()
        if not state:
            print("No frps deployment found; nothing to clean.")
            return 0
        install_dir = state.get("install_dir", DEFAULT_INSTALL_DIR)
        systemd_dir = state.get("systemd_dir", DEFAULT_SYSTEMD_DIR)
        extra_paths = [Path(install_dir)]
        if systemd_dir:
            extra_paths.append(Path(systemd_dir) / "frps@.service")
        _maybe_reexec_with_sudo(systemd_dir, extra_paths=extra_paths)
        return frps_cleanup(keep_dir=args.keep_dir)

    if args.command == "list":
        return frps_list()

    if args.command == "pwd":
        return frps_pwd()

    if args.command == "vim":
        name = resolve_config_name("frps vim", args.name, default=DEFAULT_CONFIG_NAME)
        return frps_vim(name)

    if args.command == "cat":
        name = resolve_config_name("frps cat", args.name, default=DEFAULT_CONFIG_NAME)
        return frps_cat(name)

    if args.command in SERVICE_ACTIONS:
        name = resolve_config_name(f"frps {args.command}", args.name, default=DEFAULT_CONFIG_NAME)
        return frps_service_action(args.command, name)

    parser.print_help()
    return 0


register_command(
    name="frps",
    handler=frps_main,
    description="FRP server tooling.",
    usage="frps <command> [options]",
    examples=(
        "frps deploy frps",
        "frps cleanup",
        "frps start example",
        "frps restart example",
        "frps pwd",
    ),
    notes=(
        f"Default embedded version: {FRP_VERSION}",
        "Deploy commands elevate via sudo when touching /etc/systemd/system.",
        "Service commands rely on systemctl; guidance is printed if it is missing.",
    ),
    module=__name__,
)
