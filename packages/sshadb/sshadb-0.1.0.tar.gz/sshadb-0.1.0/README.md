# sshadb

Run Android ADB over SSH on a remote host with a simple Python API.

## Overview

sshadb는 로컬 PC에서 SSH로 원격 서버에 접속해, 원격 서버에서 ADB 명령을 실행하고 그 결과를 로컬 Python API로 다룰 수 있게 해주는 경량 유틸리티 라이브러리입니다.

주요 기능:
- 원격 `adb devices` 목록 조회
- 특정 단말 대상 `adb shell` 실행
- 파일 전송: 로컬 → 원격 → 단말(`adb push`), 단말 → 원격 → 로컬(`adb pull`)
- 단말 상태 조회(`adb get-state`)

## Requirements

- Python 3.11+
- 원격 서버에 SSH 접근 가능해야 합니다(포트 기본 22).
- 원격 서버에 ADB가 설치되어 있어야 하며, 대상 단말이 해당 서버에 연결되어 있어야 합니다.

## Installation

PyPI 배포 이후:

```
pip install sshadb
```

개발/로컬 설치:

```
python -m pip install -e .
```

테스트/개발 도구 포함 설치:

```
python -m pip install -e .[dev]
```

## Quick Start

```python
from sshadb import SSHAdb

client = SSHAdb(host="192.168.0.10", user="ubuntu", key_path="~/.ssh/id_rsa")
print(client.devices())
print(client.get_state("SERIAL"))
print(client.shell("SERIAL", "echo hello"))
client.push("SERIAL", "./local.txt", "/data/local/tmp/remote.txt")
client.pull("SERIAL", "/data/local/tmp/remote.txt", "./downloaded.txt")
client.close()
```

## Usage

두 가지 방식으로 사용할 수 있습니다.

1) 인스턴스 방식

```python
from sshadb import SSHAdb

client = SSHAdb(
    host="192.168.0.10",
    user="ubuntu",
    key_path="~/.ssh/id_rsa",  # 또는 password="..."
    port=22,                    # 기본값 22
    timeout=10.0,               # 초 단위
    adb_path="adb",            # 원격의 adb 경로/이름
)
devices = client.devices()
state = client.get_state("SERIAL")
output = client.shell("SERIAL", "echo hello")
client.push("SERIAL", "./local.txt", "/data/local/tmp/remote.txt")
client.pull("SERIAL", "/data/local/tmp/remote.txt", "./downloaded.txt")
client.close()
```

2) 전역 구성 + 편의 함수

```python
import sshadb

sshadb.configure(host="192.168.0.10", user="ubuntu", key_path="~/.ssh/id_rsa")
print(sshadb.devices())
print(sshadb.get_state("SERIAL"))
print(sshadb.shell("SERIAL", "echo hello"))
```

### API 개요

- 클래스: `sshadb.SSHAdb`
  - `devices() -> list[dict]`
  - `get_state(serial: str) -> str`
  - `shell(serial: str, command: str) -> str`
  - `push(serial: str, local_path: str, device_dest_path: str) -> None`
  - `pull(serial: str, device_src_path: str, local_dest_path: str) -> None`

- 전역 함수(전역 구성 사용 시):
  - `sshadb.configure(**kwargs)`
  - `sshadb.devices()` / `sshadb.get_state(serial)` / `sshadb.shell(serial, cmd)` / `sshadb.push(...)` / `sshadb.pull(...)`

## Configuration

인증:
- 비밀번호 기반: `password="..."`
- 키 기반: `key_path="~/.ssh/id_rsa"`

연결/실행 옵션:
- `port`: SSH 포트(기본 22)
- `timeout`: SSH 연결 타임아웃(초)
- `adb_path`: 원격 ADB 바이너리 경로 또는 이름(기본 `adb`)

## Testing

환경 변수로 테스트 설정을 주입합니다. `.env` 파일을 사용하려면 프로젝트 루트에 배치하면 자동 로드됩니다.

- 필수: `SSHADB_HOST`, `SSHADB_USER`, (`SSHADB_PASSWORD` 또는 `SSHADB_KEY_PATH`), `SSHADB_SERIAL`
- 선택: `SSHADB_PORT`(기본 22), `SSHADB_TIMEOUT`(기본 10)

실행:

```
pytest -vv
```

부분 실행/디버깅:

```
pytest -vv tests/test_shell.py::test_shell_echo
pytest -vv -k devices -s -o log_cli_level=INFO
```

## Versioning & Release

이 프로젝트는 Semantic Versioning(SemVer)을 따릅니다. 세부 전략과 배포 가이드는 다음 문서를 참고하세요.

- 버전 전략: [docs/versioning.md](docs/versioning.md)
- 변경 이력: [docs/changelog.md](docs/changelog.md)

릴리스 시 권장 순서:

1. `pyproject.toml`의 `version` 업데이트
2. `src/sshadb/__init__.py`의 `__version__` 동기화
3. 변경 이력 갱신(`docs/changelog.md`)
4. Git 태그 생성: `git tag -a vX.Y.Z -m "Release vX.Y.Z" && git push --tags`
5. 배포: `python -m build && twine upload dist/*`

PyPI 버전과 Git 태그는 반드시 일치해야 합니다.

## License

MIT License. 자세한 내용은 [LICENSE](LICENSE) 파일을 참고하세요.

## Links

- Homepage: https://github.com/dhkimxx/sshadb
