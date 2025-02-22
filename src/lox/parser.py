from collections.abc import Sequence
from typing import Protocol

from lox.ast import (
    Assign,
    Binary,
    Block,
    Call,
    Expr,
    Expression,
    Function,
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
        return self.comma()

    def comma(self) -> Expr:
        expr = self.assignment()
        while self.peek() == TokenType.COMMA:
            comma = self.consume()
            right = self.assignment()
            expr = Binary(expr, comma, right)
        return expr

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
        return self.call()

    def call(self) -> Expr:
        expr = self.primary()
        while self.peek() == TokenType.LEFT_PAREN:
            expr = self.finish_call(expr)
        return expr

    def finish_call(self, callee: Expr) -> Call:
        left = self.consume()
        assert left.type_ == TokenType.LEFT_PAREN
        if self.peek() == TokenType.RIGHT_PAREN:
            return Call(callee, self.consume(), [])
        arguments = [self.expression()]
        while self.peek() == TokenType.COMMA:
            self.consume()
            arguments.append(self.expression())
        right = self.consume()
        if len(arguments) >= 255:
            self._error(right, "Can't have more than 255 arguments.")
        if right.type_ != TokenType.RIGHT_PAREN:
            raise self._error(right, "Expect ')' after arguments.")
        return Call(callee, right, arguments)

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
        if self.peek() == TokenType.FUN:
            return self.fun_stmt("function")
        if self.peek() == TokenType.WHILE:
            return self.while_stmt()
        if self.peek() == TokenType.FOR:
            return self.for_stmt()
        return self.expr_stmt()

    def fun_stmt(self, kind: str) -> Function:
        fun = self.consume()
        assert fun.type_ == TokenType.FUN
        name = self.consume()
        if name.type_ != TokenType.IDENTIFIER:
            raise self._error(name, f"Expect {kind} name.")
        left = self.consume()
        if left.type_ != TokenType.LEFT_PAREN:
            raise self._error(name, f"Expect '(' after {kind} name.")
        params = []
        if self.peek() != TokenType.RIGHT_PAREN:
            identifier = self.consume()
            if identifier.type_ != TokenType.IDENTIFIER:
                raise self._error(name, "Expect parameter name or ')'.")
            params.append(identifier)
            while self.peek() == TokenType.COMMA:
                self.consume()
                identifier = self.consume()
                if identifier.type_ != TokenType.IDENTIFIER:
                    raise self._error(name, "Expect parameter name or ')'.")
                params.append(identifier)
        right = self.consume()
        if right.type_ != TokenType.RIGHT_PAREN:
            raise self._error(name, "Expect ')' after parameters.")
        body = self.block_stmt()
        return Function(name, params, body.statements)

    def for_stmt(self) -> While | Block:
        for_ = self.consume()
        assert for_.type_ == TokenType.FOR
        left = self.consume()
        if left.type_ != TokenType.LEFT_PAREN:
            raise self._error(left, "Expect '(' after 'for'.")
        if self.peek() == TokenType.SEMICOLON:
            self.consume()
            initializer: None | Var | Expression = None
        elif self.peek() == TokenType.VAR:
            initializer = self.var_stmt()
        else:
            initializer = self.expr_stmt()

        condition = (
            Literal(True) if self.peek() == TokenType.RIGHT_PAREN else self.expression()
        )
        semicolon = self.consume()
        if semicolon.type_ != TokenType.SEMICOLON:
            raise self._error(semicolon, "Expected ';' after loop condition.")

        increment = None if self.peek() == TokenType.RIGHT_PAREN else self.expression()
        right = self.consume()
        if right.type_ != TokenType.RIGHT_PAREN:
            raise self._error(right, "Expect ')' after for clauses.")

        body = self.stmt()
        if increment is not None:
            body = Block(statements=[body, Expression(increment)])
        while_ = While(condition, body)
        if initializer is not None:
            return Block(statements=[initializer, while_])
        return while_

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
