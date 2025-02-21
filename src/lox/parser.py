from collections.abc import Sequence
from typing import Protocol

from lox.ast import (
    Assign,
    Binary,
    Block,
    Expr,
    Expression,
    Grouping,
    If,
    Literal,
    Logical,
    Print,
    Stmt,
    Unary,
    Var,
    Variable,
    While,
)
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
        return self.assignment()

    def assignment(self) -> Expr:
        expr = self.or_()
        if self.peek() == TokenType.EQUAL:
            equal = self.consume()
            if isinstance(expr, Variable):
                return Assign(expr.name, self.expression())
            self._reporter.parser_error(equal, "Invalid assignment target.")
        return expr

    def or_(self) -> Expr:
        expr = self.and_()
        while self.peek() == TokenType.OR:
            or_ = self.consume()
            expr = Logical(expr, or_, self.and_())
        return expr

    def and_(self) -> Expr:
        expr = self.equality()
        while self.peek() == TokenType.AND:
            and_ = self.consume()
            expr = Logical(expr, and_, self.equality())
        return expr

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
            case TokenType.IDENTIFIER:
                return Variable(self.consume())
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

    def parse(self) -> Sequence[Expr | Stmt] | None:
        declarations = []
        while self.peek() != TokenType.EOF:
            declaration = self.declaration()
            if declaration is not None:
                declarations.append(declaration)
            else:
                self.find_errors()
                return None
        return declarations

    def find_errors(self) -> None:
        while self.peek() != TokenType.EOF:
            self.declaration()

    def declaration(self) -> Stmt | None:
        try:
            if self.peek() == TokenType.VAR:
                return self.var_stmt()
            return self.stmt()
        except ParserError:
            self._synchronize()
            return None

    def stmt(self) -> Stmt:
        if self.peek() == TokenType.PRINT:
            return self.print_stmt()
        if self.peek() == TokenType.LEFT_BRACE:
            return self.block_stmt()
        if self.peek() == TokenType.IF:
            return self.if_stmt()
        if self.peek() == TokenType.WHILE:
            return self.while_stmt()
        return self.expr_stmt()

    def while_stmt(self) -> While:
        while_ = self.consume()
        assert while_.type_ == TokenType.WHILE
        left = self.consume()
        if left.type_ != TokenType.LEFT_PAREN:
            raise self._error(left, "Expect '(' after 'while'.")
        expr = self.expression()
        right = self.consume()
        if right.type_ != TokenType.RIGHT_PAREN:
            raise self._error(right, "Expect ')' after condition.")
        return While(expr, self.stmt())

    def if_stmt(self) -> If:
        if_ = self.consume()
        assert if_.type_ == TokenType.IF
        left = self.consume()
        if left.type_ != TokenType.LEFT_PAREN:
            raise self._error(left, "Expect '(' after 'if'.")
        expr = self.expression()
        right = self.consume()
        if right.type_ != TokenType.RIGHT_PAREN:
            raise self._error(right, "Expect ')' after if condition.")
        then = self.stmt()
        if self.peek() == TokenType.ELSE:
            self.consume()
            return If(expr, then, self.stmt())
        return If(expr, then, None)

    def block_stmt(self) -> Block:
        bracket = self.consume()
        assert bracket.type_ == TokenType.LEFT_BRACE
        statements = []
        while self.peek() not in (TokenType.RIGHT_BRACE, TokenType.EOF):
            if (statement := self.declaration()) is not None:
                statements.append(statement)
        final = self.consume()
        if final.type_ == TokenType.RIGHT_BRACE:
            return Block(statements)
        raise self._error(final, message="Expect '}' after block.")

    def expr_stmt(self) -> Expression:
        expression = self.expression()
        semicolon = self.consume()
        if semicolon.type_ != TokenType.SEMICOLON:
            raise self._error(semicolon, message="Expect ';' after value.")

        return Expression(expression)

    def print_stmt(self) -> Stmt:
        print_ = self.consume()
        assert print_.type_ == TokenType.PRINT
        expression = self.expression()
        semicolon = self.consume()
        if semicolon.type_ != TokenType.SEMICOLON:
            raise self._error(semicolon, message="Expect ';' after value.")

        return Print(expression)

    def var_stmt(self) -> Var:
        var = self.consume()
        assert var.type_ == TokenType.VAR
        name = self.consume()
        initializer: Expr = Literal(None)
        if self.peek() == TokenType.EQUAL:
            self.consume()
            initializer = self.expression()
        semicolon = self.consume()
        if semicolon.type_ != TokenType.SEMICOLON:
            raise self._error(
                self.consume(), message="Expect ';' after variable declaration.."
            )
        return Var(name, initializer)

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
