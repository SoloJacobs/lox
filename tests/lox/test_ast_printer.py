from lox.ast import Binary, Grouping, Literal, Unary
from lox.ast_printer import AstPrinter
from lox.scanner import Token, TokenType


def test_ast_printer() -> None:
    expression = Binary(
        Unary(Token(TokenType.MINUS, "-", None, 1), Literal(123)),
        Token(TokenType.STAR, "*", None, 1),
        Grouping(Literal(45.67)),
    )

    assert AstPrinter().print(expression) == "(* (- 123) (group 45.67))"
