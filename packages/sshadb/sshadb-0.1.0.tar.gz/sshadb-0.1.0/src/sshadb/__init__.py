from __future__ import annotations

from typing import Optional

from .client import SSHAdb
from .exceptions import ConfigurationError

__version__ = "0.1.0"

__all__ = [
    "SSHAdb",
    "configure",
    "get_default_client",
    "devices",
    "shell",
    "push",
    "pull",
    "get_state",
    "__version__",
]

_default_client: Optional[SSHAdb] = None


def configure(**kwargs) -> None:
    global _default_client
    _default_client = SSHAdb(**kwargs)


def get_default_client() -> SSHAdb:
    if _default_client is None:
        raise ConfigurationError("Default client is not configured. Instantiate SSHAdb or call sshadb.configure(...)")
    return _default_client


def devices():
    client = get_default_client()
    return client.devices()


def shell(serial: str, command: str) -> str:
    client = get_default_client()
    return client.shell(serial, command)


def push(serial: str, local_path: str, device_dest_path: str) -> None:
    client = get_default_client()
    return client.push(serial, local_path, device_dest_path)


def pull(serial: str, device_src_path: str, local_dest_path: str) -> None:
    client = get_default_client()
    return client.pull(serial, device_src_path, local_dest_path)


def get_state(serial: str) -> str:
    client = get_default_client()
    return client.get_state(serial)
