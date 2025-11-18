from __future__ import annotations

from pathlib import Path
from typing import Callable, Optional, Sequence, Tuple, Union

from .winsvc import get_service_state

LoadStateFn = Callable[[], Optional[dict]]
ResolveInstallDirFn = Callable[[Optional[dict]], Optional[Path]]
ServiceNameBuilder = Callable[[str], str]
StatusFetcher = Callable[[str], Union[Sequence[str], str]]


def _collect_configs(install_dir: Path, *, extension: str = ".toml") -> list[str]:
    return sorted(
        path.stem
        for path in install_dir.glob(f"*{extension}")
        if path.is_file()
    )


def _format_table(rows: Sequence[Sequence[str]], headers: Sequence[str]) -> list[str]:
    normalized_rows = [tuple(row) for row in rows]
    columns = list(zip(*([tuple(headers)] + normalized_rows)))
    widths = [max(len(str(cell)) for cell in column) for column in columns]

    def _format_row(row: Sequence[str]) -> str:
        return " | ".join(str(value).ljust(width) for value, width in zip(row, widths))

    separator = "-+-".join("-" * width for width in widths)
    return [
        _format_row(headers),
        separator,
        *(_format_row(row) for row in normalized_rows),
    ]


def list_config_profiles(
    *,
    program_name: str,
    load_state_optional: LoadStateFn,
    resolve_install_dir: ResolveInstallDirFn,
    build_service_name: ServiceNameBuilder,
    default_config: str,
    status_fetcher: Optional[StatusFetcher] = None,
    headers: Sequence[str] = ("配置", "默认", "计划任务/服务", "状态", "附加信息"),
) -> int:
    state = load_state_optional()
    install_dir = resolve_install_dir(state)
    if install_dir is None:
        print(f"未检测到 {program_name} 的部署记录。")
        return 0

    if not install_dir.exists():
        print(f"目录 {install_dir} 不存在，请重新部署。")
        return 0

    configs = _collect_configs(install_dir)
    fetch_status = status_fetcher or get_service_state
    if not configs:
        print(f"目录 {install_dir} 中未找到 *.toml 配置文件。")
        return 0

    column_count = len(headers)
    rows: list[Tuple[str, ...]] = []

    for name in configs:
        service = build_service_name(name)
        raw_status = fetch_status(service)
        if isinstance(raw_status, (list, tuple)):
            values = list(raw_status)
        else:
            values = [str(raw_status)]
        if not values:
            values = ["未知"]

        status = values[0] or "未知"
        extras = [value or "" for value in values[1:]]
        marker = "*" if name == default_config else ""

        row = [name, marker, service, status, *extras]
        if len(row) < column_count:
            row.extend([""] * (column_count - len(row)))
        elif len(row) > column_count:
            row = row[:column_count]
        rows.append(tuple(row))

    print(f"配置目录：{install_dir}")
    for line in _format_table(rows, headers):
        print(line)
    return 0
