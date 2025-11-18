"""
frps 命令集合：负责部署目录、配置文件以及 Windows 计划任务的统一入口。
"""
from __future__ import annotations

import argparse
from typing import Optional, Sequence

from ..core.config_ops import resolve_config_name
from ..core.registry import register_command
from ._shared import DEFAULT_CONFIG_NAME, DEFAULT_INSTALL_DIR, FRP_VERSION
from .cleanup import frps_cleanup
from .deploy import frps_deploy
from .file_ops import frps_edit, frps_show
from .listing import frps_list
from .pwd import frps_pwd
from .tasks import frps_addtask, frps_rmtask


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="frps",
        description="Windows 上的 frps 管理工具，提供部署、配置与计划任务导入能力。",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    deploy = subparsers.add_parser("deploy", help="部署或刷新 frps 安装目录")
    deploy.add_argument(
        "install_dir",
        nargs="?",
        default=DEFAULT_INSTALL_DIR,
        help=f"安装目录，默认 {DEFAULT_INSTALL_DIR}",
    )
    deploy.add_argument("--overwrite", action="store_true", help="覆盖已存在的安装目录")
    deploy.add_argument(
        "--no-service",
        dest="register_service",
        action="store_false",
        help="仅写入文件，不创建计划任务（需后续 addtask 手动导入）",
    )
    deploy.add_argument(
        "--auto-start",
        action="store_true",
        help="部署完成后即为默认配置创建开机自启的计划任务",
    )
    deploy.set_defaults(register_service=True)

    cleanup = subparsers.add_parser("cleanup", help="清理 frps 部署记录")
    cleanup.add_argument("--keep-dir", action="store_true", help="保留安装目录")
    cleanup.add_argument("--keep-service", action="store_true", help="保留已创建的计划任务")

    subparsers.add_parser("list", help="列出配置文件及计划任务状态")
    subparsers.add_parser("pwd", help="显示当前的部署目录")

    edit_parser = subparsers.add_parser("edit", aliases=["vim"], help="使用记事本编辑配置文件")
    edit_parser.add_argument("name", nargs="?", default=None, help="配置名称，默认为 main")

    show_parser = subparsers.add_parser("show", aliases=["cat"], help="在终端打印配置内容")
    show_parser.add_argument("name", nargs="?", default=None, help="配置名称，默认为 main")

    addtask = subparsers.add_parser("addtask", help="根据模板导入计划任务")
    addtask.add_argument("name", nargs="?", default=None, help="配置名称，默认为 main")

    rmtask = subparsers.add_parser("rmtask", help="删除对应的计划任务")
    rmtask.add_argument("name", nargs="?", default=None, help="配置名称，默认为 main")

    return parser


def frps_main(argv: Optional[Sequence[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "deploy":
        return frps_deploy(
            args.install_dir,
            overwrite=args.overwrite,
            register_service=args.register_service,
            auto_start=args.auto_start,
        )

    if args.command == "cleanup":
        return frps_cleanup(keep_dir=args.keep_dir, keep_service=args.keep_service)

    if args.command == "list":
        return frps_list()

    if args.command == "pwd":
        return frps_pwd()

    if args.command in {"edit", "vim"}:
        name = resolve_config_name("frps edit", args.name, default=DEFAULT_CONFIG_NAME)
        return frps_edit(name)

    if args.command in {"show", "cat"}:
        name = resolve_config_name("frps show", args.name, default=DEFAULT_CONFIG_NAME)
        return frps_show(name)

    if args.command == "addtask":
        name = resolve_config_name("frps addtask", args.name, default=DEFAULT_CONFIG_NAME)
        return frps_addtask(name)

    if args.command == "rmtask":
        name = resolve_config_name("frps rmtask", args.name, default=DEFAULT_CONFIG_NAME)
        return frps_rmtask(name)

    parser.print_help()
    return 0


register_command(
    name="frps",
    handler=frps_main,
    description="frps 命令入口（Windows 计划任务部署）",
    usage="frps <命令> [选项]",
    examples=(
        "frps deploy",
        "frps addtask main",
        "frps rmtask main",
        "frps list",
        "frps cleanup --keep-dir",
    ),
    notes=(
        f"内置 FRP 版本：{FRP_VERSION}",
        "计划任务相关命令需要管理员权限，请在管理员 PowerShell 中执行。",
        "计划任务名称遵循 \\\\frp\\\\frps-<名称> 约定，与 <名称>.toml 对应。",
    ),
    module=__name__,
)
