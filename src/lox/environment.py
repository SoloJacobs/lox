from typing import Self

from lox.runtime_error import LoxRuntimeErr
from lox.scanner import Token


class Environment:
    def __init__(self, enclosing: Self | None = None) -> None:
        self._enclosing = enclosing
        self._environment: dict[str, object] = {}

    def define(self, name: str, value: object) -> None:
        self._environment[name] = value

    def get(self, name: Token) -> object:
        if name.lexeme in self._environment:
            return self._environment[name.lexeme]
        if self._enclosing is None:
            raise LoxRuntimeErr(name, f"Undefined variable '{name.lexeme}'.")
        return self._enclosing.get(name)

    def assign(self, name: Token, value: object) -> None:
        if name.lexeme in self._environment:
            self._environment[name.lexeme] = value
            return
        if self._enclosing is None:
            raise LoxRuntimeErr(name, f"Undefined variable '{name.lexeme}'.")
        self._enclosing.assign(name, value)
