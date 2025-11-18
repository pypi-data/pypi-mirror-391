from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Iterable, Optional, Sequence
import xml.etree.ElementTree as ET
from datetime import datetime
import getpass

from ..core.tasks import (
    create_task_from_xml,
    delete_task,
    disable_task,
    enable_task,
    run_task,
    stop_task,
    task_exists,
    task_state,
)

FRP_VERSION = "0.65.0"
DEFAULT_INSTALL_DIR = str(Path.home() / "frp" / "frpc")
STATE_FILE = Path.home() / ".wfrppy" / "frpc_state.json"
TASK_PREFIX = "frpc"
DEFAULT_CONFIG_NAME = "main"
RESOURCE_DIR = Path(__file__).resolve().parent.parent / "resources" / "frpc"
BIN_DIR = Path(__file__).resolve().parent.parent / "bin"
BATCH_NAME = "frpc.bat"
BIN_NAME = "frpc.exe"
TASK_TEMPLATE_FILE = BIN_DIR / "frpc_task_template.xml"
TASK_XML_CACHE_DIR = STATE_FILE.parent / "tasks"
TASK_XML_NAMESPACE = "http://schemas.microsoft.com/windows/2004/02/mit/task"

ET.register_namespace("", TASK_XML_NAMESPACE)


def _current_user() -> str:
    username = os.environ.get("USERNAME")
    if not username:
        try:
            username = getpass.getuser()
        except Exception:
            username = ""
    domain = os.environ.get("USERDOMAIN")
    if domain and username and not username.lower().startswith(domain.lower() + "\\"):
        username = f"{domain}\\{username}"
    return username or "SYSTEM"

