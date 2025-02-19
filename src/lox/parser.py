from collections.abc import Sequence
from typing import Protocol

from lox.ast import Binary, Expr, Grouping, Literal, Unary
from lox.scanner import Token, TokenType


class ParserError(Exception):
    def __init__(self) -> None:
        pass


class ErrorReporter(Protocol):
    def parser_error(self, token: Token, message: str) -> None: ...


class Parser:
    def __init__(self, reporter: ErrorReporter, tokens: Sequence[Token]) -> None:
        self._reporter = reporter
        self._tokens = tokens
        self._current = 0

    def expression(self) -> Expr:
        return self.equality()

    def equality(self) -> Expr:
        expr = self.comparison()
        while self.peek() in (TokenType.EQUAL_EQUAL, TokenType.BANG_EQUAL):
            operator = self.consume()
            right = self.comparison()
            expr = Binary(expr, operator, right)
        return expr

    def comparison(self) -> Expr:
        expr = self.term()
        while self.peek() in (
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
        ):
            operator = self.consume()
            right = self.term()
            expr = Binary(expr, operator, right)
        return expr

    def term(self) -> Expr:
        expr = self.factor()
        while self.peek() in (TokenType.MINUS, TokenType.PLUS):
            operator = self.consume()
            right = self.factor()
            expr = Binary(expr, operator, right)
        return expr

    def factor(self) -> Expr:
        expr = self.unary()
        while self.peek() in (TokenType.SLASH, TokenType.STAR):
            operator = self.consume()
            right = self.unary()
            expr = Binary(expr, operator, right)
        return expr

    def unary(self) -> Expr:
        if self.peek() in (TokenType.MINUS, TokenType.BANG):
            operator = self.consume()
            return Unary(operator, self.unary())
        return self.primary()

    def primary(self) -> Expr:
        match self.peek():
            case TokenType.NUMBER | TokenType.STRING:
                return Literal(self.consume().literal)
            case TokenType.FALSE:
                self.consume()
                return Literal(False)
            case TokenType.TRUE:
                self.consume()
                return Literal(True)
            case TokenType.NIL:
                self.consume()
                return Literal(None)
            case TokenType.LEFT_PAREN:
                self.consume()
                expr = self.expression()
                if self.peek() == TokenType.RIGHT_PAREN:
                    self.consume()
                    return Grouping(expr)
                raise self._error(
                    self.consume(), message="Expect ')' after expression."
                )
        raise self._error(self.consume(), "Expected expression.")

    def peek(self) -> TokenType:
        return self._tokens[self._current].type_

    def consume(self) -> Token:
        self._current += 1
        return self._tokens[self._current - 1]

    def _error(self, token: Token, message: str) -> ParserError:
        self._reporter.parser_error(token, message)
        return ParserError()

    def parse(self) -> Expr | None:
        try:
            return self.expression()
        except ParserError:
            return None

    def _synchronize(self) -> None:
        while self.peek() != TokenType.EOF:
            if self.peek() == TokenType.SEMICOLON:
                self.consume()
                return
            if self.peek() in (
                TokenType.CLASS,
                TokenType.FOR,
                TokenType.FUN,
                TokenType.IF,
                TokenType.PRINT,
                TokenType.RETURN,
                TokenType.VAR,
                TokenType.WHILE,
            ):
                return
            self.consume()
