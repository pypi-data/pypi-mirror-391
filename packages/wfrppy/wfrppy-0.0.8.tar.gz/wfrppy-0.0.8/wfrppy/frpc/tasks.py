from __future__ import annotations

from pathlib import Path
from typing import Optional

from ..core.tasks import task_exists
from ..core.winsvc import NOT_WINDOWS
from ._shared import (
    DEFAULT_CONFIG_NAME,
    _config_path,
    _load_state_optional,
    _register_task,
    _remove_task,
    _resolve_install_dir,
    _task_name,
)


def _require_windows() -> bool:
    if NOT_WINDOWS:
        print("计划任务仅支持 Windows，请在 Windows 环境下运行。")
        return False
    return True


def _load_install_dir() -> Optional[Path]:
    state = _load_state_optional()
    if not state:
        print("尚未发现 frpc 部署记录，请先执行 `frpc deploy`。")
        return None
    install_dir = _resolve_install_dir(state)
    if not install_dir:
        print("部署记录缺少安装路径，请重新执行 `frpc deploy`。")
        return None
    if not install_dir.exists():
        print(f"安装目录 {install_dir} 不存在，请检查后重试。")
        return None
    return install_dir


def frpc_addtask(name: str) -> int:
    if not _require_windows():
        return 1
    install_dir = _load_install_dir()
    if install_dir is None:
        return 1

    target_name = name or DEFAULT_CONFIG_NAME
    config_path = _config_path(install_dir, target_name)
    if not config_path.exists():
        print(f"未找到配置文件：{config_path}")
        return 1

    success = _register_task(target_name, install_dir=install_dir, auto_start=True)
    return 0 if success else 1


def frpc_rmtask(name: str) -> int:
    if not _require_windows():
        return 1

    target_name = name or DEFAULT_CONFIG_NAME
    task = _task_name(target_name)
    if not task_exists(task):
        print(f"计划任务 {task} 尚未创建。")
        return 0

    success = _remove_task(target_name)
    return 0 if success else 1
