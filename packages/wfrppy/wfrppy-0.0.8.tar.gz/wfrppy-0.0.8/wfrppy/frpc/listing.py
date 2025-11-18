from __future__ import annotations

from ..core.listing import list_config_profiles
from ..core.winsvc import ensure_admin
from ._shared import (
    DEFAULT_CONFIG_NAME,
    _load_state_optional,
    _resolve_install_dir,
    _service_name,
    _service_state,
)


def frpc_list() -> int:
    ensure_admin()
    return list_config_profiles(
        program_name="frpc",
        load_state_optional=_load_state_optional,
        resolve_install_dir=_resolve_install_dir,
        build_service_name=_service_name,
        default_config=DEFAULT_CONFIG_NAME,
        status_fetcher=_service_state,
        headers=("配置", "默认", "计划任务 URI", "计划任务状态", "上次运行时间", "上次运行结果"),
    )
