from __future__ import annotations

from typing import List, Dict

from ..exceptions import ParseError


def parse_adb_devices(output: str) -> List[Dict[str, str]]:
    try:
        lines = [l.rstrip() for l in output.splitlines()]
        devices: List[Dict[str, str]] = []
        seen_header = False
        for raw in lines:
            line = raw.strip()
            if not line:
                continue
            if line.startswith("List of devices attached"):
                seen_header = True
                continue
            if not seen_header:
                # 헤더 이전의 데몬 메시지 등은 무시
                continue
            if line.startswith("*"):
                # "* daemon not running; starting now at tcp:5037" 같은 라인 무시
                continue
            parts = line.split()
            if len(parts) < 2:
                continue
            serial, state = parts[0], parts[1]
            devices.append({"serial": serial, "state": state})
        return devices
    except Exception as e:
        raise ParseError(f"Failed to parse adb devices output: {e}") from e
