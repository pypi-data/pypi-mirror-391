"""
命令注册中心，负责调度 wfrppy 中的所有子命令并管理依赖。
"""
from __future__ import annotations

import importlib
import os
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple

sys.modules.setdefault("wfrppy.core.registry", sys.modules[__name__])


class CommandNotFoundError(LookupError):
    """请求的命令未注册时抛出。"""


class MissingDependencyError(RuntimeError):
    """命令缺少依赖包时抛出。"""


@dataclass(frozen=True)
class Dependency:
    """
    pip 依赖描述。

    package: pip 安装包名称。
    import_name: 依赖校验时导入的模块，默认与 package 相同。
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
    """记录安装或钩子执行的结果。"""

    kind: str
    target: str
    success: bool
    detail: str = ""


@dataclass
class CommandSpec:
    """命令元数据定义。"""

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
        依次执行 pip 安装与自定义钩子，返回每一步的执行结果。
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
            detail = "安装成功" if success else f"安装失败（退出码 {completed.returncode}）"
            reports.append(
                InstallReport(kind="pip", target=dep.package, success=success, detail=detail)
            )

        for installer in self.installers:
            hook_name = getattr(installer, "__name__", "custom_install")
            try:
                message = installer(upgrade)
                detail = message or "执行完成"
                reports.append(InstallReport(kind="hook", target=hook_name, success=True, detail=detail))
            except Exception as exc:  # pragma: no cover
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
    """命令注册表，实现自动发现、执行及依赖检查。"""

    def __init__(self) -> None:
        self._commands: Dict[str, CommandSpec] = {}
        self._aliases: Dict[str, str] = {}
        self._discovered = False

    # 注册 ---------------------------------------------------------
    def register(self, spec: CommandSpec) -> None:
        if spec.name in self._commands:
            raise ValueError(f"命令“{spec.name}”已注册。")
        qualified_aliases = set()
        for alias in spec.aliases:
            if alias in self._commands or alias in self._aliases:
                raise ValueError(f"别名“{alias}”已被占用。")
            qualified_aliases.add(alias)

        self._commands[spec.name] = spec
        for alias in qualified_aliases:
            self._aliases[alias] = spec.name

    # 发现 ---------------------------------------------------------
    def discover(self) -> None:
        """
        自动导入顶层包下的子模块，使其在 import 时完成命令注册。
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

    # 查询 ---------------------------------------------------------
    def _resolve_name(self, name: str) -> str:
        if name in self._commands:
            return name
        if name in self._aliases:
            return self._aliases[name]
        raise CommandNotFoundError(f"未知命令“{name}”。")

    def get(self, name: str) -> CommandSpec:
        return self._commands[self._resolve_name(name)]

    def list_commands(self) -> List[CommandSpec]:
        return sorted(self._commands.values(), key=lambda spec: spec.name)

    def iter_commands(self) -> Iterable[CommandSpec]:
        return self.list_commands()

    # 执行与依赖 ---------------------------------------------------
    def ensure_ready(self, name: str) -> None:
        spec = self.get(name)
        missing = spec.missing_dependencies()
        if missing:
            missing_pkgs = ", ".join(dep.package for dep in missing)
            raise MissingDependencyError(
                f"命令“{spec.name}”缺少依赖：{missing_pkgs}。\n"
                f"请先安装“{spec.name}”所需依赖后再重试。"
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
    注册命令的便捷函数。
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
