from __future__ import annotations

from ..core.file_transfer import FileTransfer


def pull_file(transfer: FileTransfer, serial: str, device_src_path: str, local_dest_path: str) -> None:
    transfer.pull(serial, device_src_path, local_dest_path)
