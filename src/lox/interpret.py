from typing import Protocol, final, override

from lox.ast import (
    Binary,
    Expr,
    Grouping,
    Literal,
    Unary,
    Visitor,
)
from lox.render import render
from lox.runtime_error import LoxRuntimeErr
from lox.scanner import TokenType


def _check_float(value: object, exception: Exception) -> float:
    if not isinstance(value, float):
        raise exception
    return value


class ErrorReporter(Protocol):
    def runtime_error(self, err: LoxRuntimeErr) -> None: ...


@final
class Interpreter(Visitor[object]):
    def interpret(self, reporter: ErrorReporter, expr: Expr) -> None:
        try:
            value = expr.accept(self)
            print(render(value))
        except LoxRuntimeErr as err:
            reporter.runtime_error(err)

    @override
    def visit_binary_expr(self, expr: Binary) -> object:
        right = expr.right.accept(self)
        left = expr.left.accept(self)
        match expr.operator.type_:
            case TokenType.PLUS:
                if isinstance(right, float) and isinstance(left, float):
                    return right + left
                if isinstance(right, str) and isinstance(left, str):
                    return right + left
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
                return right_float - left_float
            case TokenType.STAR:
                right_float = _check_float(
                    right, LoxRuntimeErr(expr.operator, "Operands must be numbers.")
                )
                left_float = _check_float(
                    left, LoxRuntimeErr(expr.operator, "Operands must be numbers.")
                )
                return right_float * left_float
            case TokenType.SLASH:
                right_float = _check_float(
                    right, LoxRuntimeErr(expr.operator, "Operands must be numbers.")
                )
                left_float = _check_float(
                    left, LoxRuntimeErr(expr.operator, "Operands must be numbers.")
                )
                return right_float / left_float
            case TokenType.GREATER:
                right_float = _check_float(
                    right, LoxRuntimeErr(expr.operator, "Operands must be numbers.")
                )
                left_float = _check_float(
                    left, LoxRuntimeErr(expr.operator, "Operands must be numbers.")
                )
                return right_float > left_float
            case TokenType.GREATER_EQUAL:
                right_float = _check_float(
                    right, LoxRuntimeErr(expr.operator, "Operands must be numbers.")
                )
                left_float = _check_float(
                    left, LoxRuntimeErr(expr.operator, "Operands must be numbers.")
                )
                return right_float >= left_float
            case TokenType.LESS:
                right_float = _check_float(
                    right, LoxRuntimeErr(expr.operator, "Operands must be numbers.")
                )
                left_float = _check_float(
                    left, LoxRuntimeErr(expr.operator, "Operands must be numbers.")
                )
                return right_float < left_float
            case TokenType.LESS_EQUAL:
                right_float = _check_float(
                    right, LoxRuntimeErr(expr.operator, "Operands must be numbers.")
                )
                left_float = _check_float(
                    left, LoxRuntimeErr(expr.operator, "Operands must be numbers.")
                )
                return right_float <= left_float
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
                if right is None:
                    return True
                if isinstance(right, bool):
                    return not right
                return False
        raise NotImplementedError()
