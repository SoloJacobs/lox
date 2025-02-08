from abc import ABC, abstractmethod
from typing import TypeVar, override

from lox.scanner import Token

T = TypeVar("T")


class Expr(ABC):
    @abstractmethod
    def accept[T](self, visitor: "Visitor[T]") -> T: ...


class Binary(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr) -> None:
        self.left = left
        self.operator = operator
        self.right = right

    @override
    def accept[T](self, visitor: "Visitor[T]") -> T:
        return visitor.visit_binary_expr(self)


class Grouping(Expr):
    def __init__(self, expression: Expr) -> None:
        self.expression = expression

    @override
    def accept[T](self, visitor: "Visitor[T]") -> T:
        return visitor.visit_grouping_expr(self)


class Literal(Expr):
    def __init__(self, value: object) -> None:
        self.value = value

    @override
    def accept[T](self, visitor: "Visitor[T]") -> T:
        return visitor.visit_literal_expr(self)


class Unary(Expr):
    def __init__(self, operator: Token, right: Expr) -> None:
        self.operator = operator
        self.right = right

    @override
    def accept[T](self, visitor: "Visitor[T]") -> T:
        return visitor.visit_unary_expr(self)


class Visitor[T](ABC):
    @abstractmethod
    def visit_binary_expr(self, expr: Binary) -> T: ...
    @abstractmethod
    def visit_grouping_expr(self, expr: Grouping) -> T: ...
    @abstractmethod
    def visit_literal_expr(self, expr: Literal) -> T: ...
    @abstractmethod
    def visit_unary_expr(self, expr: Unary) -> T: ...
