from collections.abc import Sequence

from lox.runtime_error import LoxRuntimeErr
from lox.scanner import Token


class Reporter:
    def __init__(self) -> None:
        self._errors: list[tuple[int, str]] = []
        self._parser_errors: list[tuple[Token, str]] = []
        self._runtime_errors: list[LoxRuntimeErr] = []

    def error(self, line: int, message: str) -> None:
        self._errors.append((line, message))

    def parser_error(self, token: Token, message: str) -> None:
        self._parser_errors.append((token, message))

    def runtime_error(self, err: LoxRuntimeErr) -> None:
        self._runtime_errors.append(err)

    @property
    def errors(self) -> Sequence[tuple[int, str]]:
        return self._errors

    @property
    def parser_errors(self) -> Sequence[tuple[Token, str]]:
        return self._parser_errors

    @property
    def runtime_errors(self) -> Sequence[LoxRuntimeErr]:
        return self._runtime_errors
