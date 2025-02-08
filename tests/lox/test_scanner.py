from collections.abc import Sequence

from lox.scanner import Scanner, Token, TokenType


class Reporter:
    def __init__(self) -> None:
        self._errors: list[tuple[int, str]] = []

    def error(self, line: int, message: str) -> None:
        self._errors.append((line, message))

    @property
    def errors(self) -> Sequence[tuple[int, str]]:
        return self._errors


def test_scan_tokens() -> None:
    # Assemble
    lox = r"""// this is a comment
(( )){} // grouping stuff
!*+-/=<> <= == // operators"""
    reporter = Reporter()
    scanner = Scanner(reporter, lox)
    # Act
    tokens = scanner.scan_tokens()
    # Assert
    assert tokens == [
        Token(type_=TokenType.LEFT_PAREN, lexeme="(", literal=None, line=2),
        Token(type_=TokenType.LEFT_PAREN, lexeme="(", literal=None, line=2),
        Token(type_=TokenType.RIGHT_PAREN, lexeme=")", literal=None, line=2),
        Token(type_=TokenType.RIGHT_PAREN, lexeme=")", literal=None, line=2),
        Token(type_=TokenType.LEFT_BRACE, lexeme="{", literal=None, line=2),
        Token(type_=TokenType.RIGHT_BRACE, lexeme="}", literal=None, line=2),
        Token(type_=TokenType.BANG, lexeme="!", literal=None, line=3),
        Token(type_=TokenType.STAR, lexeme="*", literal=None, line=3),
        Token(type_=TokenType.PLUS, lexeme="+", literal=None, line=3),
        Token(type_=TokenType.MINUS, lexeme="-", literal=None, line=3),
        Token(type_=TokenType.SLASH, lexeme="/", literal=None, line=3),
        Token(type_=TokenType.EQUAL, lexeme="=", literal=None, line=3),
        Token(type_=TokenType.LESS, lexeme="<", literal=None, line=3),
        Token(type_=TokenType.GREATER, lexeme=">", literal=None, line=3),
        Token(type_=TokenType.LESS_EQUAL, lexeme="<=", literal=None, line=3),
        Token(type_=TokenType.EQUAL_EQUAL, lexeme="==", literal=None, line=3),
        Token(type_=TokenType.EOF, lexeme="", literal=None, line=3),
    ]
    assert reporter.errors == []


def test_scan_tokens_two_char() -> None:
    # Assemble
    lox = "!="
    reporter = Reporter()
    scanner = Scanner(reporter, lox)
    # Act
    tokens = scanner.scan_tokens()
    # Assert
    assert tokens == [
        Token(type_=TokenType.BANG_EQUAL, lexeme="!=", literal=None, line=1),
        Token(type_=TokenType.EOF, lexeme="", literal=None, line=1),
    ]
    assert reporter.errors == []
