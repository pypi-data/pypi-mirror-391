"""
Central command registry and dependency management for lfrppy.
"""
from __future__ import annotations

import importlib
import os
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple

sys.modules.setdefault("lfrppy.core.registry", sys.modules[__name__])


class CommandNotFoundError(LookupError):
    """Raised when a requested command is not registered."""


class MissingDependencyError(RuntimeError):
    """Raised when a command is missing required dependencies."""


@dataclass(frozen=True)
class Dependency:
    """
    Describes a pip dependency for a command.

    package: Name passed to `pip install`.
    import_name: Module name used to verify availability (defaults to package).
    """

    package: str
    import_name: Optional[str] = None

    @property
    def module_name(self) -> str:
        return self.import_name or self.package

    def is_available(self) -> bool:
        try:
            importlib.import_module(self.module_name)
            return True
        except ModuleNotFoundError:
            return False


CliHandler = Callable[[Optional[Sequence[str]]], Optional[int]]
Installer = Callable[[bool], Optional[str]]


@dataclass
class InstallReport:
    """Represents the outcome of an installation step."""

    kind: str  # e.g. "pip" or "hook"
    target: str
    success: bool
    detail: str = ""


@dataclass
class CommandSpec:
    """Metadata describing a CLI command exposed by lfrppy."""

    name: str
    handler: CliHandler
    description: str = ""
    usage: Optional[str] = None
    examples: Sequence[str] = field(default_factory=tuple)
    notes: Sequence[str] = field(default_factory=tuple)
    dependencies: Sequence[Dependency] = field(default_factory=tuple)
    aliases: Sequence[str] = field(default_factory=tuple)
    module: Optional[str] = None
    installers: Sequence[Installer] = field(default_factory=tuple)

    def missing_dependencies(self) -> List[Dependency]:
        return [dep for dep in self.dependencies if not dep.is_available()]

    def install_dependencies(self, *, upgrade: bool = False) -> List[InstallReport]:
        """
        Install dependencies via pip followed by optional custom installers.
        Returns a list of InstallReport objects describing each step.
        """
        reports: List[InstallReport] = []
        for dep in self.dependencies:
            if dep.is_available() and not upgrade:
                reports.append(
                    InstallReport(kind="pip", target=dep.package, success=True, detail="已安装，跳过")
                )
                continue
            args = [sys.executable, "-m", "pip", "install"]
            if upgrade:
                args.append("--upgrade")
            args.append(dep.package)
            completed = subprocess.run(args, check=False)
            success = completed.returncode == 0
            detail = "安装成功" if success else f"安装失败 (退出码 {completed.returncode})"
            reports.append(
                InstallReport(kind="pip", target=dep.package, success=success, detail=detail)
            )

        for installer in self.installers:
            hook_name = getattr(installer, "__name__", "custom_install")
            try:
                message = installer(upgrade)
                detail = message or "执行完成"
                reports.append(InstallReport(kind="hook", target=hook_name, success=True, detail=detail))
            except Exception as exc:  # pragma: no cover - defensive guard
                reports.append(
                    InstallReport(
                        kind="hook",
                        target=hook_name,
                        success=False,
                        detail=f"执行失败：{exc}",
                    )
                )
        return reports

    def run(self, argv: Optional[Sequence[str]] = None) -> Optional[int]:
        return self.handler(argv)


class CommandRegistry:
    """Holds registered commands and supports discovery and execution."""

    def __init__(self) -> None:
        self._commands: Dict[str, CommandSpec] = {}
        self._aliases: Dict[str, str] = {}
        self._discovered = False

    # Registration -------------------------------------------------
    def register(self, spec: CommandSpec) -> None:
        if spec.name in self._commands:
            raise ValueError(f"Command '{spec.name}' already registered.")
        qualified_aliases = set()
        for alias in spec.aliases:
            if alias in self._commands or alias in self._aliases:
                raise ValueError(f"Alias '{alias}' already registered.")
            qualified_aliases.add(alias)

        self._commands[spec.name] = spec
        for alias in qualified_aliases:
            self._aliases[alias] = spec.name

    # Discovery ----------------------------------------------------
    def discover(self) -> None:
        """
        Import all command submodules under the top-level package.
        Each submodule is expected to register its commands on import.
        """
        if self._discovered:
            return

        package_dir = os.path.dirname(os.path.dirname(__file__))
        package_name = __name__.split(".")[0]

        for entry in os.listdir(package_dir):
            if entry.startswith((".", "_")):
                continue
            if entry == "core":
                continue
            full_path = os.path.join(package_dir, entry)
            if not os.path.isdir(full_path):
                continue
            module_init = os.path.join(full_path, "__init__.py")
            if not os.path.isfile(module_init):
                continue
            importlib.import_module(f"{package_name}.{entry}")

        self._discovered = True

    # Lookups ------------------------------------------------------
    def _resolve_name(self, name: str) -> str:
        if name in self._commands:
            return name
        if name in self._aliases:
            return self._aliases[name]
        raise CommandNotFoundError(f"Unknown command '{name}'.")

    def get(self, name: str) -> CommandSpec:
        return self._commands[self._resolve_name(name)]

    def list_commands(self) -> List[CommandSpec]:
        return sorted(self._commands.values(), key=lambda spec: spec.name)

    def iter_commands(self) -> Iterable[CommandSpec]:
        return self.list_commands()

    # Execution and dependencies ----------------------------------
    def ensure_ready(self, name: str) -> None:
        spec = self.get(name)
        missing = spec.missing_dependencies()
        if missing:
            missing_pkgs = ", ".join(dep.package for dep in missing)
            raise MissingDependencyError(
                f"Command '{spec.name}' requires missing packages: {missing_pkgs}.\n"
                f"Install the required dependencies for '{spec.name}' before retrying."
            )

    def run(self, name: str, argv: Optional[Sequence[str]] = None, *, ensure_ready: bool = True) -> Optional[int]:
        spec = self.get(name)
        if ensure_ready:
            self.ensure_ready(spec.name)
        return spec.run(argv)

    def install_dependencies(self, name: str, *, upgrade: bool = False) -> List[InstallReport]:
        spec = self.get(name)
        return spec.install_dependencies(upgrade=upgrade)


registry = CommandRegistry()


def register_command(
    *,
    name: str,
    handler: CliHandler,
    description: str = "",
    dependencies: Sequence[Dependency] = (),
    aliases: Sequence[str] = (),
    module: Optional[str] = None,
    usage: Optional[str] = None,
    examples: Sequence[str] = (),
    notes: Sequence[str] = (),
    installers: Sequence[Installer] = (),
) -> CommandSpec:
    """
    Convenience helper for registering a command. Returns the registered spec.
    """
    spec = CommandSpec(
        name=name,
        handler=handler,
        description=description,
        usage=usage,
        examples=tuple(examples),
        notes=tuple(notes),
        dependencies=tuple(dependencies),
        aliases=tuple(aliases),
        module=module,
        installers=tuple(installers),
    )
    registry.register(spec)
    return spec
