import pytest

from lox.main import parse_arguments


def test_parse_arguments_script() -> None:
    parse_arguments(["/tmp/script.lox"])


def test_parse_arguments_prompt() -> None:
    parse_arguments([])


def test_parse_arguments_reject() -> None:
    with pytest.raises(SystemExit):
        parse_arguments(["/tmp/script.lox", "/tmp/script.lox"])
