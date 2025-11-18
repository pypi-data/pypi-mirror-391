"""
通用命令入口，负责在运行时分发 wfrppy 中注册的命令。
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional, Sequence

from .registry import CommandNotFoundError, MissingDependencyError


def _print_available_commands() -> None:
    from .. import list_commands

    print("可用命令：")
    for spec in list_commands():
        summary = spec.description or ""
        print(f"  {spec.name:<7} {summary}")
    print("\n示例：")
    print("  frpc deploy --help")
    print("  frps cleanup --help")


def main(argv: Optional[Sequence[str]] = None) -> int:
    from .. import run_command

    args = list(argv if argv is not None else sys.argv[1:])
    invoked = Path(sys.argv[0]).name.lower()

    if invoked in {"frpc", "frps"}:
        try:
            result = run_command(invoked, args)
        except MissingDependencyError as exc:
            print(exc)
            return 1
        except CommandNotFoundError:
            print(f"未知命令：{invoked}")
            return 1
        return result or 0

    if not args or args[0] in {"-h", "--help"}:
        _print_available_commands()
        return 0

    command = args[0]
    command_args = args[1:]

    try:
        result = run_command(command, command_args)
    except MissingDependencyError as exc:
        print(exc)
        return 1
    except CommandNotFoundError:
        print(f"未知命令：{command}。请运行 frpc --help 或 frps --help 查看使用说明。")
        return 1

    return result or 0


if __name__ == "__main__":
    raise SystemExit(main())
