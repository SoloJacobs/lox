from lox.interpret import Interpreter
from lox.parser import Parser
from lox.scanner import Scanner
from tests.lox.utils import Reporter


def test_parse_comma_expr() -> None:
    # Assemble
    lox = "1-1,2,1*3"
    reporter = Reporter()
    tokens = Scanner(reporter, lox).scan_tokens()
    print(tokens)
    assert not reporter.errors
    parser = Parser(reporter, tokens)
    expr = parser.expression()
    interpreter = Interpreter()
    assert not reporter.parser_errors
    # Act
    value = expr.accept(interpreter)
    # Assert
    assert value == 3.0
