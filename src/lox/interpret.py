import time
from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Protocol, final, override

from lox.ast import (
    Assign,
    Binary,
    Block,
    Call,
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
    VisitorExpr,
    VisitorStmt,
    While,
)
from lox.environment import Environment
from lox.render import render
from lox.runtime_error import LoxRuntimeErr
from lox.scanner import TokenType


def _check_float(value: object, exception: Exception) -> float:
    if not isinstance(value, float):
        raise exception
    return value


def _is_truthy(value: object) -> bool:
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    return True


class ErrorReporter(Protocol):
    def runtime_error(self, err: LoxRuntimeErr) -> None: ...


@final
class Interpreter(VisitorExpr[object], VisitorStmt[None]):
    def __init__(self) -> None:
        self._globals = Environment()
        self._environment = self._globals
        self._globals.define("clock", Clock())

    def interpret(self, reporter: ErrorReporter, stmts: Sequence[Expr | Stmt]) -> None:
        try:
            for stmt in stmts:
                stmt.accept(self)
        except LoxRuntimeErr as err:
            reporter.runtime_error(err)

    @override
    def visit_binary_expr(self, expr: Binary) -> object:
        right = expr.right.accept(self)
        left = expr.left.accept(self)
        match expr.operator.type_:
            case TokenType.PLUS:
                if isinstance(right, float) and isinstance(left, float):
                    return left + right
                if isinstance(right, str) and isinstance(left, str):
                    return left + right
                raise LoxRuntimeErr(
                    expr.operator, "Operands must be be two numbers or two strings."
                )
            case TokenType.MINUS:
                right_float = _check_float(
                    right, LoxRuntimeErr(expr.operator, "Operands must be numbers.")
                )
                left_float = _check_float(
                    left, LoxRuntimeErr(expr.operator, "Operands must be numbers.")
                )
                return left_float - right_float
            case TokenType.STAR:
                right_float = _check_float(
                    right, LoxRuntimeErr(expr.operator, "Operands must be numbers.")
                )
                left_float = _check_float(
                    left, LoxRuntimeErr(expr.operator, "Operands must be numbers.")
                )
                return left_float * right_float
            case TokenType.SLASH:
                right_float = _check_float(
                    right, LoxRuntimeErr(expr.operator, "Operands must be numbers.")
                )
                left_float = _check_float(
                    left, LoxRuntimeErr(expr.operator, "Operands must be numbers.")
                )
                return left_float / right_float
            case TokenType.GREATER:
                right_float = _check_float(
                    right, LoxRuntimeErr(expr.operator, "Operands must be numbers.")
                )
                left_float = _check_float(
                    left, LoxRuntimeErr(expr.operator, "Operands must be numbers.")
                )
                return left_float > right_float
            case TokenType.GREATER_EQUAL:
                right_float = _check_float(
                    right, LoxRuntimeErr(expr.operator, "Operands must be numbers.")
                )
                left_float = _check_float(
                    left, LoxRuntimeErr(expr.operator, "Operands must be numbers.")
                )
                return left_float >= right_float
            case TokenType.LESS:
                right_float = _check_float(
                    right, LoxRuntimeErr(expr.operator, "Operands must be numbers.")
                )
                left_float = _check_float(
                    left, LoxRuntimeErr(expr.operator, "Operands must be numbers.")
                )
                return left_float < right_float
            case TokenType.LESS_EQUAL:
                right_float = _check_float(
                    right, LoxRuntimeErr(expr.operator, "Operands must be numbers.")
                )
                left_float = _check_float(
                    left, LoxRuntimeErr(expr.operator, "Operands must be numbers.")
                )
                return left_float <= right_float
            case TokenType.BANG_EQUAL:
                right_float = _check_float(
                    right, LoxRuntimeErr(expr.operator, "Operands must be numbers.")
                )
                left_float = _check_float(
                    left, LoxRuntimeErr(expr.operator, "Operands must be numbers.")
                )
                return left_float != right_float
            case TokenType.EQUAL_EQUAL:
                right_float = _check_float(
                    right, LoxRuntimeErr(expr.operator, "Operands must be numbers.")
                )
                left_float = _check_float(
                    left, LoxRuntimeErr(expr.operator, "Operands must be numbers.")
                )
                return left_float == right_float
        raise NotImplementedError()

    @override
    def visit_grouping_expr(self, expr: Grouping) -> object:
        return expr.expression.accept(self)

    @override
    def visit_literal_expr(self, expr: Literal) -> object:
        return expr.value

    @override
    def visit_unary_expr(self, expr: Unary) -> object:
        right = expr.right.accept(self)
        match expr.operator.type_:
            case TokenType.MINUS:
                right_float = _check_float(
                    right, LoxRuntimeErr(expr.operator, "Operands must be numbers.")
                )
                return -right_float
            case TokenType.BANG:
                return not _is_truthy(right)
        raise NotImplementedError()

    @override
    def visit_expression_stmt(self, expr: Expression) -> None:
        _ = expr.expression.accept(self)

    @override
    def visit_print_stmt(self, expr: Print) -> None:
        value = expr.expression.accept(self)
        print(render(value))

    @override
    def visit_var_stmt(self, expr: Var) -> None:
        initializer = expr.initializer.accept(self)
        self._environment.define(expr.name.lexeme, initializer)

    @override
    def visit_variable_expr(self, expr: Variable) -> object:
        return self._environment.get(expr.name)

    @override
    def visit_assign_expr(self, expr: Assign) -> object:
        value = expr.value.accept(self)
        self._environment.assign(expr.name, value)
        return value

    @override
    def visit_call_expr(self, expr: Call) -> object:
        # Order of argument evaluation matter! Moreover, we could check whether the callee is
        # callable before evaluating arguments.
        callee = expr.callee.accept(self)
        arguments = [arg.accept(self) for arg in expr.arguments]
        if not isinstance(callee, LoxCallable):
            raise LoxRuntimeErr(expr.paren, "Can only call functions and classes.")
        if callee.arity != len(arguments):
            raise LoxRuntimeErr(
                expr.paren,
                f"Expected {callee.arity} arguments but got {len(arguments)}.",
            )
        return callee.call(self, arguments)

    @override
    def visit_block_stmt(self, expr: Block) -> None:
        previous = self._environment
        try:
            self._environment = Environment(previous)
            for statement in expr.statements:
                statement.accept(self)
        finally:
            self._environment = previous

    @override
    def visit_if_stmt(self, expr: If) -> None:
        if expr.condition.accept(self):
            expr.then_branch.accept(self)
        elif expr.else_branch is not None:
            expr.else_branch.accept(self)

    @override
    def visit_while_stmt(self, expr: While) -> None:
        while _is_truthy(expr.condition.accept(self)):
            expr.body.accept(self)

    @override
    def visit_logical_expr(self, expr: Logical) -> object:
        left = expr.left.accept(self)
        match expr.operator.type_:
            case TokenType.AND:
                if not _is_truthy(left):
                    return left
                return expr.right.accept(self)
            case TokenType.OR:
                if _is_truthy(left):
                    return left
                return expr.right.accept(self)
        raise NotImplementedError()


class LoxCallable(ABC):
    @property
    @abstractmethod
    def arity(self) -> int: ...

    @abstractmethod
    def call(self, interpreter: Interpreter, arguments: Sequence[object]) -> object: ...


class Clock(LoxCallable):
    @property
    @override
    def arity(self) -> int:
        return 0

    @override
    def call(self, interpreter: Interpreter, arguments: Sequence[object]) -> object:
        return time.time()

    @override
    def __str__(self) -> str:
        return "<native fun>"
