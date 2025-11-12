from __future__ import annotations

import os
import posixpath
import uuid
from pathlib import Path

from ..exceptions import CommandExecutionError, FileTransferError
from .adb_executor import AdbExecutor
from .ssh_client import SSHClientWrapper


class FileTransfer:
    def __init__(self, ssh: SSHClientWrapper, executor: AdbExecutor):
        self._ssh = ssh
        self._executor = executor
        self._base_tmp = "/tmp/sshadb"

    def _ensure_tmp_dir(self) -> None:
        self._ssh.exec(f"mkdir -p {self._base_tmp}")

    def _remote_tmp(self, basename: str) -> str:
        token = uuid.uuid4().hex
        return posixpath.join(self._base_tmp, f"{token}_{basename}")

    def push(self, serial: str, local_path: str, device_dest_path: str) -> None:
        if not Path(local_path).exists():
            raise FileTransferError(f"Local file not found: {local_path}")
        self._ensure_tmp_dir()
        basename = Path(local_path).name
        remote_tmp = self._remote_tmp(basename)
        try:
            self._ssh.sftp_upload(local_path, remote_tmp)
            out = self._executor.run(["-s", serial, "push", remote_tmp, device_dest_path])
            _ = out
        finally:
            try:
                self._ssh.sftp_remove(remote_tmp)
            except Exception:
                pass

    def pull(self, serial: str, device_src_path: str, local_dest_path: str) -> None:
        self._ensure_tmp_dir()
        basename = Path(device_src_path).name
        remote_tmp = self._remote_tmp(basename)
        try:
            out = self._executor.run(["-s", serial, "pull", device_src_path, remote_tmp])
            _ = out
            local_parent = Path(local_dest_path).parent
            os.makedirs(local_parent, exist_ok=True)
            self._ssh.sftp_download(remote_tmp, local_dest_path)
        finally:
            try:
                self._ssh.sftp_remove(remote_tmp)
            except Exception:
                pass
