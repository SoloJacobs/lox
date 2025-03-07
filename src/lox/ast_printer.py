from typing import final, override

from lox.ast import (
    Assign,
    Binary,
    Call,
    Expr,
    Grouping,
    Literal,
    Logical,
    Unary,
    Variable,
    VisitorExpr,
)
from lox.render import render


@final
class AstPrinter(VisitorExpr[str]):
    def print(self, expr: Expr) -> str:
        return expr.accept(self)

    @override
    def visit_binary_expr(self, expr: Binary) -> str:
        return self._parenthesize(expr.operator.lexeme, expr.left, expr.right)

    @override
    def visit_grouping_expr(self, expr: Grouping) -> str:
        return self._parenthesize("group", expr.expression)

    @override
    def visit_literal_expr(self, expr: Literal) -> str:
        return render(expr.value)

    @override
    def visit_unary_expr(self, expr: Unary) -> str:
        return self._parenthesize(expr.operator.lexeme, expr.right)

    def _parenthesize(self, name: str, *exprs: Expr) -> str:
        exprs_str = " ".join(expr.accept(self) for expr in exprs)
        return f"({name} {exprs_str})"

    @override
    def visit_variable_expr(self, expr: Variable) -> str:
        return Variable.name.lexeme

    @override
    def visit_assign_expr(self, expr: Assign) -> str:
        return self._parenthesize("=", Variable(expr.name), expr.value)

    @override
    def visit_logical_expr(self, expr: Logical) -> str:
        return self._parenthesize(expr.operator.lexeme, expr.left, expr.right)

    @override
    def visit_call_expr(self, expr: Call) -> str:
        return self._parenthesize(
            "call",
            expr.callee,
            *expr.arguments,
        )
