from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TypeVar, override

from lox.scanner import Token

T = TypeVar("T")


class Expr(ABC):
    @abstractmethod
    def accept[T](self, visitor: "Visitor[T]") -> T: ...


@dataclass(frozen=True)
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr

    @override
    def accept[T](self, visitor: "Visitor[T]") -> T:
        return visitor.visit_binary_expr(self)


@dataclass(frozen=True)
class Grouping(Expr):
    expression: Expr

    @override
    def accept[T](self, visitor: "Visitor[T]") -> T:
        return visitor.visit_grouping_expr(self)


@dataclass(frozen=True)
class Literal(Expr):
    value: object

    @override
    def accept[T](self, visitor: "Visitor[T]") -> T:
        return visitor.visit_literal_expr(self)


@dataclass(frozen=True)
class Unary(Expr):
    operator: Token
    right: Expr

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
