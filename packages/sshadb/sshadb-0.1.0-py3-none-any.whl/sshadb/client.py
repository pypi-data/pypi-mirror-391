from __future__ import annotations

from typing import Optional

from .core.adb_executor import AdbExecutor
from .core.file_transfer import FileTransfer
from .core.ssh_client import SSHClientWrapper, SSHConfig


class SSHAdb:
    def __init__(
        self,
        host: str,
        user: str,
        password: Optional[str] = None,
        key_path: Optional[str] = None,
        port: int = 22,
        timeout: float = 10.0,
        adb_path: str = "adb",
    ) -> None:
        config = SSHConfig(host=host, user=user, port=port, password=password, key_path=key_path, timeout=timeout)
        ssh = SSHClientWrapper(config)
        self._ssh = ssh
        self._executor = AdbExecutor(ssh, adb_path=adb_path)
        self._transfer = FileTransfer(ssh, self._executor)

    def close(self) -> None:
        self._ssh.close()

    def __enter__(self) -> "SSHAdb":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def devices(self):
        from .commands.devices import list_devices

        return list_devices(self._executor)

    def shell(self, serial: str, command: str) -> str:
        from .commands.shell import run_shell

        return run_shell(self._executor, serial, command)

    def push(self, serial: str, local_path: str, device_dest_path: str) -> None:
        from .commands.push import push_file

        return push_file(self._transfer, serial, local_path, device_dest_path)

    def pull(self, serial: str, device_src_path: str, local_dest_path: str) -> None:
        from .commands.pull import pull_file

        return pull_file(self._transfer, serial, device_src_path, local_dest_path)

    def get_state(self, serial: str) -> str:
        from .commands.get_state import get_state as _get_state

        return _get_state(self._executor, serial)
