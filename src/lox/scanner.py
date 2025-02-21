import enum
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol, override


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


class ErrorReporter(Protocol):
    def error(self, line: int, message: str) -> None: ...


def _is_digit(char: str | None) -> bool:
    if char is None:
        return False
    return "0" <= char <= "9"


def _is_alpha(char: str | None) -> bool:
    if char is None:
        return False
    return "a" <= char <= "z" or "A" <= char <= "Z" or char == "_"


def _is_alpha_numeric(char: str | None) -> bool:
    return _is_alpha(char) or _is_digit(char)


class Scanner:
    def __init__(self, reporter: ErrorReporter, source: str) -> None:
        self._source = source
        self._reporter = reporter
        self._start = 0
        self._current = 0
        self._line = 1
        self._tokens: list[Token] = []

    def scan_tokens(self) -> Sequence[Token]:
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
        match self._advance():
            case "(":
                self._add_token(TokenType.LEFT_PAREN)
            case ")":
                self._add_token(TokenType.RIGHT_PAREN)
            case "{":
                self._add_token(TokenType.LEFT_BRACE)
            case "}":
                self._add_token(TokenType.RIGHT_BRACE)
            case ",":
                self._add_token(TokenType.COMMA)
            case ".":
                self._add_token(TokenType.DOT)
            case "-":
                self._add_token(TokenType.MINUS)
            case "+":
                self._add_token(TokenType.PLUS)
            case ";":
                self._add_token(TokenType.SEMICOLON)
            case "*":
                self._add_token(TokenType.STAR)
            case "!":
                self._add_token(
                    TokenType.BANG_EQUAL if self._match("=") else TokenType.BANG
                )
            case "=":
                self._add_token(
                    TokenType.EQUAL_EQUAL if self._match("=") else TokenType.EQUAL
                )
            case "<":
                self._add_token(
                    TokenType.LESS_EQUAL if self._match("=") else TokenType.LESS
                )
            case ">":
                self._add_token(
                    TokenType.GREATER_EQUAL if self._match("=") else TokenType.GREATER
                )
            case "/":
                if self._match("/"):
                    while self._peek() != "\n" and not self._is_at_end():
                        self._advance()
                elif self._match("*"):
                    while not self._is_at_end():
                        if self._peek() == "*" and self._peek_next() == "/":
                            self._advance()
                            self._advance()
                            return
                        if self._peek() == "/" and self._peek_next() == "*":
                            self._reporter.error(
                                self._line, "Nested comments disallowed."
                            )
                        if self._peek() == "\n":
                            self._line += 1
                        self._advance()
                    self._reporter.error(self._line, "Unterminated comment.")
                else:
                    self._add_token(TokenType.SLASH)
            case "\n":
                self._line += 1
            case '"':
                self._string()
            case c if c.isspace():
                pass
            case c if _is_digit(c):
                self._number()
            case c if _is_alpha(c):
                self._identifier()
            case _:
                self._reporter.error(self._line, "Unexpected character.")

    def _is_at_end(self) -> bool:
        return self._current >= len(self._source)

    def _identifier(self) -> None:
        while _is_alpha_numeric(self._peek()):
            self._advance()
        keyword_map = {
            "and": TokenType.AND,
            "class": TokenType.CLASS,
            "else": TokenType.ELSE,
            "false": TokenType.FALSE,
            "for": TokenType.FOR,
            "fun": TokenType.FUN,
            "if": TokenType.IF,
            "nil": TokenType.NIL,
            "or": TokenType.OR,
            "print": TokenType.PRINT,
            "return": TokenType.RETURN,
            "super": TokenType.SUPER,
            "this": TokenType.THIS,
            "true": TokenType.TRUE,
            "var": TokenType.VAR,
            "while": TokenType.WHILE,
        }
        lexeme = self._source[self._start : self._current]
        self._add_token(
            keyword_map.get(lexeme, TokenType.IDENTIFIER),
            lexeme,
        )

    def _number(self) -> None:
        while _is_digit(self._peek()):
            self._advance()
        if self._peek() == "." and _is_digit(self._peek_next()):
            self._advance()
            while _is_digit(self._peek()):
                self._advance()
        self._add_token(
            type_=TokenType.NUMBER,
            literal=float(self._source[self._start : self._current]),
        )

    def _peek_next(self) -> str | None:
        if self._current + 1 >= len(self._source):
            return None
        return self._source[self._current + 1]

    def _peek(self) -> str | None:
        if self._is_at_end():
            return None
        return self._source[self._current]

    def _string(self) -> None:
        while self._peek() != '"' and not self._is_at_end():
            if self._peek() == "\n":
                self._line += 1
            self._current += 1
        if self._is_at_end():
            self._reporter.error(self._line, "Unterminated string.")
        self._current += 1
        self._add_token(
            TokenType.STRING,
            self._source[self._start + 1 : self._current - 1],
        )

    def _match(self, expected: str) -> bool:
        if self._is_at_end():
            return False
        if self._source[self._current] != expected:
            return False
        self._current += 1
        return True

    def _advance(self) -> str:
        char = self._source[self._current]
        self._current += 1
        return char

    def _add_token(self, type_: TokenType, literal: object = None) -> None:
        self._tokens.append(
            Token(
                type_=type_,
                lexeme=self._source[self._start : self._current],
                literal=literal,
                line=self._line,
            )
        )
