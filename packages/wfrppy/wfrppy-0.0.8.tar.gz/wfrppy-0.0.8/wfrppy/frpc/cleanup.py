from __future__ import annotations

import shutil
from pathlib import Path

from ._shared import (
    DEFAULT_INSTALL_DIR,
    _load_state_optional,
    _mark_not_deployed,
    _remove_service,
    _resolve_install_dir,
    _stop_services,
)


def frpc_cleanup(*, keep_dir: bool, keep_service: bool) -> int:
    state = _load_state_optional()
    if not state:
        print("未检测到 frpc 部署记录，无需清理。")
        return 0

    install_dir = _resolve_install_dir(state) or Path(DEFAULT_INSTALL_DIR).expanduser()
    exit_code = 0

    if not keep_service:
        if install_dir.exists():
            configs = sorted(path.stem for path in install_dir.glob("*.toml") if path.is_file())
        else:
            configs = [state.get("default_config", "main")]
        _stop_services(configs)
        for name in configs:
            if not _remove_service(name):
                exit_code = 1
    else:
        print("已保留计划任务（--keep-service）")

    if not keep_dir and install_dir.exists():
        try:
            shutil.rmtree(install_dir)
            print(f"已删除目录：{install_dir}")
        except OSError as exc:
            print(f"删除目录 {install_dir} 失败：{exc}")
            exit_code = 1
    elif keep_dir:
        print(f"已保留配置目录（--keep-dir）：{install_dir}")

    if exit_code == 0:
        _mark_not_deployed()
    return exit_code

