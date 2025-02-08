from typing import final, override

from lox.ast import Binary, Expr, Grouping, Literal, Unary, Visitor


@final
class RPN(Visitor[str]):
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
        if expr.value is None:
            return "nil"
        return str(expr.value)

    @override
    def visit_unary_expr(self, expr: Unary) -> str:
        return f"{expr.right.accept(self)} {expr.operator.lexeme}"
