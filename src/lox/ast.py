from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import override

from lox.scanner import Token


class Expr(ABC):
    @abstractmethod
    def accept[T](self, visitor: "VisitorExpr[T]") -> T: ...


@dataclass(frozen=True)
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr

    @override
    def accept[T](self, visitor: "VisitorExpr[T]") -> T:
        return visitor.visit_binary_expr(self)


@dataclass(frozen=True)
class Grouping(Expr):
    expression: Expr

    @override
    def accept[T](self, visitor: "VisitorExpr[T]") -> T:
        return visitor.visit_grouping_expr(self)


@dataclass(frozen=True)
class Literal(Expr):
    value: object

    @override
    def accept[T](self, visitor: "VisitorExpr[T]") -> T:
        return visitor.visit_literal_expr(self)


@dataclass(frozen=True)
class Unary(Expr):
    operator: Token
    right: Expr

    @override
    def accept[T](self, visitor: "VisitorExpr[T]") -> T:
        return visitor.visit_unary_expr(self)


class VisitorExpr[T](ABC):
    @abstractmethod
    def visit_binary_expr(self, expr: Binary) -> T: ...
    @abstractmethod
    def visit_grouping_expr(self, expr: Grouping) -> T: ...
    @abstractmethod
    def visit_literal_expr(self, expr: Literal) -> T: ...
    @abstractmethod
    def visit_unary_expr(self, expr: Unary) -> T: ...


class Stmt(ABC):
    @abstractmethod
    def accept[T](self, visitor: "VisitorStmt[T]") -> T: ...


@dataclass(frozen=True)
class Expression(Stmt):
    expression: Expr

    @override
    def accept[T](self, visitor: "VisitorStmt[T]") -> T:
        return visitor.visit_expression_stmt(self)


@dataclass(frozen=True)
class Print(Stmt):
    expression: Expr

    @override
    def accept[T](self, visitor: "VisitorStmt[T]") -> T:
        return visitor.visit_print_stmt(self)


class VisitorStmt[T](ABC):
    @abstractmethod
    def visit_expression_stmt(self, expr: Expression) -> T: ...
    @abstractmethod
    def visit_print_stmt(self, expr: Print) -> T: ...
