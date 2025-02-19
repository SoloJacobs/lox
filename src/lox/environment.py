from lox.runtime_error import LoxRuntimeErr
from lox.scanner import Token


class Environment:
    def __init__(self) -> None:
        self._environment: dict[str, object] = {}

    def define(self, name: str, value: object) -> None:
        self._environment[name] = value

    def get(self, name: Token) -> object:
        if name.lexeme not in self._environment:
            raise LoxRuntimeErr(name, f"Undefined variable '{name.lexeme}'.")
        return self._environment[name.lexeme]

    def assign(self, name: Token, value: object) -> None:
        if name.lexeme not in self._environment:
            raise LoxRuntimeErr(name, f"Undefined variable '{name.lexeme}'.")
        self._environment[name.lexeme] = value
