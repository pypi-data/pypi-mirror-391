from __future__ import annotations

import sys
from pathlib import Path

from ._shared import DEFAULT_INSTALL_DIR, _load_state


def frps_pwd() -> int:
    try:
        state = _load_state()
    except FileNotFoundError as exc:
        print(exc, file=sys.stderr)
        return 1

    target = Path(state.get("install_dir", DEFAULT_INSTALL_DIR)).expanduser()
    if not target.exists():
        print(f"部署目录 {target} 不存在，请重新执行 frps deploy。", file=sys.stderr)
        return 1

    print(target)
    return 0
