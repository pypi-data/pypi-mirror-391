from __future__ import annotations

from pathlib import Path

from ..core.winsvc import service_exists, get_service_state
from ._shared import (
    DEFAULT_INSTALL_DIR,
    _config_path,
    _disable_service,
    _enable_service,
    _ensure_service_ready,
    _load_state_optional,
    _resolve_install_dir,
    _service_name,
    _start_service,
    _stop_service,
    _restart_service,
)


def frps_service_action(action: str, name: str) -> int:
    state = _load_state_optional()
    if not state:
        print("未检测到 frps 部署记录，无法执行服务相关操作。")
        return 1

    install_dir = _resolve_install_dir(state) or Path(DEFAULT_INSTALL_DIR).expanduser()
    config_path = _config_path(install_dir, name)
    service = _service_name(name)

    if action in {"start", "restart", "enable"} and not config_path.exists():
        print(f"配置文件 {config_path} 不存在，无法执行操作：{action}。")
        return 1

    if action in {"start", "restart", "enable"}:
        auto_start = action == "enable"
        if not _ensure_service_ready(name, install_dir=install_dir, auto_start=auto_start):
            return 1

    if action == "start":
        success, detail = _start_service(name)
        if not success:
            print(f"服务 {service} 启动失败：{detail}")
            return 1
        print(f"服务 {service} 已启动。")
        return 0

    if action == "stop":
        if not service_exists(service):
            print(f"服务 {service} 尚未创建。")
            return 1
        success, detail = _stop_service(name)
        if not success:
            print(f"停止服务 {service} 失败：{detail}")
            return 1
        print(f"服务 {service} 已停止。")
        return 0

    if action == "restart":
        success, detail = _restart_service(name)
        if not success:
            print(f"重新启动服务 {service} 失败：{detail}")
            return 1
        print(f"服务 {service} 已重新启动。")
        return 0

    if action == "status":
        status, start_mode = get_service_state(service)
        print(f"{service}：当前状态={status}，启动类型={start_mode}")
        return 0

    if action == "enable":
        success, detail = _enable_service(name)
        if not success:
            print(f"启用服务 {service} 失败：{detail}")
            return 1
        print(f"服务 {service} 已设置为开机自启。")
        return 0

    if action == "disable":
        if not service_exists(service):
            print(f"服务 {service} 尚未创建。")
            return 1
        success, detail = _disable_service(name)
        if not success:
            print(f"禁用服务 {service} 失败：{detail}")
            return 1
        print(f"服务 {service} 已禁用。")
        return 0

    print(f"未知操作：{action}")
    return 1