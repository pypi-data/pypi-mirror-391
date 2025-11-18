from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Sequence, Callable, Optional


CommandRunner = Callable[[Sequence[str]], None]


def edit_with_vim(config_path: Path, run_command: CommandRunner, *, require_sudo: bool) -> None:
    """
    在打开配置文件前创建目录、文件，并根据平台选择合适的编辑器。
    Windows 下使用记事本，其它平台保留原有 vim/sudo 行为。
    """
    if os.name == "nt":
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.touch(exist_ok=True)
        run_command(["notepad.exe", str(config_path)])
        return

    if require_sudo:
        run_command(["sudo", "mkdir", "-p", str(config_path.parent)])
        run_command(["sudo", "touch", str(config_path)])
        run_command(["sudo", "vim", str(config_path)])
        return

    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.touch(exist_ok=True)
    run_command(["vim", str(config_path)])


def cat_config(config_path: Path, *, use_sudo_on_posix: bool) -> int:
    """
    打印配置文件内容；在非 Windows 平台可选用 sudo 读取只读文件。
    """
    if os.name == "nt" or not use_sudo_on_posix:
        try:
            print(config_path.read_text(encoding="utf-8"), end="")
        except OSError as exc:
            print(f"无法读取 {config_path}：{exc}")
            return 1
        return 0

    result = subprocess.run(["sudo", "cat", str(config_path)], check=False)
    if result.returncode != 0:
        print(f"`sudo cat {config_path}` 执行失败（退出码 {result.returncode}）。")
    return result.returncode


def resolve_config_name(command_label: str, provided: Optional[str], *, default: str) -> str:
    """
    根据用户输入或默认值得到配置名称，并在自动回退时向用户提示。
    """
    if provided:
        return provided
    print(f"{command_label}：未指定配置名称，默认使用“{default}”。")
    return default
