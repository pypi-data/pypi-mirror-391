class SSHAdbError(Exception):
    pass


class SSHConnectionError(SSHAdbError):
    pass


class SSHAuthenticationError(SSHAdbError):
    pass


class CommandExecutionError(SSHAdbError):
    def __init__(self, message: str, exit_code: int | None = None, stderr: str | None = None):
        super().__init__(message)
        self.exit_code = exit_code
        self.stderr = stderr


class FileTransferError(SSHAdbError):
    pass


class ConfigurationError(SSHAdbError):
    pass


class ParseError(SSHAdbError):
    pass
