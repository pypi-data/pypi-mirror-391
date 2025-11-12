from __future__ import annotations

from ..core.adb_executor import AdbExecutor


def run_shell(executor: AdbExecutor, serial: str, command: str) -> str:
    return executor.shell(serial, command)
