from challenges.chapter_5_exercise_3 import RPN
from lox.ast import Binary, Grouping, Literal, Unary
from lox.scanner import Token, TokenType


def test_rpn_example_one() -> None:
    expression = Binary(
        Unary(Token(TokenType.MINUS, "-", None, 1), Literal(123)),
        Token(TokenType.STAR, "*", None, 1),
        Grouping(Literal(45.67)),
    )

    assert RPN().rpn(expression) == "123 - 45.67 *"


def test_rpn_example_two() -> None:
    expression = Binary(
        Grouping(
            Binary(
                Literal(1),
                Token(TokenType.PLUS, "+", None, 1),
                Literal(2),
            ),
        ),
        Token(TokenType.STAR, "*", None, 1),
        Grouping(
            Binary(
                Literal(3),
                Token(TokenType.MINUS, "-", None, 1),
                Literal(4),
            ),
        ),
    )

    assert RPN().rpn(expression) == "1 2 + 3 4 - *"
