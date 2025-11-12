from __future__ import annotations

from ..core.file_transfer import FileTransfer


def push_file(transfer: FileTransfer, serial: str, local_path: str, device_dest_path: str) -> None:
    transfer.push(serial, local_path, device_dest_path)
