from __future__ import annotations

import shlex
from typing import List, Optional

from ..exceptions import CommandExecutionError
from .ssh_client import SSHClientWrapper


class AdbExecutor:
    def __init__(self, ssh: SSHClientWrapper, adb_path: str = "adb"):
        self._ssh = ssh
        self._adb_path = adb_path

    def _compose(self, parts: List[str]) -> str:
        return " ".join(shlex.quote(p) for p in parts)

    def run(self, args: List[str]) -> str:
        cmd = self._compose([self._adb_path] + args)
        code, out, err = self._ssh.exec(cmd)
        if code != 0:
            raise CommandExecutionError(f"adb command failed: {cmd}", exit_code=code, stderr=err)
        return out.strip()

    def devices(self) -> str:
        return self.run(["devices"])

    def get_state(self, serial: str) -> str:
        return self.run(["-s", serial, "get-state"]) or ""

    def shell(self, serial: str, command: str) -> str:
        cmd = self._compose([self._adb_path, "-s", serial, "shell", command])
        code, out, err = self._ssh.exec(cmd)
        if code != 0:
            raise CommandExecutionError(f"adb shell failed: {command}", exit_code=code, stderr=err)
        return out.rstrip("\n")
