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
class RPN(VisitorExpr[str]):
    def rpn(self, expr: Expr) -> str:
        return expr.accept(self)

    @override
    def visit_binary_expr(self, expr: Binary) -> str:
        return (
            f"{expr.left.accept(self)} {expr.right.accept(self)} {expr.operator.lexeme}"
        )

    @override
    def visit_grouping_expr(self, expr: Grouping) -> str:
        return expr.expression.accept(self)

    @override
    def visit_literal_expr(self, expr: Literal) -> str:
        return render(expr.value)

    @override
    def visit_unary_expr(self, expr: Unary) -> str:
        return f"{expr.right.accept(self)} {expr.operator.lexeme}"

    @override
    def visit_variable_expr(self, expr: Variable) -> str:
        return expr.name.lexeme

    @override
    def visit_assign_expr(self, expr: Assign) -> str:
        return f"{expr.name.lexeme} {expr.value.accept(self)} ="

    @override
    def visit_logical_expr(self, expr: Logical) -> str:
        return (
            f"{expr.left.accept(self)} {expr.right.accept(self)} {expr.operator.lexeme}"
        )

    @override
    def visit_call_expr(self, expr: Call) -> str:
        arguments = " ".join(arg.accept(self) for arg in expr.arguments)
        return f"{expr.callee.accept(self)} {arguments} call"
