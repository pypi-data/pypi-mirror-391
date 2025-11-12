from __future__ import annotations

from ..core.adb_executor import AdbExecutor


def get_state(executor: AdbExecutor, serial: str) -> str:
    return executor.get_state(serial)
