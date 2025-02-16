from collections.abc import Sequence
from typing import Protocol, final, override

from lox.ast import (
    Binary,
    Expr,
    Expression,
    Grouping,
    Literal,
    Print,
    Stmt,
    Unary,
    Var,
    Variable,
    VisitorExpr,
    VisitorStmt,
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
        self._environment = Environment()

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
