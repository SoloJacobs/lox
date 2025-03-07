from lox.scanner import Scanner, Token, TokenType
from tests.lox.utils import Reporter


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


def test_scan_tokens_string() -> None:
    # Assemble
    lox = '"// this is a comment (( )){} // grouping stuff !*+-/=<> <= == // operators"'
    reporter = Reporter()
    scanner = Scanner(reporter, lox)
    # Act
    tokens = scanner.scan_tokens()
    # Assert
    assert tokens == [
        Token(
            type_=TokenType.STRING,
            lexeme='"// this is a comment (( )){} // grouping stuff !*+-/=<> <= == // operators"',
            literal="// this is a comment (( )){} // grouping stuff !*+-/=<> <= == // operators",
            line=1,
        ),
        Token(type_=TokenType.EOF, lexeme="", literal=None, line=1),
    ]
    assert reporter.errors == []


def test_scan_tokens_invalid_string() -> None:
    # Assemble
    lox = '"// this is '
    reporter = Reporter()
    scanner = Scanner(reporter, lox)
    # Act
    _ = scanner.scan_tokens()
    # Assert
    assert reporter.errors == [(1, "Unterminated string.")]


def test_scan_tokens_integer() -> None:
    # Assemble
    lox = " 123 "
    reporter = Reporter()
    scanner = Scanner(reporter, lox)
    # Act
    tokens = scanner.scan_tokens()
    # Assert
    assert tokens == [
        Token(type_=TokenType.NUMBER, lexeme="123", literal=123, line=1),
        Token(type_=TokenType.EOF, lexeme="", literal=None, line=1),
    ]
    assert reporter.errors == []


def test_scan_tokens_float() -> None:
    # Assemble
    lox = " 123.4 "
    reporter = Reporter()
    scanner = Scanner(reporter, lox)
    # Act
    tokens = scanner.scan_tokens()
    # Assert
    assert tokens == [
        Token(type_=TokenType.NUMBER, lexeme="123.4", literal=123.4, line=1),
        Token(type_=TokenType.EOF, lexeme="", literal=None, line=1),
    ]
    assert reporter.errors == []


def test_scan_tokens_identifiers() -> None:
    # Assemble
    lox = " and class or abc nil "
    reporter = Reporter()
    scanner = Scanner(reporter, lox)
    # Act
    tokens = scanner.scan_tokens()
    # Assert
    assert tokens == [
        Token(type_=TokenType.AND, lexeme="and", literal="and", line=1),
        Token(type_=TokenType.CLASS, lexeme="class", literal="class", line=1),
        Token(type_=TokenType.OR, lexeme="or", literal="or", line=1),
        Token(type_=TokenType.IDENTIFIER, lexeme="abc", literal="abc", line=1),
        Token(type_=TokenType.NIL, lexeme="nil", literal="nil", line=1),
        Token(type_=TokenType.EOF, lexeme="", literal=None, line=1),
    ]
    assert reporter.errors == []


def test_scan_c_style_comment() -> None:
    # Assemble
    lox = " 1 /* one */ * 2 / 2 // comment"
    reporter = Reporter()
    scanner = Scanner(reporter, lox)
    # Act
    tokens = scanner.scan_tokens()
    # Assert
    assert tokens == [
        Token(
            type_=TokenType.NUMBER,
            lexeme="1",
            literal=1.0,
            line=1,
        ),
        Token(
            type_=TokenType.STAR,
            lexeme="*",
            literal=None,
            line=1,
        ),
        Token(
            type_=TokenType.NUMBER,
            lexeme="2",
            literal=2.0,
            line=1,
        ),
        Token(
            type_=TokenType.SLASH,
            lexeme="/",
            literal=None,
            line=1,
        ),
        Token(
            type_=TokenType.NUMBER,
            lexeme="2",
            literal=2.0,
            line=1,
        ),
        Token(
            type_=TokenType.EOF,
            lexeme="",
            literal=None,
            line=1,
        ),
    ]
    assert reporter.errors == []


def test_scan_c_style_comment_new_line() -> None:
    # Assemble
    lox = """ 1 /*

*/ + 1"""
    reporter = Reporter()
    scanner = Scanner(reporter, lox)
    # Act
    tokens = scanner.scan_tokens()
    # Assert
    assert tokens == [
        Token(
            type_=TokenType.NUMBER,
            lexeme="1",
            literal=1.0,
            line=1,
        ),
        Token(
            type_=TokenType.PLUS,
            lexeme="+",
            literal=None,
            line=3,
        ),
        Token(
            type_=TokenType.NUMBER,
            lexeme="1",
            literal=1.0,
            line=3,
        ),
        Token(
            type_=TokenType.EOF,
            lexeme="",
            literal=None,
            line=3,
        ),
    ]
    assert reporter.errors == []


def test_scan_c_style_comment_reject_nested() -> None:
    # The lexical grammar would no longer be regular, if we supported balancing /* */.
    # Assemble
    lox = """/* /* */"""
    reporter = Reporter()
    scanner = Scanner(reporter, lox)
    # Act
    _tokens = scanner.scan_tokens()
    # Assert
    assert reporter.errors == [(1, "Nested comments disallowed.")]
