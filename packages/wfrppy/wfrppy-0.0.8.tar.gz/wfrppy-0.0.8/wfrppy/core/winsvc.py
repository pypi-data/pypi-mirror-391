"""
封装 Windows 服务（Service Control Manager）相关操作，并提供权限自动提升。
"""
from __future__ import annotations

import ctypes
import os
import shutil
import subprocess
import sys
from typing import Optional, Sequence, Tuple


NOT_WINDOWS = os.name != "nt"


def ensure_admin(argv: Optional[Sequence[str]] = None) -> None:
    """确保需要管理员权限的步骤在管理员环境下执行。"""
    if NOT_WINDOWS:
        return
    try:
        is_admin = bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:  # pragma: no cover
        is_admin = False

    if is_admin:
        return

    args = list(argv if argv is not None else sys.argv[1:])
    script_path = os.path.abspath(sys.argv[0])
    if os.path.exists(script_path):
        command = subprocess.list2cmdline([script_path, *args])
    else:
        command = subprocess.list2cmdline([sys.executable, script_path, *args])
    command = command or "frpc ..."

    print("需要管理员权限，请先安装 gsudo 并在管理员模式下运行命令：")
    print("  winget install gerardog.gsudo")
    print(f"安装完成后执行：gsudo {command}")
    sys.exit(1)

def _run_sc(args: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["sc", *args],
        check=False,
        capture_output=True,
        text=True,
    )


def service_exists(name: str) -> bool:
    if NOT_WINDOWS:
        return False
    result = _run_sc(["query", name])
    if result.returncode == 0:
        return True
    combined = (result.stdout + result.stderr).lower()
    return "1060" not in combined  # ERROR_SERVICE_DOES_NOT_EXIST


def create_service(
    name: str,
    *,
    command: str,
    working_dir: str,
    description: Optional[str],
    auto_start: bool,
) -> Tuple[bool, str]:
    if NOT_WINDOWS:
        return False, "当前系统不支持 Windows 服务。"

    ensure_admin()

    if service_exists(name):
        return True, "服务已存在，跳过创建。"

    start_mode = "auto" if auto_start else "demand"
    args = [
        "create",
        name,
        "binPath=",
        command,
        "start=",
        start_mode,
        "obj=",
        "LocalSystem",
    ]
    result = _run_sc(args)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"退出码 {result.returncode}"
        return False, detail

    if description:
        _run_sc(["description", name, description])

    return True, "服务创建成功。"


def delete_service(name: str) -> Tuple[bool, str]:
    if NOT_WINDOWS:
        return False, "当前系统不支持 Windows 服务。"
    if not service_exists(name):
        return True, "服务不存在，无需删除。"

    ensure_admin()
    result = _run_sc(["delete", name])
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"退出码 {result.returncode}"
        return False, detail
    return True, "服务已删除。"


def start_service(name: str) -> Tuple[bool, str]:
    if NOT_WINDOWS:
        return False, "当前系统不支持 Windows 服务。"
    if not service_exists(name):
        return False, "服务尚未创建。"

    ensure_admin()
    result = _run_sc(["start", name])
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"退出码 {result.returncode}"
        return False, detail
    return True, "服务已启动。"


def stop_service(name: str) -> Tuple[bool, str]:
    if NOT_WINDOWS:
        return False, "当前系统不支持 Windows 服务。"
    if not service_exists(name):
        return False, "服务尚未创建。"

    ensure_admin()
    result = _run_sc(["stop", name])
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"退出码 {result.returncode}"
        if "1062" in detail:
            return False, "服务未在运行。"
        return False, detail or "服务停止失败。"
    return True, "服务已停止。"


def set_start_mode(name: str, mode: str) -> Tuple[bool, str]:
    if NOT_WINDOWS:
        return False, "当前系统不支持 Windows 服务。"
    if mode not in {"auto", "demand", "disabled"}:
        return False, f"未知的启动模式：{mode}"
    if not service_exists(name):
        return False, "服务尚未创建。"

    ensure_admin()
    result = _run_sc(["config", name, f"start= {mode}"])
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"退出码 {result.returncode}"
        return False, detail
    readable = {"auto": "自动", "demand": "手动", "disabled": "禁用"}[mode]
    return True, f"启动模式已设置为 {readable}。"


def get_service_state(name: str) -> Tuple[str, str]:
    if NOT_WINDOWS:
        return "不支持", "不支持"
    if not service_exists(name):
        return "未创建", "未创建"

    result = _run_sc(["query", name])
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"退出码 {result.returncode}"
        return f"查询失败：{detail}", "未知"

    status = "未知"
    for line in result.stdout.splitlines():
        if "STATE" in line:
            parts = line.split(":", 1)
            if len(parts) == 2:
                status = parts[1].strip()
            break

    result_config = _run_sc(["qc", name])
    start_mode = "未知"
    if result_config.returncode == 0:
        for line in result_config.stdout.splitlines():
            if "START_TYPE" in line:
                parts = line.split(":", 1)
                if len(parts) == 2:
                    start_mode = parts[1].strip()
                break

    status_mapping = {
        "1  STOPPED": "已停止",
        "2  START_PENDING": "启动中",
        "3  STOP_PENDING": "停止中",
        "4  RUNNING": "运行中",
    }
    for key, value in status_mapping.items():
        if key in status:
            status = value
            break

    mode_mapping = {
        "AUTO_START": "自动",
        "DEMAND_START": "手动",
        "DISABLED": "禁用",
    }
    for key, value in mode_mapping.items():
        if key in start_mode:
            start_mode = value
            break

    return status, start_mode


def restart_service(name: str) -> Tuple[bool, str]:
    success, detail = stop_service(name)
    if not success and "未在运行" not in detail:
        return False, detail
    return start_service(name)
