import enum
from collections.abc import Sequence
from dataclasses import dataclass
from typing import override


class TokenType(enum.Enum):
    # Single-character tokens.
    LEFT_PAREN = enum.auto()
    RIGHT_PAREN = enum.auto()
    LEFT_BRACE = enum.auto()
    RIGHT_BRACE = enum.auto()
    COMMA = enum.auto()
    DOT = enum.auto()
    MINUS = enum.auto()
    PLUS = enum.auto()
    SEMICOLON = enum.auto()
    SLASH = enum.auto()
    STAR = enum.auto()
    # One or two character tokens.
    BANG = enum.auto()
    BANG_EQUAL = enum.auto()
    EQUAL = enum.auto()
    EQUAL_EQUAL = enum.auto()
    GREATER = enum.auto()
    GREATER_EQUAL = enum.auto()
    LESS = enum.auto()
    LESS_EQUAL = enum.auto()
    # Literals.
    IDENTIFIER = enum.auto()
    STRING = enum.auto()
    NUMBER = enum.auto()
    # Keywords.
    AND = enum.auto()
    CLASS = enum.auto()
    ELSE = enum.auto()
    FALSE = enum.auto()
    FUN = enum.auto()
    FOR = enum.auto()
    IF = enum.auto()
    NIL = enum.auto()
    OR = enum.auto()
    PRINT = enum.auto()
    RETURN = enum.auto()
    SUPER = enum.auto()
    THIS = enum.auto()
    TRUE = enum.auto()
    VAR = enum.auto()
    WHILE = enum.auto()
    EOF = enum.auto()


@dataclass(frozen=True)
class Token:
    type_: TokenType
    lexeme: str
    literal: object
    line: int

    @override
    def __str__(self) -> str:
        return f"{self.type_.name} {self.lexeme} {self.literal}"


class Scanner:
    def __init__(self, source: str) -> None:
        self._source = source
        self._start = 0
        self._current = 0
        self._line = 1
        self._tokens: list[Token] = []

    def scan_tokens(self, source: str) -> Sequence[Token]:
        while not self._is_at_end():
            self._start = self._current
            self._scan_token()
        self._tokens.append(
            Token(
                type_=TokenType.EOF,
                lexeme="",
                literal=None,
                line=self._line,
            )
        )
        return self._tokens

    def _scan_token(self) -> None:
        raise NotImplementedError()

    def _is_at_end(self) -> bool:
        return self._current >= len(self._source)
