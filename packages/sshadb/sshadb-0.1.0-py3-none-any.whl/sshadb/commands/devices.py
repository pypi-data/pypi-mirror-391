from __future__ import annotations

from typing import List, Dict

from ..utils.parser import parse_adb_devices
from ..core.adb_executor import AdbExecutor


def list_devices(executor: AdbExecutor) -> List[Dict[str, str]]:
    output = executor.devices()
    return parse_adb_devices(output)
