from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path
from typing import Sequence, Tuple

from .winsvc import NOT_WINDOWS, ensure_admin


def _run_schtasks(args: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["schtasks", *args],
        check=False,
        capture_output=True,
        text=True,
    )


def _format_detail(result: subprocess.CompletedProcess[str]) -> str:
    return result.stderr.strip() or result.stdout.strip() or f"退出码 {result.returncode}"


def task_exists(name: str) -> bool:
    if NOT_WINDOWS:
        return False
    ensure_admin()
    result = _run_schtasks(["/query", "/tn", name])
    return result.returncode == 0


def _task_definition_path(name: str) -> Path:
    system_root = Path(os.environ.get("SystemRoot", r"C:\\Windows"))
    path = system_root / "System32" / "Tasks"
    parts = [part for part in re.split(r"[\\/]+", name) if part]
    for part in parts:
        path /= part
    return path


def _ensure_task_folder(name: str) -> None:
    if NOT_WINDOWS:
        return
    folder = _task_definition_path(name).parent
    if folder.exists():
        return
    ensure_admin()
    folder.mkdir(parents=True, exist_ok=True)


def create_task_from_xml(name: str, xml_path: Path) -> Tuple[bool, str]:
    if NOT_WINDOWS:
        return False, "当前系统不支持 Windows 计划任务"

    xml_file = Path(xml_path)
    if not xml_file.exists():
        return False, f"找不到计划任务模板：{xml_file}"

    ensure_admin()
    _ensure_task_folder(name)
    result = _run_schtasks(
        [
            "/Create",
            "/TN",
            name,
            "/XML",
            str(xml_file),
            "/RU",
            "SYSTEM",
            "/F",
        ]
    )
    if result.returncode != 0:
        return False, _format_detail(result)
    return True, "计划任务导入成功"


def delete_task(name: str) -> Tuple[bool, str]:
    if NOT_WINDOWS:
        return False, "当前系统不支持 Windows 计划任务"
    if not task_exists(name):
        return True, "计划任务尚未创建"

    ensure_admin()
    result = _run_schtasks(["/delete", "/tn", name, "/f"])
    if result.returncode != 0:
        return False, _format_detail(result)
    remove_task_definition_file(name)
    return True, "计划任务已删除"


def run_task(name: str) -> Tuple[bool, str]:
    if NOT_WINDOWS:
        return False, "当前系统不支持 Windows 计划任务"
    if not task_exists(name):
        return False, "计划任务尚未创建"

    ensure_admin()
    result = _run_schtasks(["/run", "/tn", name])
    if result.returncode != 0:
        detail = _format_detail(result)
        lowered = detail.lower()
        if (
            "已经在运行" in detail
            or "正在运行" in detail
            or "already running" in lowered
            or "is currently running" in lowered
        ):
            return False, "计划任务已在运行，无需重复启动"
        return False, detail
    return True, "计划任务已触发运行"


def stop_task(name: str) -> Tuple[bool, str]:
    if NOT_WINDOWS:
        return False, "当前系统不支持 Windows 计划任务"
    if not task_exists(name):
        return False, "计划任务尚未创建"

    ensure_admin()
    result = _run_schtasks(["/end", "/tn", name])
    if result.returncode != 0:
        detail = _format_detail(result)
        lowered = detail.lower()
        if (
            "没有在运行" in detail
            or "未在运行" in detail
            or "not currently running" in lowered
            or "is not currently running" in lowered
        ):
            return False, "计划任务未在运行，无需终止"
        return False, detail
    return True, "计划任务已停止"


def enable_task(name: str) -> Tuple[bool, str]:
    if NOT_WINDOWS:
        return False, "当前系统不支持 Windows 计划任务"
    if not task_exists(name):
        return False, "计划任务尚未创建"

    ensure_admin()
    result = _run_schtasks(["/change", "/tn", name, "/enable"])
    if result.returncode != 0:
        return False, _format_detail(result)
    return True, "计划任务已启用"


def disable_task(name: str) -> Tuple[bool, str]:
    if NOT_WINDOWS:
        return False, "当前系统不支持 Windows 计划任务"
    if not task_exists(name):
        return False, "计划任务尚未创建"

    ensure_admin()
    result = _run_schtasks(["/change", "/tn", name, "/disable"])
    if result.returncode != 0:
        return False, _format_detail(result)
    return True, "计划任务已禁用"


def _format_last_result(value: str) -> str:
    trimmed = value.strip()
    if not trimmed or trimmed.lower() == "n/a":
        return trimmed or "未知"
    try:
        code = int(trimmed, 0)
    except ValueError:
        return trimmed
    if code == 0:
        return f"成功 ({code})"
    return f"失败 ({code})"


def task_state(name: str) -> Tuple[str, str, str]:
    if NOT_WINDOWS:
        return "不支持", "不支持", "不支持"
    if not task_exists(name):
        return "未部署", "未部署", "未部署"
    ensure_admin()

    result = _run_schtasks(["/query", "/tn", name, "/fo", "LIST", "/v"])
    if result.returncode != 0:
        detail = _format_detail(result)
        return f"查询失败：{detail}", "未知", "未知"

    status = "未知"
    last_run = "未知"
    last_result = "未知"
    status_tokens = ("status", "状态", "模式")
    last_run_tokens = ("last run time", "上次运行时间")
    last_result_tokens = ("last result", "上次结果")
    next_run_tokens = ("next run time", "下一次运行时间", "下次运行时间")

    for raw in result.stdout.splitlines():
        line = raw.strip()
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        original_key = key.strip()
        lowered_key = original_key.lower()
        value = value.strip() or "未知"

        if any(token in lowered_key or token in original_key for token in status_tokens):
            if status in {"未知", "未部署"}:
                status = value
            continue

        if any(token in lowered_key or token in original_key for token in last_run_tokens):
            if last_run in {"未知", "未部署"}:
                last_run = value
            continue

        if any(token in lowered_key or token in original_key for token in last_result_tokens):
            if last_result in {"未知", "未部署"}:
                last_result = _format_last_result(value)
            continue

        if any(token in lowered_key or token in original_key for token in next_run_tokens):
            if last_run in {"未知", "未部署"}:
                last_run = value

    return status, last_run, last_result


def remove_task_definition_file(name: str) -> None:
    if NOT_WINDOWS:
        return
    path = _task_definition_path(name)
    ensure_admin()
    try:
        path.unlink()
    except FileNotFoundError:
        return
