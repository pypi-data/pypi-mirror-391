from __future__ import annotations

import os
import socket
from dataclasses import dataclass
from typing import Optional, Tuple

import paramiko

from ..exceptions import (
    SSHConnectionError,
    SSHAuthenticationError,
)


@dataclass
class SSHConfig:
    host: str
    user: str
    port: int = 22
    password: Optional[str] = None
    key_path: Optional[str] = None
    timeout: float = 10.0


class SSHClientWrapper:
    def __init__(self, config: SSHConfig):
        self._config = config
        self._client: Optional[paramiko.SSHClient] = None

    def connect(self) -> None:
        if self._client is not None:
            return
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            connect_kwargs = {
                "hostname": self._config.host,
                "username": self._config.user,
                "port": self._config.port,
                "timeout": self._config.timeout,
                "allow_agent": True,
                "look_for_keys": True,
                "compress": True,
            }
            if self._config.key_path:
                key_path = os.path.expanduser(self._config.key_path)
                connect_kwargs["key_filename"] = key_path
            if self._config.password:
                connect_kwargs["password"] = self._config.password
            client.connect(**connect_kwargs)
            self._client = client
        except paramiko.AuthenticationException as e:
            raise SSHAuthenticationError("SSH authentication failed") from e
        except (paramiko.SSHException, socket.timeout, OSError) as e:
            raise SSHConnectionError(f"SSH connection failed: {e}") from e

    def close(self) -> None:
        if self._client is not None:
            try:
                self._client.close()
            finally:
                self._client = None

    def _ensure(self) -> paramiko.SSHClient:
        if self._client is None:
            self.connect()
        assert self._client is not None
        return self._client

    def exec(
        self, command: str, get_pty: bool = False, timeout: Optional[float] = None
    ) -> Tuple[int, str, str]:
        try:
            client = self._ensure()
            stdin, stdout, stderr = client.exec_command(
                command, get_pty=get_pty, timeout=timeout
            )
            exit_code = stdout.channel.recv_exit_status()
            out = stdout.read().decode("utf-8", errors="replace")
            err = stderr.read().decode("utf-8", errors="replace")
            return exit_code, out, err
        except paramiko.AuthenticationException as e:
            raise SSHAuthenticationError("SSH authentication failed during exec") from e
        except (paramiko.SSHException, socket.timeout, OSError) as e:
            raise SSHConnectionError(f"SSH exec failed: {e}") from e

    def sftp_upload(self, local_path: str, remote_path: str) -> None:
        try:
            sftp = self._ensure().open_sftp()
            try:
                sftp.put(local_path, remote_path)
            finally:
                sftp.close()
        except (paramiko.SSHException, OSError) as e:
            raise SSHConnectionError(f"SFTP upload failed: {e}") from e

    def sftp_download(self, remote_path: str, local_path: str) -> None:
        try:
            sftp = self._ensure().open_sftp()
            try:
                sftp.get(remote_path, local_path)
            finally:
                sftp.close()
        except (paramiko.SSHException, OSError) as e:
            raise SSHConnectionError(f"SFTP download failed: {e}") from e

    def sftp_remove(self, remote_path: str) -> None:
        try:
            sftp = self._ensure().open_sftp()
            try:
                sftp.remove(remote_path)
            finally:
                sftp.close()
        except FileNotFoundError:
            return
        except (paramiko.SSHException, OSError) as e:
            raise SSHConnectionError(f"SFTP remove failed: {e}") from e
