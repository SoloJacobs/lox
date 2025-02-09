from lox.scanner import Token


class LoxRuntimeErr(Exception):
    def __init__(self, token: Token, message: str) -> None:
        self._token = token
        self._message = message

    @property
    def message(self) -> str:
        return self._message

    @property
    def token(self) -> Token:
        return self._token
