from lox.ast import Binary, Expr, Grouping, Literal, Unary
from lox.scanner import Token, TokenType


class ParserError(Exception):
    def __init__(self, token: Token, message: str) -> None:
        self.token = token
        self.message = message


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
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
                return Literal(False)
            case TokenType.TRUE:
                return Literal(True)
            case TokenType.NIL:
                return Literal(None)
            case TokenType.LEFT_PAREN:
                self.consume()
                expr = self.expression()
                if self.peek() == TokenType.RIGHT_PAREN:
                    self.consume()
                    return Grouping(expr)
                raise ParserError(
                    self.consume(), message="Expect ')' after expression."
                )
        raise ParserError(self.consume(), message="Expected?")

    def peek(self) -> TokenType:
        return self._tokens[self._current].type_

    def consume(self) -> Token:
        self._current += 1
        return self._tokens[self._current - 1]
