from collections.abc import Sequence

from lox.ast import Binary, Literal
from lox.parser import Parser
from lox.scanner import Scanner, Token, TokenType


class Reporter:
    def __init__(self) -> None:
        self._errors: list[tuple[int, str]] = []
        self._parser_errors: list[tuple[Token, str]] = []

    def error(self, line: int, message: str) -> None:
        self._errors.append((line, message))

    def parser_error(self, token: Token, message: str) -> None:
        self._parser_errors.append((token, message))

    @property
    def errors(self) -> Sequence[tuple[int, str]]:
        return self._errors

    @property
    def parser_errors(self) -> Sequence[tuple[Token, str]]:
        return self._parser_errors


def test_parse_associative() -> None:
    # Assemble
    lox = "1 + 2 + 3"
    reporter = Reporter()
    tokens = Scanner(reporter, lox).scan_tokens()
    assert not reporter.errors
    parser = Parser(reporter, tokens)
    # Act
    expr = parser.expression()
    # Assert
    assert not reporter.parser_errors
    assert expr == Binary(
        Binary(
            Literal(1),
            Token(TokenType.PLUS, "+", None, 1),
            Literal(2),
        ),
        Token(TokenType.PLUS, "+", None, 1),
        Literal(3),
    )


def test_parse_precedence_arithmetic() -> None:
    # Assemble
    lox = "1 + 2 * 3"
    reporter = Reporter()
    tokens = Scanner(reporter, lox).scan_tokens()
    assert not reporter.errors
    parser = Parser(reporter, tokens)
    # Act
    expr = parser.expression()
    # Assert
    assert not reporter.parser_errors
    assert expr == Binary(
        Literal(1),
        Token(TokenType.PLUS, "+", None, 1),
        Binary(
            Literal(2),
            Token(TokenType.STAR, "*", None, 1),
            Literal(3),
        ),
    )


def test_parse_equal_associativity() -> None:
    # Assemble
    lox = "false == true == true"
    reporter = Reporter()
    tokens = Scanner(reporter, lox).scan_tokens()
    assert not reporter.errors
    parser = Parser(reporter, tokens)
    # Act
    expr = parser.expression()
    # Assert
    assert not reporter.parser_errors
    assert expr == Binary(
        Binary(
            Literal(False),
            Token(TokenType.EQUAL_EQUAL, "==", None, 1),
            Literal(True),
        ),
        Token(TokenType.EQUAL_EQUAL, "==", None, 1),
        Literal(True),
    )