__all__ = [
    "FRP_VERSION",
    "DEFAULT_INSTALL_DIR",
    "STATE_FILE",
    "TASK_PREFIX",
    "DEFAULT_CONFIG_NAME",
    "RESOURCE_DIR",
    "BIN_DIR",
    "BIN_NAME",
    "_write_text",
    "_save_state",
    "_load_state",
    "_load_state_optional",
    "_mark_not_deployed",
    "_resolve_install_dir",
    "_config_path",
    "_binary_path",
    "_task_name",
    "_register_task",
    "_remove_task",
    "_ensure_task_ready",
    "_stop_tasks",
    "_list_known_tasks",
    "_run_task",
    "_stop_task",
    "_enable_task",
    "_disable_task",
    "_service_name",
    "_service_exists",
    "_service_state",
    "_register_service",
    "_remove_service",
    "_ensure_service_ready",
    "_stop_services",
    "_start_service",
    "_stop_service",
    "_restart_service",
    "_enable_service",
    "_disable_service",
]


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _save_state(data: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _load_state() -> dict:
    if not STATE_FILE.exists():
        raise FileNotFoundError("未检测到 frpc 部署记录，请先执行 frpc deploy。")
    return json.loads(STATE_FILE.read_text(encoding="utf-8"))


def _load_state_optional() -> Optional[dict]:
    if not STATE_FILE.exists():
        return None
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _mark_not_deployed() -> None:
    STATE_FILE.unlink(missing_ok=True)


def _resolve_install_dir(state: Optional[dict]) -> Optional[Path]:
    if not state:
        return None
    install = state.get("install_dir")
    if not install:
        return None
    return Path(install).expanduser()


def _config_path(install_dir: Path, name: str) -> Path:
    return install_dir / f"{name}.toml"


def _binary_path() -> Path:
    candidate = BIN_DIR / BIN_NAME
    if not candidate.exists():
        raise FileNotFoundError(f"未找到内置二进制文件：{candidate}")
    return candidate


def _batch_path() -> Path:
    candidate = BIN_DIR / BATCH_NAME
    if not candidate.exists():
        raise FileNotFoundError(f"未找到计划任务批处理文件：{candidate}")
    return candidate


def _task_name(name: str) -> str:
    value = (name or "").strip()
    lowered = value.lower()
    if lowered.startswith("\\frp\\"):
        return value
    sanitized = re.sub(r"[^A-Za-z0-9_-]", "-", value)
    sanitized = sanitized.strip("-") or DEFAULT_CONFIG_NAME
    return f"\\frp\\{TASK_PREFIX}-{sanitized}"


def _resolve_task_identifier(identifier: str) -> str:
    value = (identifier or "").strip()
    lowered = value.lower()
    if lowered.startswith("\\frp\\"):
        return value
    return _task_name(value or DEFAULT_CONFIG_NAME)


def _build_command_parts(config: Path, install_dir: Path) -> tuple[str, str]:
    batch = _batch_path()
    command = f'"{batch}"'
    arguments = f'"{config.name}"'
    return command, arguments


def _task_template_path() -> Path:
    if not TASK_TEMPLATE_FILE.exists():
        raise FileNotFoundError(f"未找到计划任务模板：{TASK_TEMPLATE_FILE}")
    return TASK_TEMPLATE_FILE


def _task_xml_output_path(task_name: str) -> Path:
    safe_name = task_name.strip("\\/ ").replace("\\", "_").replace("/", "_") or TASK_PREFIX
    TASK_XML_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return TASK_XML_CACHE_DIR / f"{safe_name}.xml"


def _render_task_template(task_name: str, install_dir: Path, config: Path) -> Path:
    template = _task_template_path()
    tree = ET.parse(template)
    root = tree.getroot()
    ns = {"t": TASK_XML_NAMESPACE}
    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    user_id = _current_user()

    def _set_required_text(xpath: str, value: str) -> None:
        node = root.find(xpath, ns)
        if node is None:
            raise ValueError(f"模板缺少节点：{xpath}")
        node.text = value

    command_text, arguments_text = _build_command_parts(config, install_dir)

    placeholder_values = {
        ".//t:RegistrationInfo/t:Date": timestamp,
        ".//t:RegistrationInfo/t:Author": user_id,
        ".//t:RegistrationInfo/t:URI": task_name,
        ".//t:Triggers/t:SessionStateChangeTrigger/t:UserId": user_id,
        ".//t:Principals/t:Principal[@id='Author']/t:UserId": user_id,
        ".//t:Actions/t:Exec/t:Command": command_text,
        ".//t:Actions/t:Exec/t:WorkingDirectory": str(install_dir),
    }

    for xpath, value in placeholder_values.items():
        _set_required_text(xpath, value)

    exec_node = root.find(".//t:Actions/t:Exec", ns)
    if exec_node is None:
        raise ValueError("模板缺少 Exec 节点")
    arguments_node = exec_node.find("t:Arguments", ns)
    if arguments_node is None:
        arguments_node = ET.SubElement(exec_node, f"{{{TASK_XML_NAMESPACE}}}Arguments")
    arguments_node.text = arguments_text

    xml_path = _task_xml_output_path(task_name)
    tree.write(xml_path, encoding="utf-16", xml_declaration=True)
    return xml_path


def _register_task(name: str, *, install_dir: Path, auto_start: bool) -> bool:
    config = _config_path(install_dir, name)
    if not config.exists():
        print(f"找不到配置文件：{config}，无法创建任务。")
        return False

    task = _task_name(name)

    try:

        xml_path = _render_task_template(task, install_dir, config)

    except (FileNotFoundError, ValueError) as exc:

        print(f"无法生成计划任务模板：{exc}")

        return False



    success, detail = create_task_from_xml(task, xml_path)

    if success:

        print(f"已导入计划任务{task}")

    else:

        print(f"计划任务创建失败：{detail}")

    return success



def _remove_task(name: str) -> bool:
    task = _task_name(name)
    if not task_exists(task):
        return True
    task_path = _task_name(name)
    success, detail = _stop_task(task_path)
    detail_lower = detail.lower()
    if not success and "未在运行" not in detail and "not running" not in detail_lower:
        print(f"停止计划任务 {task} 失败：{detail}")
        return False
    success, detail = delete_task(task)
    if not success:
        print(f"删除计划任务 {task} 失败：{detail}")
        return False
    print(f"已删除计划任务{task}")
    return True


def _ensure_task_ready(name: str, *, install_dir: Path, auto_start: bool) -> bool:
    task = _task_name(name)
    if task_exists(task):
        return True
    print(f"未检测到计划任务 {task}，开始自动创建。")
    return _register_task(name, install_dir=install_dir, auto_start=auto_start)


def _stop_tasks(names: Iterable[str]) -> None:
    for name in names:
        task_path = _task_name(name)
        if not task_exists(task_path):
            continue
        success, detail = _stop_task(task_path)
        if success:
            print(f"已停止计划任务{task_path}")
        else:
            print(f"停止计划任务 {task_path} 失败：{detail}")


def _list_known_tasks(configs: Sequence[str]) -> list[tuple[str, str, str, str]]:
    rows: list[tuple[str, str, str, str]] = []
    for name in configs:
        task = _task_name(name)
        status, last_run, last_result = task_state(task)
        rows.append((name, status, last_run, last_result))
    return rows


def _run_task(name: str) -> tuple[bool, str]:
    return run_task(_task_name(name))


def _stop_task(name: str) -> tuple[bool, str]:
    return stop_task(_task_name(name))


def _enable_task(name: str) -> tuple[bool, str]:
    return enable_task(_task_name(name))


def _disable_task(name: str) -> tuple[bool, str]:
    return disable_task(_task_name(name))


def _service_name(name: str) -> str:
    return _task_name(name)


def _service_exists(name: str) -> bool:
    return task_exists(_task_name(name))


def _service_state(name: str) -> tuple[str, str, str]:
    task = _task_name(name)
    if not task_exists(task):
        return "未部署", "-", "-"
    status, last_run, last_result = task_state(task)
    return status or "未知", last_run or "-", last_result or "-"


def _register_service(name: str, *, install_dir: Path, auto_start: bool) -> bool:
    return _register_task(name, install_dir=install_dir, auto_start=auto_start)


def _remove_service(name: str) -> bool:
    return _remove_task(name)


def _ensure_service_ready(name: str, *, install_dir: Path, auto_start: bool) -> bool:
    return _ensure_task_ready(name, install_dir=install_dir, auto_start=auto_start)


def _stop_services(names: Iterable[str]) -> None:
    _stop_tasks(names)


def _start_service(name: str) -> tuple[bool, str]:
    return _run_task(name)


def _stop_service(name: str) -> tuple[bool, str]:
    return _stop_task(name)


def _restart_service(name: str) -> tuple[bool, str]:
    success, detail = _stop_service(name)
    detail_lower = detail.lower()
    if not success and "未运行" not in detail and "not running" not in detail_lower:
        return False, detail
    return _start_service(name)


def _enable_service(name: str) -> tuple[bool, str]:
    return _enable_task(name)


def _disable_service(name: str) -> tuple[bool, str]:
    return _disable_task(name)



