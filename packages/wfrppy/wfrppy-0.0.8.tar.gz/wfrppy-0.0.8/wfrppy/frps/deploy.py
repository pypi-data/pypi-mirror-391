from __future__ import annotations

import shutil
from pathlib import Path
from textwrap import dedent

from ._shared import (
    DEFAULT_CONFIG_NAME,
    DEFAULT_INSTALL_DIR,
    RESOURCE_DIR,
    _load_state_optional,
    _mark_not_deployed,
    _register_service,
    _resolve_install_dir,
    _save_state,
    _write_text,
)


def _copy_templates(target_dir: Path) -> None:
    primary = RESOURCE_DIR / "main.toml"
    if primary.exists():
        _write_text(target_dir / "main.toml", primary.read_text(encoding="utf-8"))


def frps_deploy(
    install_dir: str,
    *,
    overwrite: bool,
    register_service: bool,
    auto_start: bool,
) -> int:
    target_dir = Path(install_dir or DEFAULT_INSTALL_DIR).expanduser().resolve()
    existing_state = _load_state_optional()
    stored_dir = _resolve_install_dir(existing_state)

    if existing_state and stored_dir and stored_dir != target_dir and not overwrite:
        print(f"检测到已有部署目录 {stored_dir}，请先执行 frps cleanup 或使用 --overwrite 强制覆盖。")
        return 1

    if target_dir.exists():
        if not overwrite:
            print(f"目录 {target_dir} 已存在，使用 --overwrite 以重新部署。")
            return 1
        try:
            shutil.rmtree(target_dir)
        except OSError as exc:
            print(f"无法删除目录 {target_dir}：{exc}")
            return 1
        _mark_not_deployed()

    target_dir.mkdir(parents=True, exist_ok=True)
    (target_dir / "logs").mkdir(parents=True, exist_ok=True)
    _copy_templates(target_dir)

    readme = dedent(
        f"""frps 部署完成

安装目录：{target_dir}

目录内容：
  - main.toml               默认配置模板
  - logs/                   日志目录

常用命令：
  frps list                查看配置及计划任务状态
  frps edit <名称>         使用记事本编辑配置
  frps addtask <名称>      基于模板导入计划任务
  frps rmtask <名称>       删除对应计划任务
  frps cleanup             清理部署目录及计划任务

说明：
  - 首次执行 addtask 时会自动创建 \\frp\\frps-<名称> 任务。
  - 计划任务运行包内 frps.exe，配置文件以 <名称>.toml 命名。
  - 计划任务操作需在管理员 PowerShell 中执行。
"""
    )
    _write_text(target_dir / "readme.txt", readme)

    state = {
        "install_dir": str(target_dir),
        "default_config": DEFAULT_CONFIG_NAME,
    }
    _save_state(state)

    if register_service:
        print(f"已为默认配置创建计划任务 {DEFAULT_CONFIG_NAME}")
    else:
        print("已跳过计划任务创建（--no-service）。")
    return 0
