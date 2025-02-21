from abc import ABC, abstractmethod
from collections.abc import Sequence
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
class Call(Expr):
    callee: Expr
    paren: Token
    arguments: Sequence[Expr]

    @override
    def accept[T](self, visitor: "VisitorExpr[T]") -> T:
        return visitor.visit_call_expr(self)


@dataclass(frozen=True)
class Assign(Expr):
    name: Token
    value: Expr

    @override
    def accept[T](self, visitor: "VisitorExpr[T]") -> T:
        return visitor.visit_assign_expr(self)


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
class Logical(Expr):
    left: Expr
    operator: Token
    right: Expr

    @override
    def accept[T](self, visitor: "VisitorExpr[T]") -> T:
        return visitor.visit_logical_expr(self)


@dataclass(frozen=True)
class Unary(Expr):
    operator: Token
    right: Expr

    @override
    def accept[T](self, visitor: "VisitorExpr[T]") -> T:
        return visitor.visit_unary_expr(self)


@dataclass(frozen=True)
class Variable(Expr):
    name: Token

    @override
    def accept[T](self, visitor: "VisitorExpr[T]") -> T:
        return visitor.visit_variable_expr(self)


class VisitorExpr[T](ABC):
    @abstractmethod
    def visit_binary_expr(self, expr: Binary) -> T: ...
    @abstractmethod
    def visit_call_expr(self, expr: Call) -> T: ...
    @abstractmethod
    def visit_assign_expr(self, expr: Assign) -> T: ...
    @abstractmethod
    def visit_grouping_expr(self, expr: Grouping) -> T: ...
    @abstractmethod
    def visit_literal_expr(self, expr: Literal) -> T: ...
    @abstractmethod
    def visit_logical_expr(self, expr: Logical) -> T: ...
    @abstractmethod
    def visit_unary_expr(self, expr: Unary) -> T: ...
    @abstractmethod
    def visit_variable_expr(self, expr: Variable) -> T: ...


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
class If(Stmt):
    condition: Expr
    then_branch: Stmt
    else_branch: Stmt | None

    @override
    def accept[T](self, visitor: "VisitorStmt[T]") -> T:
        return visitor.visit_if_stmt(self)


@dataclass(frozen=True)
class While(Stmt):
    condition: Expr
    body: Stmt

    @override
    def accept[T](self, visitor: "VisitorStmt[T]") -> T:
        return visitor.visit_while_stmt(self)


@dataclass(frozen=True)
class Block(Stmt):
    statements: Sequence[Stmt]

    @override
    def accept[T](self, visitor: "VisitorStmt[T]") -> T:
        return visitor.visit_block_stmt(self)


@dataclass(frozen=True)
class Print(Stmt):
    expression: Expr

    @override
    def accept[T](self, visitor: "VisitorStmt[T]") -> T:
        return visitor.visit_print_stmt(self)


@dataclass(frozen=True)
class Var(Stmt):
    name: Token
    initializer: Expr

    @override
    def accept[T](self, visitor: "VisitorStmt[T]") -> T:
        return visitor.visit_var_stmt(self)


class VisitorStmt[T](ABC):
    @abstractmethod
    def visit_expression_stmt(self, expr: Expression) -> T: ...
    @abstractmethod
    def visit_if_stmt(self, expr: If) -> T: ...
    @abstractmethod
    def visit_while_stmt(self, expr: While) -> T: ...
    @abstractmethod
    def visit_block_stmt(self, expr: Block) -> T: ...
    @abstractmethod
    def visit_print_stmt(self, expr: Print) -> T: ...
    @abstractmethod
    def visit_var_stmt(self, expr: Var) -> T: ...
